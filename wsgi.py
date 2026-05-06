"""WSGI entry point for production servers (PythonAnywhere, Gunicorn, Waitress).

PythonAnywhere expects a module-level `application` callable. This file is also
compatible with `waitress-serve --call wsgi:application` and `gunicorn wsgi:application`.

For PythonAnywhere, point the WSGI configuration file at this location:
    /home/<user>/graduation-project-archival-system/wsgi.py
And inside the PA WSGI config, the boilerplate they generate already imports
`application` from this file — no edits needed beyond setting the path.
"""
import os
import sys

# Ensure the project root is on the Python path even when launched outside it
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Load any .env that sits next to this file (optional)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(HERE, ".env"))
except Exception:
    pass

from app import create_app  # noqa: E402

application = create_app()


if __name__ == "__main__":
    # Local production-style run: python wsgi.py
    from waitress import serve
    serve(application, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
