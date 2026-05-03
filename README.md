# GPAS — Graduation Project Archival System

A web-based digital repository for AOU Kuwait graduation projects.
Implements the TM471 Part A specification: bilingual (English/Arabic) interface with RTL support, WCAG 2.1 AA accessibility, role-based access control, full-text search, and an admin approval workflow.

**Stack:** Python 3.11 · Flask 3 · SQLAlchemy · SQLite (with FTS5) · Bootstrap 5 · Flask-Babel.

---

## Quick start (Windows)

```cmd
cd E:\salman\gpas
venv\Scripts\activate
pip install -r requirements.txt
python scripts\init_db.py
python scripts\seed.py
python run.py
```

Open http://127.0.0.1:5000

For a production-style server use waitress:
```cmd
venv\Scripts\waitress-serve --listen=127.0.0.1:8000 run:app
```

---

## Demo accounts (seeded)

| Role      | Email                     | Password       |
|-----------|---------------------------|----------------|
| Student   | student@aou.edu.kw        | Student123!    |
| Faculty   | faculty@aou.edu.kw        | Faculty123!    |
| Admin     | admin@aou.edu.kw          | Admin123!      |
| SysAdmin  | sysadmin@aou.edu.kw       | SysAdmin123!   |

Faculty can upload; Admin can approve/reject/manage users and view reports.

---

## Functional requirement coverage

| #     | Requirement                                 | Implementation |
|-------|---------------------------------------------|----------------|
| FR01  | Register with email verification            | `/auth/register` + token link logged to `instance/email.log` |
| FR02  | Login by email/password                     | `/auth/login` (bcrypt-verified) |
| FR03  | Role-based access (student/faculty/admin/sysadmin) | `app/utils/security.py` `@role_required` |
| FR04  | Faculty upload PDF/DOCX                     | `/projects/upload` (50 MB max) |
| FR05  | Browse by year / department / category      | `/projects/` with filter UI |
| FR06  | Full-text search                            | `/projects/search` via SQLite FTS5 with rank ordering |
| FR07  | Detailed project view                       | `/projects/<id>` shows abstract, authors, files |
| FR08  | Authorized download                         | `/projects/<id>/files/<fid>` (login-required) |
| FR09  | Approval workflow                           | `/admin/approvals` queue + approve/reject |
| FR10  | Admin manages user accounts                 | `/admin/users` create / edit / delete |
| FR11  | Usage reports                               | `/admin/reports` (top viewed/downloaded, by year/dept) |
| FR12  | Bilingual EN/AR                             | Flask-Babel; switcher in navbar; `/lang/<code>` |
| FR13  | Access log for views and downloads          | `access_log` table written on every view/download |
| FR14  | Filter search results by multiple criteria  | year + department + category filters on browse and search |
| FR15  | Email notifications                         | `app/utils/mailer.py` writes to `instance/email.log` (FR15 stub per design) |

## Non-functional requirement coverage

| #      | Requirement                       | How |
|--------|-----------------------------------|-----|
| NFR01  | Pages load < 3 s                  | SQLite + indexes; FTS5 for search |
| NFR02  | 100 concurrent users              | Use `waitress-serve` (above) for prod |
| NFR03  | bcrypt password hashing           | `passlib` bcrypt at 12 rounds |
| NFR04  | HTTPS                             | Cookies set `HttpOnly` + `SameSite=Lax`; uncomment `SESSION_COOKIE_SECURE` behind a TLS reverse proxy |
| NFR05  | 30-min session timeout            | `PERMANENT_SESSION_LIFETIME = 30min` |
| NFR06  | WCAG 2.1 AA                       | Semantic HTML, skip link, ARIA labels, keyboard navigation, ≥4.5:1 contrast |
| NFR07  | Alt text on images                | All images have alt; cards use semantic structure |
| NFR08  | Keyboard navigable                | Bootstrap focus rings overridden with high-visibility outline |
| NFR09  | Responsive                        | Bootstrap 5 grid |
| NFR10  | RTL for Arabic                    | `<html dir="rtl">` + Bootstrap RTL build |
| NFR11  | 99% uptime                        | Stateless app; SQLite single-file backup trivially scriptable |
| NFR12  | Daily automated backups           | Schedule `copy instance\gpas.db backups\gpas-%date%.db` via Windows Task Scheduler |
| NFR13  | 10 000+ projects                  | SQLite + FTS5 handles this easily |
| NFR14  | Coding standards                  | PEP 8 (Python equivalent of PSR-12) |
| NFR15  | University data-protection policy | RBAC enforced; privacy notice at `/privacy` |

