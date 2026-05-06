# Deploying GPAS to PythonAnywhere (free, always-on)

This guide walks you through hosting GPAS on **PythonAnywhere** so it's reachable from any device, 24/7, without your laptop.

**Estimated time:** ~10 minutes. **Cost:** $0 (free Beginner account).

---

## 1. Create a free PythonAnywhere account

1. Go to <https://www.pythonanywhere.com/registration/register/beginner/>
2. Pick a username — this becomes your URL: `https://<username>.pythonanywhere.com`
3. Confirm your email.

---

## 2. Open a Bash console and clone the repo

In the PythonAnywhere dashboard:

1. Top-right menu → **Consoles** → **Bash**
2. Run:
   ```bash
   cd ~
   git clone https://github.com/Anas-Lees/graduation-project-archival-system.git
   cd graduation-project-archival-system
   bash scripts/pa_bootstrap.sh
   ```

The bootstrap script will:
- Create a Python 3.11 virtualenv called `gpas-venv`
- Install all dependencies
- Compile translations
- Generate a strong `SECRET_KEY` and write it to `.env`
- Initialise the SQLite database and seed demo data (4 demo accounts + 10 sample projects)

It takes 1–2 minutes. When it finishes you'll see a **"Bootstrap complete"** message.

---

## 3. Create the web app

1. Top-right menu → **Web** → **Add a new web app**
2. Pick **Manual configuration** → **Python 3.11**
3. After it's created, fill in these fields on the Web tab:

| Field | Value |
|---|---|
| **Source code** | `/home/<username>/graduation-project-archival-system` |
| **Working directory** | `/home/<username>/graduation-project-archival-system` |
| **Virtualenv** | `/home/<username>/.virtualenvs/gpas-venv` |

(Replace `<username>` with your actual PythonAnywhere username.)

---

## 4. Configure WSGI

On the Web tab, click the link under **Code → WSGI configuration file**.
PythonAnywhere will open a file editor. **Replace its entire contents** with the
contents of `scripts/pa_wsgi.py` from the repo (a 25-line snippet).

> The file already reads your username from the `USER` env var, so usually you
> don't need to edit anything. If the path doesn't auto-resolve, change
> `PROJECT_PATH` near the top to your actual repo folder.

Save (Ctrl+S).

---

## 5. Map static files

On the Web tab → **Static files**, add **two** mappings:

| URL | Directory |
|---|---|
| `/static/` | `/home/<username>/graduation-project-archival-system/app/static/` |

This lets the browser fetch CSS / JS / uploaded thumbnails directly from disk
without going through Python (much faster).

---

## 6. Reload and visit

Top of the Web tab → **green Reload button**.

Open `https://<username>.pythonanywhere.com` in your browser. You should see the
GPAS home page with the hero, popular categories, and 8 seeded projects.

Sign in with one of the demo accounts:

| Role | Email | Password |
|---|---|---|
| Student | `student@aou.edu.kw` | `Student123!` |
| Doctor | `doc@aou.edu.kw` | `Doctor123!` |

---

## Updating the app after a new git push

Every time you push code to GitHub:

```bash
# In a PythonAnywhere Bash console
cd ~/graduation-project-archival-system
git pull
workon gpas-venv
pip install -r requirements.txt        # only if requirements.txt changed
pybabel compile -d translations         # only if translations changed
```

Then click **Reload** on the Web tab. New code is live.

---

## Adding your own data after deploy

The seed data is just a starting demo. To add real graduation projects:

1. Sign in to your live site as a Doctor (`doc@aou.edu.kw`)
2. Go to **Doctor panel → Users** and create real student accounts
3. Students sign in with their real accounts and use **Upload** to submit
4. You approve their submissions from **Doctor panel → Approvals**

You can also reset everything (drop the seed data + your uploads):

```bash
cd ~/graduation-project-archival-system
workon gpas-venv
rm -f instance/gpas.db instance/email.log
rm -f app/static/uploads/*.pdf app/static/uploads/*.mp4 \
      app/static/uploads/thumbs/*.svg
python scripts/init_db.py
python scripts/seed.py
# then click Reload on the Web tab
```

---

## Free tier limits — things to know

| Limit | Free tier | Likely impact |
|---|---|---|
| Storage | 512 MB | Plenty for code + a few hundred small uploads. Big videos eat into it fast. |
| Custom domain | Not available | Stick with `<username>.pythonanywhere.com`. Upgrade ($5/mo Hacker plan) if you want your own domain. |
| HTTPS | Always-on, free | No setup needed. |
| Outbound internet | Whitelisted only | We don't make external calls, so nothing to do. |
| Always-on | ✓ Free tier never sleeps | Your site is up even at 4 AM. |
| Web app idle timeout | 3 months of zero hits → app suspends | Click Reload once every 3 months and you're fine. |

---

## Troubleshooting

**"Something went wrong :-(" when visiting the site**
Check the Web tab → **Error log**. Most common causes:
- WSGI file path doesn't match the actual folder name
- Virtualenv path is wrong
- You forgot to click **Reload** after changing config

**500 errors after a `git pull`**
- Did `requirements.txt` change? Run `pip install -r requirements.txt`.
- Did `models.py` change? You may need to drop/recreate the DB:
  `rm instance/gpas.db && python scripts/init_db.py && python scripts/seed.py`
- Click **Reload** afterwards.

**"Sign-in works locally but fails on PythonAnywhere"**
Make sure `.env` was created by the bootstrap script. Check with `cat .env` —
it should contain `SECRET_KEY=...` and `FLASK_HTTPS=1`. If missing, re-run
`bash scripts/pa_bootstrap.sh`.

**Translations show in English even after switching language**
The `.mo` files might not have compiled. Run:
```bash
workon gpas-venv
python scripts/fill_translations.py    # rebuilds AR + EN .mo
```
Then click **Reload**.

---

## Summary of what's installed

| File on PythonAnywhere | What it does |
|---|---|
| `~/.virtualenvs/gpas-venv/` | Python 3.11 venv with Flask, SQLAlchemy, etc. |
| `~/graduation-project-archival-system/` | Your code (git clone of the repo) |
| `~/graduation-project-archival-system/.env` | `SECRET_KEY` + `FLASK_HTTPS=1` |
| `~/graduation-project-archival-system/instance/gpas.db` | SQLite database |
| `~/graduation-project-archival-system/app/static/uploads/` | Uploaded PDFs / videos / thumbnails |

That's it. Your project is live, free, and always-on.
