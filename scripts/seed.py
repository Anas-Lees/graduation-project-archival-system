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
    {"email": "student@aou.edu.kw",  "name": "Salman Dawara",   "role": "student",  "password": "Student123!"},
    {"email": "faculty@aou.edu.kw",  "name": "Dr. Aws Abu Eid", "role": "faculty",  "password": "Faculty123!"},
    {"email": "admin@aou.edu.kw",    "name": "GPAS Admin",      "role": "admin",    "password": "Admin123!"},
    {"email": "sysadmin@aou.edu.kw", "name": "System Admin",    "role": "sysadmin", "password": "SysAdmin123!"},
]

CATEGORIES = [
    ("Software Engineering",  "هندسة البرمجيات"),
    ("Web Development",       "تطوير الويب"),
    ("AI / Machine Learning", "الذكاء الاصطناعي والتعلم الآلي"),
    ("Networks",              "الشبكات"),
    ("Mobile Apps",           "تطبيقات الجوال"),
    ("Databases",             "قواعد البيانات"),
    ("Cybersecurity",         "الأمن السيبراني"),
]

DEPARTMENTS = ["Information Technology and Computing", "Computer Science", "Information Systems"]


PROJECTS = [
    {
        "title": "Accessible E-Learning Platform for Visually Impaired Students",
        "abstract": "An accessible web-based learning management system that conforms to WCAG 2.1 Level AA, "
                    "supports screen readers, and provides keyboard-only navigation. The platform allows "
                    "instructors to author lessons that are automatically narrated and includes adaptive "
                    "color-contrast themes for low-vision users.",
        "keywords": "accessibility, e-learning, WCAG, screen reader, education",
        "year": 2024, "department": DEPARTMENTS[0], "status": "approved",
        "categories": ["Web Development", "Software Engineering"],
    },
    {
        "title": "AI-Powered Plagiarism Detection in Arabic Academic Texts",
        "abstract": "A natural-language-processing system that detects plagiarism in Arabic dissertations and "
                    "graduation projects using transformer-based embeddings. The system normalizes Arabic "
                    "diacritics, handles dialectal variation, and reports cross-document similarity scores.",
        "keywords": "NLP, Arabic, plagiarism, AI, transformers",
        "year": 2024, "department": DEPARTMENTS[1], "status": "approved",
        "categories": ["AI / Machine Learning", "Software Engineering"],
    },
    {
        "title": "Smart Campus IoT Monitoring System",
        "abstract": "An Internet-of-Things dashboard for monitoring temperature, humidity, occupancy, and "
                    "energy consumption across the AOU Kuwait campus. Uses MQTT, ESP32 sensors, and a "
                    "Node-RED backend with a real-time React dashboard.",
        "keywords": "IoT, MQTT, sensors, dashboard, smart campus",
        "year": 2023, "department": DEPARTMENTS[1], "status": "approved",
        "categories": ["Networks", "Web Development"],
    },
    {
        "title": "Secure Online Voting System Using Blockchain",
        "abstract": "A proof-of-concept voting platform that records ballots on a permissioned Ethereum chain "
                    "to provide immutability and public auditability while preserving voter anonymity through "
                    "zero-knowledge proofs.",
        "keywords": "blockchain, voting, security, zero-knowledge, ethereum",
        "year": 2023, "department": DEPARTMENTS[2], "status": "approved",
        "categories": ["Cybersecurity", "Web Development"],
    },
    {
        "title": "Bilingual Mobile Library Catalog Application",
        "abstract": "A cross-platform mobile application for searching and reserving library books in both "
                    "Arabic and English. Built with Flutter, it supports right-to-left layout, offline "
                    "caching, and barcode scanning for quick check-out.",
        "keywords": "mobile, flutter, RTL, Arabic, library",
        "year": 2023, "department": DEPARTMENTS[0], "status": "approved",
        "categories": ["Mobile Apps", "Databases"],
    },
    {
        "title": "Data Warehouse for Student Performance Analytics",
        "abstract": "An ETL pipeline and star-schema warehouse that consolidates student grades, attendance, "
                    "and engagement metrics across courses. Power BI dashboards expose at-risk-student "
                    "indicators and support early-intervention workflows for advisors.",
        "keywords": "data warehouse, ETL, analytics, education, BI",
        "year": 2022, "department": DEPARTMENTS[2], "status": "approved",
        "categories": ["Databases", "AI / Machine Learning"],
    },
    {
        "title": "Phishing-URL Detection Using Lightweight Machine Learning",
        "abstract": "A browser extension that flags phishing URLs in real time using a logistic-regression "
                    "classifier trained on lexical and host-based features. The classifier runs entirely "
                    "client-side, requiring no external API calls and preserving user privacy.",
        "keywords": "phishing, machine learning, browser extension, security",
        "year": 2022, "department": DEPARTMENTS[1], "status": "approved",
        "categories": ["Cybersecurity", "AI / Machine Learning"],
    },
    {
        "title": "RESTful API for Multi-Tenant SaaS Inventory System",
        "abstract": "A scalable inventory-management API designed for small-to-medium businesses. Implements "
                    "per-tenant data isolation, OAuth 2.0 authentication, role-based access control, and "
                    "webhook notifications for stock changes.",
        "keywords": "REST, API, SaaS, multi-tenant, OAuth",
        "year": 2021, "department": DEPARTMENTS[0], "status": "approved",
        "categories": ["Software Engineering", "Web Development"],
    },
    # Pending submissions (so admin queue isn't empty for the demo)
    {
        "title": "Augmented Reality Campus Navigation",
        "abstract": "An AR mobile app that overlays directional arrows on the camera feed to guide students "
                    "to classrooms, offices, and facilities across the AOU Kuwait campus. Integrates with "
                    "the existing campus map service for indoor positioning.",
        "keywords": "AR, navigation, mobile, indoor positioning",
        "year": 2025, "department": DEPARTMENTS[0], "status": "pending",
        "categories": ["Mobile Apps"],
    },
    {
        "title": "Voice-Controlled Smart Home Hub for Arabic Speakers",
        "abstract": "An open-source smart-home automation hub with native Arabic voice recognition. Supports "
                    "Modern Standard Arabic and Gulf dialect commands for controlling lights, climate, and "
                    "media playback through Zigbee and Z-Wave devices.",
        "keywords": "smart home, voice, Arabic, IoT, Zigbee",
        "year": 2025, "department": DEPARTMENTS[1], "status": "pending",
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


def upsert_projects(app):
    faculty = db.session.query(User).filter_by(email="faculty@aou.edu.kw").one()
    admin = db.session.query(User).filter_by(email="admin@aou.edu.kw").one()
    cat_by_name = {c.name_en: c for c in db.session.query(Category).all()}
    upload_folder = app.config["UPLOAD_FOLDER"]
    created = 0

    for i, p in enumerate(PROJECTS):
        if db.session.query(Project).filter_by(title=p["title"]).first():
            continue

        project = Project(
            title=p["title"], abstract=p["abstract"], keywords=p["keywords"],
            year=p["year"], department=p["department"], status=p["status"],
            uploader_id=faculty.id,
            created_at=datetime.utcnow() - timedelta(days=180 - i * 14),
        )
        if p["status"] == "approved":
            project.approver_id = admin.id
            project.approved_at = project.created_at + timedelta(days=2)
        project.categories = [cat_by_name[name] for name in p["categories"] if name in cat_by_name]

        slug = "".join(ch if ch.isalnum() else "_" for ch in p["title"].lower())[:40].strip("_")
        unique = f"seed_{slug}_{uuid.uuid4().hex[:8]}.pdf"
        stored = write_pdf(unique, upload_folder)
        original = f"{slug}.pdf"

        db.session.add(project)
        db.session.flush()
        db.session.add(ProjectFile(
            project_id=project.id, filename=original, stored_path=stored,
            mimetype="application/pdf", size=os.path.getsize(stored),
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
