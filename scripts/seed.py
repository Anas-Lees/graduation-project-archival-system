"""Seed GPAS with demo users, categories, and ~10 sample projects with placeholder PDFs.

Idempotent: safe to re-run; existing rows are skipped.
"""
import os
import sys
import uuid
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models import User, Category, Project, ProjectFile, install_fts
from app.utils.security import hash_password


# Minimal valid PDF (a single blank page). ~600 bytes.
MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 595 842]/Resources<</Font<</F1 5 0 R>>>>/Contents 4 0 R>>endobj\n"
    b"4 0 obj<</Length 62>>stream\nBT /F1 18 Tf 60 760 Td (GPAS placeholder PDF) Tj ET\nendstream\nendobj\n"
    b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
    b"xref\n0 6\n"
    b"0000000000 65535 f \n"
    b"0000000010 00000 n \n"
    b"0000000053 00000 n \n"
    b"0000000098 00000 n \n"
    b"0000000196 00000 n \n"
    b"0000000305 00000 n \n"
    b"trailer<</Size 6/Root 1 0 R>>\nstartxref\n372\n%%EOF\n"
)


USERS = [
    {"email": "student@aou.edu.kw", "name": "Salman Dawara",   "role": "student", "password": "Student123!"},
    {"email": "faculty@aou.edu.kw", "name": "Dr. Aws Abu Eid", "role": "faculty", "password": "Faculty123!"},
]

CATEGORIES = [
    ("Software Engineering",  "هندسة البرمجيات"),
    ("Web Development",       "تطوير الويب"),
    ("AI / Machine Learning", "الذكاء الاصطناعي والتعلم الآلي"),
    ("Networks",              "الشبكات"),
    ("Mobile Apps",           "تطبيقات الجوال"),
    ("Databases",             "قواعد البيانات"),
    ("Cybersecurity",         "الأمن السيبراني"),
    ("Other",                 "أخرى"),
]

# Single department (the system isn't faculty-specific anymore)
DEPARTMENT = "Information Technology"


