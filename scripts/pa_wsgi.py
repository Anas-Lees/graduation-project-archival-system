"""
PythonAnywhere WSGI configuration — paste this into the WSGI file PA generates
for you (something like /var/www/<user>_pythonanywhere_com_wsgi.py).

The path "graduation-project-archival-system" below assumes you cloned with the
default repo name. Change it to match your actual folder if different.
"""
import os
import sys

# 1. Add your project to PYTHONPATH ---------------------------------------- #
USERNAME = os.environ.get("USER") or "REPLACE-WITH-YOUR-USERNAME"
PROJECT_PATH = f"/home/{USERNAME}/graduation-project-archival-system"
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

# 2. Load the .env (created by pa_bootstrap.sh) ---------------------------- #
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_PATH, ".env"))
except Exception:
    pass

# 3. Hand the Flask app to PA's WSGI runner -------------------------------- #
from wsgi import application  # noqa: F401,E402  (PA imports this name)
