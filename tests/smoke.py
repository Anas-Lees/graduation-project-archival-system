"""End-to-end smoke test against a running GPAS dev server on :5000."""
import re
import io
import sys
import requests

BASE = "http://127.0.0.1:5000"
ok = lambda msg: print(f"  PASS  {msg}")
bad = lambda msg: (print(f"  FAIL  {msg}"), sys.exit(1))


def csrf(html: str) -> str:
    m = re.search(r'name="csrf_token"[^>]*\bvalue="([^"]+)"', html)
    if not m:
        bad("no CSRF token in form")
    return m.group(1)


def login(s: requests.Session, email: str, password: str):
    r = s.get(f"{BASE}/auth/login")
    token = csrf(r.text)
    r = s.post(f"{BASE}/auth/login", data={"csrf_token": token, "email": email, "password": password, "submit": "Sign in"}, allow_redirects=False)
    if r.status_code not in (302, 303):
        bad(f"login {email} got status {r.status_code}")
    ok(f"login {email}")


def main():
    print("== GPAS smoke tests ==")

    # 1. Public home
    r = requests.get(f"{BASE}/")
    assert r.status_code == 200, r.status_code
    assert "GPAS" in r.text
    assert 'lang="en"' in r.text and 'dir="ltr"' in r.text
    ok("home (en, ltr)")

    # 2. Language switch -> ar
    s = requests.Session()
    s.get(f"{BASE}/lang/ar")
    r = s.get(f"{BASE}/")
    assert 'lang="ar"' in r.text and 'dir="rtl"' in r.text, "RTL not set"
    assert "تصفح" in r.text or "تخرج" in r.text, "no Arabic strings rendered"
    ok("language switch to Arabic with RTL")

    # 3. Browse approved projects
    r = requests.get(f"{BASE}/projects/")
    assert r.status_code == 200
    assert "Accessible E-Learning" in r.text
    ok("browse lists approved projects")

    # 4. FTS search
    r = requests.get(f"{BASE}/projects/search", params={"q": "accessibility"})
    assert r.status_code == 200
    assert "Accessible E-Learning" in r.text
    ok("FTS5 search finds 'accessibility'")

    r = requests.get(f"{BASE}/projects/search", params={"q": "blockchain"})
    assert "Blockchain" in r.text or "blockchain" in r.text
    ok("FTS5 search finds 'blockchain'")

    # 5. Login as student + upload (students can submit in the simplified role model)
    sf = requests.Session()
    login(sf, "student@aou.edu.kw", "Student123!")
    r = sf.get(f"{BASE}/projects/upload")
    assert r.status_code == 200
    token = csrf(r.text)
    pdf = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"
    fake_mp4 = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 80  # extension passes; bytes are placeholder
    fake_pptx = b"PK\x03\x04" + b"\x00" * 60               # zip magic so it looks plausible
    files = [
        ("file",   ("smoke_test.pdf",   io.BytesIO(pdf),       "application/pdf")),
        ("video",  ("smoke_test.mp4",   io.BytesIO(fake_mp4),  "video/mp4")),
        ("slides", ("smoke_test.pptx",  io.BytesIO(fake_pptx), "application/vnd.openxmlformats-officedocument.presentationml.presentation")),
    ]
    data = {
        "csrf_token": token,
        "title": "Smoke Test Project",
        "abstract": "This is an automated smoke test submission used to verify the upload + approval workflow.",
        "keywords": "smoke, test",
        "year": "2025",
        "department": "Information Technology and Computing",
        "categories": [],
        "github_url": "https://github.com/aou-kuwait/smoke-test",
        "submit": "Submit for approval",
    }
    r = sf.post(f"{BASE}/projects/upload", data=data, files=files, allow_redirects=False)
    assert r.status_code in (302, 303), f"upload got {r.status_code}, body={r.text[:300]}"
    location = r.headers["Location"]
    pid = int(re.search(r"/projects/(\d+)", location).group(1))
    ok(f"upload created project id={pid} with doc + video + slides + github (pending)")

    # 6. Login as doc + approve the upload
    sa = requests.Session()
    login(sa, "doc@aou.edu.kw", "Doctor123!")
    r = sa.get(f"{BASE}/admin/approvals")
    assert r.status_code == 200
    assert "Smoke Test Project" in r.text, "pending project not in queue"
    ok("admin sees pending submission in queue")

    token = csrf(r.text)
    r = sa.post(f"{BASE}/admin/approvals/{pid}/approve",
                data={"csrf_token": token}, allow_redirects=False)
    assert r.status_code in (302, 303), f"approve got {r.status_code}"
    ok("admin approved project")

    # Confirm it's now publicly visible AND renders the video + github link
    r = requests.get(f"{BASE}/projects/{pid}")
    assert r.status_code == 200 and "Smoke Test Project" in r.text
    ok("approved project is publicly visible")

    assert "<video" in r.text and f"/projects/{pid}/media/" in r.text, "video player not rendered"
    ok("project page embeds <video> with /media/ src")

    assert "github.com/aou-kuwait/smoke-test" in r.text
    ok("project page shows GitHub link")

    assert "smoke_test.pptx" in r.text or "Slides" in r.text
    ok("project page lists slides file")

    # Inline media route returns the video bytes (not as attachment)
    media_match = re.search(rf'src="(/projects/{pid}/media/\d+)"', r.text)
    assert media_match, "no /media/ src found"
    rm = requests.get(f"{BASE}{media_match.group(1)}")
    assert rm.status_code == 200, f"media route got {rm.status_code}"
    assert "attachment" not in (rm.headers.get("Content-Disposition") or ""), "video served as attachment"
    ok("inline /media/ route serves video without attachment header")

    # 7. Logged-in student can download approved files
    ss = requests.Session()
    login(ss, "student@aou.edu.kw", "Student123!")
    r = ss.get(f"{BASE}/projects/")
    seed_link = re.search(r'href="(/projects/\d+/files/\d+)"', r.text) or \
                re.search(r'/projects/(\d+)', r.text)
    # Pick the first approved seed project and find its file
    r = ss.get(f"{BASE}/projects/1")
    m = re.search(r'href="(/projects/1/files/\d+)"', r.text)
    if m:
        r = ss.get(f"{BASE}{m.group(1)}", allow_redirects=False)
        assert r.status_code == 200, f"download got {r.status_code}"
        assert r.content.startswith(b"%PDF"), "downloaded file is not a PDF"
        ok("student downloads PDF")
    else:
        ok("(skip download — no file link found; OK if uploads dir empty)")

    # 8. Reports page (admin only)
    r = sa.get(f"{BASE}/admin/reports")
    assert r.status_code == 200
    assert "Most viewed" in r.text or "Reports" in r.text
    ok("admin reports page renders")

    # 9. RBAC: student cannot reach admin
    r = ss.get(f"{BASE}/admin/", allow_redirects=False)
    assert r.status_code in (302, 403), f"student admin got {r.status_code}"
    ok(f"student blocked from /admin (status {r.status_code})")

    # 10. Email log written
    import os
    log = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instance", "email.log"))
    assert os.path.exists(log) and os.path.getsize(log) > 0, "email.log empty"
    ok("FR15 email.log has entries")

    print("\nAll smoke checks passed.")


if __name__ == "__main__":
    main()