PROJECTS = [
    # Approved — varied years 2018-2025 to populate the year filter
    {
        "title": "Accessible E-Learning Platform for Visually Impaired Students",
        "abstract": "An accessible web-based learning management system that conforms to WCAG 2.1 Level AA, "
                    "supports screen readers, and provides keyboard-only navigation. The platform allows "
                    "instructors to author lessons that are automatically narrated and includes adaptive "
                    "color-contrast themes for low-vision users.",
        "keywords": "accessibility, e-learning, WCAG, screen reader, education",
        "year": 2025, "status": "approved",
        "categories": ["Web Development", "Software Engineering"],
        "github": "https://github.com/aou-kuwait/accessible-elearning",
        "slides": True,
    },
    {
        "title": "AI-Powered Plagiarism Detection in Arabic Academic Texts",
        "abstract": "A natural-language-processing system that detects plagiarism in Arabic dissertations and "
                    "graduation projects using transformer-based embeddings. The system normalizes Arabic "
                    "diacritics, handles dialectal variation, and reports cross-document similarity scores.",
        "keywords": "NLP, Arabic, plagiarism, AI, transformers",
        "year": 2024, "status": "approved",
        "categories": ["AI / Machine Learning", "Software Engineering"],
        "github": "https://github.com/aou-kuwait/arabic-plagiarism",
        "slides": True,
    },
    {
        "title": "Smart Campus IoT Monitoring System",
        "abstract": "An Internet-of-Things dashboard for monitoring temperature, humidity, occupancy, and "
                    "energy consumption across the AOU Kuwait campus. Uses MQTT, ESP32 sensors, and a "
                    "Node-RED backend with a real-time React dashboard.",
        "keywords": "IoT, MQTT, sensors, dashboard, smart campus",
        "year": 2024, "status": "approved",
        "categories": ["Networks", "Web Development"],
        "github": "https://github.com/aou-kuwait/smart-campus-iot",
        "slides": True,
    },
    {
        "title": "Secure Online Voting System Using Blockchain",
        "abstract": "A proof-of-concept voting platform that records ballots on a permissioned Ethereum chain "
                    "to provide immutability and public auditability while preserving voter anonymity through "
                    "zero-knowledge proofs.",
        "keywords": "blockchain, voting, security, zero-knowledge, ethereum",
        "year": 2023, "status": "approved",
        "categories": ["Cybersecurity", "Web Development"],
        "github": "https://github.com/aou-kuwait/blockchain-voting",
        "slides": True,
    },
    {
        "title": "Bilingual Mobile Library Catalog Application",
        "abstract": "A cross-platform mobile application for searching and reserving library books in both "
                    "Arabic and English. Built with Flutter, it supports right-to-left layout, offline "
                    "caching, and barcode scanning for quick check-out.",
        "keywords": "mobile, flutter, RTL, Arabic, library",
        "year": 2023, "status": "approved",
        "categories": ["Mobile Apps", "Databases"],
        "github": "https://github.com/aou-kuwait/bilingual-library",
        "slides": True,
    },
    {
        "title": "Data Warehouse for Student Performance Analytics",
        "abstract": "An ETL pipeline and star-schema warehouse that consolidates student grades, attendance, "
                    "and engagement metrics across courses. Power BI dashboards expose at-risk-student "
                    "indicators and support early-intervention workflows for advisors.",
        "keywords": "data warehouse, ETL, analytics, education, BI",
        "year": 2022, "status": "approved",
        "categories": ["Databases", "AI / Machine Learning"],
        "github": "https://github.com/aou-kuwait/student-analytics-dwh",
        "slides": True,
    },
    {
        "title": "Phishing-URL Detection Using Lightweight Machine Learning",
        "abstract": "A browser extension that flags phishing URLs in real time using a logistic-regression "
                    "classifier trained on lexical and host-based features. The classifier runs entirely "
                    "client-side, requiring no external API calls and preserving user privacy.",
        "keywords": "phishing, machine learning, browser extension, security",
        "year": 2022, "status": "approved",
        "categories": ["Cybersecurity", "AI / Machine Learning"],
        "github": "https://github.com/aou-kuwait/phishing-detector",
        "slides": False,
    },
    {
        "title": "RESTful API for Multi-Tenant SaaS Inventory System",
        "abstract": "A scalable inventory-management API designed for small-to-medium businesses. Implements "
                    "per-tenant data isolation, OAuth 2.0 authentication, role-based access control, and "
                    "webhook notifications for stock changes.",
        "keywords": "REST, API, SaaS, multi-tenant, OAuth",
        "year": 2021, "status": "approved",
        "categories": ["Software Engineering", "Web Development"],
        "github": "https://github.com/aou-kuwait/multi-tenant-inventory-api",
        "slides": False,
    },
    {
        "title": "Real-Time Hospital Bed-Allocation Dashboard",
        "abstract": "A web dashboard that aggregates bed-occupancy data across hospital wards and visualises "
                    "live availability. Originally a third-year project — extended for graduation with "
                    "predictive analytics that forecast peak demand based on admissions history.",
        "keywords": "hospital, dashboard, healthcare, real-time, analytics",
        "year": 2020, "status": "approved",
        "categories": ["Web Development", "Databases", "Other"],
        "github": "https://github.com/aou-kuwait/hospital-beds",
        "slides": False,
    },
    {
        "title": "Quranic Recitation Training App with Tajweed Feedback",
        "abstract": "A mobile application that records a user's recitation, compares it against a reference "
                    "qari, and gives real-time tajweed feedback using DSP and a small acoustic-model classifier "
                    "trained on labelled samples. Cross-discipline project blending audio engineering and ML.",
        "keywords": "Quran, audio, mobile, classifier, tajweed",
        "year": 2019, "status": "approved",
        "categories": ["Mobile Apps", "AI / Machine Learning", "Other"],
        "github": "https://github.com/aou-kuwait/tajweed-coach",
        "slides": True,
    },
    {
        "title": "Course-Selection Recommender for Distance-Learning Students",
        "abstract": "A collaborative-filtering recommender that suggests electives to AOU students based on "
                    "the patterns of past graduates with similar majors and grade profiles. Built as one of "
                    "the very first GPAS archive submissions.",
        "keywords": "recommender, collaborative filtering, education, AOU",
        "year": 2018, "status": "approved",
        "categories": ["AI / Machine Learning", "Databases"],
        "github": "https://github.com/aou-kuwait/course-recommender",
        "slides": False,
    },
    # Pending submissions (so admin queue isn't empty for the demo)
    {
        "title": "Augmented Reality Campus Navigation",
        "abstract": "An AR mobile app that overlays directional arrows on the camera feed to guide students "
                    "to classrooms, offices, and facilities across the AOU Kuwait campus. Integrates with "
                    "the existing campus map service for indoor positioning.",
        "keywords": "AR, navigation, mobile, indoor positioning",
        "year": 2025, "status": "pending",
        "categories": ["Mobile Apps"],
    },
    {
        "title": "Voice-Controlled Smart Home Hub for Arabic Speakers",
        "abstract": "An open-source smart-home automation hub with native Arabic voice recognition. Supports "
                    "Modern Standard Arabic and Gulf dialect commands for controlling lights, climate, and "
                    "media playback through Zigbee and Z-Wave devices.",
        "keywords": "smart home, voice, Arabic, IoT, Zigbee",
        "year": 2025, "status": "pending",
        "categories": ["AI / Machine Learning", "Networks"],
    },
]


def upsert_users():
    created = 0
    for u in USERS:
        if db.session.query(User).filter_by(email=u["email"]).first():
            continue
        db.session.add(User(
            email=u["email"], full_name=u["name"], role=u["role"],
            password_hash=hash_password(u["password"]),
            email_verified=True, language="en",
        ))
        created += 1
    db.session.commit()
    return created


def upsert_categories():
    created = 0
    for en, ar in CATEGORIES:
        if db.session.query(Category).filter_by(name_en=en).first():
            continue
        db.session.add(Category(name_en=en, name_ar=ar))
        created += 1
    db.session.commit()
    return created