---

## Project layout

```
gpas/
├─ app/
│  ├─ __init__.py            Flask app factory + locale selection
│  ├─ models.py              SQLAlchemy schema + FTS5 triggers
│  ├─ extensions.py          db, login_manager, csrf, babel
│  ├─ forms.py               WTForms with CSRF
│  ├─ errors.py              401/403/404/500 handlers
│  ├─ blueprints/
│  │  ├─ main.py             Home, lang switch, about, privacy
│  │  ├─ auth.py             Register, verify, login, logout
│  │  ├─ projects.py         Browse, search, view, upload, download, "my submissions"
│  │  └─ admin.py            Dashboard, approvals, users, reports
│  ├─ utils/
│  │  ├─ security.py         bcrypt + @role_required
│  │  ├─ files.py            Safe upload storage
│  │  ├─ search.py           FTS5 query builder
│  │  └─ mailer.py           Logs notifications to email.log
│  ├─ templates/             Jinja2 (base + per-blueprint folders)
│  └─ static/
│     ├─ css/app.css         Accessibility-first overrides
│     ├─ js/app.js           Minimal progressive enhancement
│     └─ uploads/            Stored project files
├─ translations/
│  ├─ en/LC_MESSAGES/messages.{po,mo}
│  └─ ar/LC_MESSAGES/messages.{po,mo}
├─ scripts/
│  ├─ init_db.py             Create tables + FTS5 + triggers
│  ├─ seed.py                Demo users, categories, 10 sample projects
│  └─ fill_translations.py   Populates AR translations + compiles .mo
├─ tests/
│  └─ smoke.py               End-to-end smoke test (16 checks)
├─ instance/
│  ├─ gpas.db                SQLite database (auto-created)
│  └─ email.log              FR15 notification log
├─ config.py
├─ run.py                    Dev entry point
├─ requirements.txt
└─ babel.cfg
```

---

## Development

Re-extract translatable strings after editing templates / Python:
```cmd
venv\Scripts\pybabel extract -F babel.cfg -o translations\messages.pot --keyword=_l --keyword=_ .
venv\Scripts\pybabel update -i translations\messages.pot -d translations
```
Edit the `.po` files (or extend `scripts\fill_translations.py`) then:
```cmd
venv\Scripts\pybabel compile -d translations
```

Run the smoke test (server must be up on :5000):
```cmd
venv\Scripts\python tests\smoke.py
```

Reset the database (deletes all data + uploads):
```cmd
del instance\gpas.db
del app\static\uploads\*.pdf
python scripts\init_db.py
python scripts\seed.py
```

---

## Mapping to the TM471 report

- **Chapter 1 — Objectives & Problem Definition:** the 8 objectives in §1.1 are realised through the FR coverage table above.
- **Chapter 2 — Literature Review:** the comparison table (§2.6) noted that no existing platform combines WCAG 2.1 AA + native Arabic + UG-project focus + low complexity. GPAS demonstrates exactly that combination.
- **Chapter 3 — Requirements & Analysis:** the ERD in §3.2.4 is realised in `app/models.py` with the same entity names (Users, Projects, Files, Categories, Project_Categories, Access_Log).

---

© 2026 Salman Dawara — Arab Open University, Kuwait.
