import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me-in-production-please-32chars")

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "instance", "gpas.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB per upload
    ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}

    # NFR05: 30-min idle timeout
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # SESSION_COOKIE_SECURE = True  # enable behind HTTPS in production

    # i18n
    LANGUAGES = {"en": "English", "ar": "العربية"}
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "Asia/Kuwait"
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(basedir, "translations")

    # FR15 mailer
    EMAIL_LOG_PATH = os.path.join(basedir, "instance", "email.log")

    # Pagination
    PROJECTS_PER_PAGE = 12