def write_pdf(filename: str, upload_folder: str) -> str:
    os.makedirs(upload_folder, exist_ok=True)
    path = os.path.join(upload_folder, filename)
    with open(path, "wb") as fh:
        fh.write(MINIMAL_PDF)
    return path


def write_thumbnail(title: str, project_id: int, upload_folder: str) -> str:
    """Generate a small SVG cover for a project. Stored under uploads/thumbs/.
    Returns path relative to app/static/ (so url_for('static', filename=...) works).
    """
    folder = os.path.join(upload_folder, "thumbs")
    os.makedirs(folder, exist_ok=True)
    hue = (project_id * 137) % 360
    initial = (title or "?")[0].upper()
    title_short = (title[:26] + "…") if len(title) > 26 else title
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 450' role='img' aria-label='{title}'>
  <defs>
    <linearGradient id='g' x1='0' x2='1' y1='0' y2='1'>
      <stop offset='0' stop-color='hsl({hue},75%,55%)'/>
      <stop offset='1' stop-color='hsl({(hue + 60) % 360},75%,50%)'/>
    </linearGradient>
    <radialGradient id='p' cx='30%' cy='30%' r='60%'>
      <stop offset='0' stop-color='rgba(255,255,255,.25)'/>
      <stop offset='1' stop-color='rgba(255,255,255,0)'/>
    </radialGradient>
  </defs>
  <rect width='800' height='450' fill='url(#g)'/>
  <rect width='800' height='450' fill='url(#p)'/>
  <circle cx='670' cy='110' r='130' fill='rgba(255,255,255,.10)'/>
  <circle cx='110' cy='370' r='90'  fill='rgba(255,255,255,.08)'/>
  <text x='60' y='250' font-family='Inter,Tajawal,sans-serif' font-size='160' font-weight='800' fill='rgba(255,255,255,.95)'>{initial}</text>
  <text x='60' y='340' font-family='Inter,Tajawal,sans-serif' font-size='26' font-weight='600' fill='rgba(255,255,255,.85)'>{title_short.replace('&', '&amp;').replace('<', '&lt;')}</text>
</svg>"""
    filename = f"seed_thumb_{project_id}_{uuid.uuid4().hex[:8]}.svg"
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(svg)
    return f"uploads/thumbs/{filename}"


def upsert_projects(app):
    student = db.session.query(User).filter_by(email="student@aou.edu.kw").one()
    faculty = db.session.query(User).filter_by(email="faculty@aou.edu.kw").one()
    cat_by_name = {c.name_en: c for c in db.session.query(Category).all()}
    upload_folder = app.config["UPLOAD_FOLDER"]
    created = 0

    for i, p in enumerate(PROJECTS):
        if db.session.query(Project).filter_by(title=p["title"]).first():
            continue

        project = Project(
            title=p["title"], abstract=p["abstract"], keywords=p["keywords"],
            year=p["year"], department=DEPARTMENT, status=p["status"],
            github_url=p.get("github"),
            uploader_id=student.id,
            created_at=datetime.utcnow() - timedelta(days=180 - i * 14),
        )
        if p["status"] == "approved":
            project.approver_id = faculty.id
            project.approved_at = project.created_at + timedelta(days=2)
        project.categories = [cat_by_name[name] for name in p["categories"] if name in cat_by_name]

        slug = "".join(ch if ch.isalnum() else "_" for ch in p["title"].lower())[:40].strip("_")

        db.session.add(project)
        db.session.flush()

        # Thumbnail
        project.thumbnail_path = write_thumbnail(p["title"], project.id, upload_folder)

        # Main document
        doc_unique = f"seed_{slug}_{uuid.uuid4().hex[:8]}.pdf"
        doc_stored = write_pdf(doc_unique, upload_folder)
        db.session.add(ProjectFile(
            project_id=project.id, filename=f"{slug}.pdf", stored_path=doc_stored,
            mimetype="application/pdf", size=os.path.getsize(doc_stored), kind="document",
        ))

        # Optional slides
        if p.get("slides"):
            sl_unique = f"seed_{slug}_slides_{uuid.uuid4().hex[:8]}.pdf"
            sl_stored = write_pdf(sl_unique, upload_folder)
            db.session.add(ProjectFile(
                project_id=project.id, filename=f"{slug}_slides.pdf", stored_path=sl_stored,
                mimetype="application/pdf", size=os.path.getsize(sl_stored), kind="slides",
            ))

        created += 1

    db.session.commit()
    return created


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        with db.engine.begin() as conn:
            install_fts(conn)

        u = upsert_users()
        c = upsert_categories()
        p = upsert_projects(app)
        print(f"Seeded: users +{u}, categories +{c}, projects +{p}")
        print()
        print("Login credentials:")
        print(f"  {'Role':<10} {'Email':<28} Password")
        print(f"  {'-'*10} {'-'*28} {'-'*14}")
        for usr in USERS:
            print(f"  {usr['role']:<10} {usr['email']:<28} {usr['password']}")


if __name__ == "__main__":
    main()
