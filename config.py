import os
import secrets
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


def _truthy(val):
    return str(val).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Default config. Production overrides come from environment variables."""

    # Secret key: must be set via env in production. We generate a one-shot fallback
    # so dev runs don't crash, but warn loudly on startup.
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32)
    _SECRET_KEY_FROM_ENV = bool(os.environ.get("SECRET_KEY"))

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "instance", "gpas.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads directory — overridable via env so PythonAnywhere users can point
    # it at a path that survives redeploys (e.g. /home/<user>/gpas-uploads/)
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER", os.path.join(basedir, "app", "static", "uploads")
    )
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200MB total per submission

    ALLOWED_DOC_EXTENSIONS = {"pdf", "docx", "doc"}
    ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm", "mov", "m4v"}
    ALLOWED_SLIDES_EXTENSIONS = {"pptx", "ppt", "pdf"}
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "svg"}
    ALLOWED_EXTENSIONS = (
        ALLOWED_DOC_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS
        | ALLOWED_SLIDES_EXTENSIONS | ALLOWED_IMAGE_EXTENSIONS
    )

    # NFR05: 30-min idle timeout
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Enable Secure cookies automatically behind HTTPS (set FLASK_HTTPS=1 in prod)
    SESSION_COOKIE_SECURE = _truthy(os.environ.get("FLASK_HTTPS", "0"))

    # i18n
    LANGUAGES = {"en": "English", "ar": "العربية"}
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "Asia/Kuwait"
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(basedir, "translations")

    # FR15 mailer — log file, overridable
    EMAIL_LOG_PATH = os.environ.get(
        "EMAIL_LOG_PATH", os.path.join(basedir, "instance", "email.log")
    )

    # Pagination
    PROJECTS_PER_PAGE = 12

    # Production hardening flags applied via WSGI middleware in app/__init__.py
    PREFERRED_URL_SCHEME = "https" if _truthy(os.environ.get("FLASK_HTTPS", "0")) else "http"
