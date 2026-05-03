import os
from flask import Flask, request, session, g
from config import Config
from .extensions import db, login_manager, csrf, babel
from .models import User


def select_locale():
    lang = session.get("lang")
    if lang in ("en", "ar"):
        return lang
    return request.accept_languages.best_match(["en", "ar"]) or "en"


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class)

    os.makedirs(os.path.join(app.root_path, "..", "instance"), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    babel.init_app(app, locale_selector=select_locale)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(uid):
        return db.session.get(User, int(uid))

    @app.before_request
    def _make_session_permanent():
        session.permanent = True
        g.lang = select_locale()
        g.is_rtl = g.lang == "ar"

    @app.context_processor
    def _inject_globals():
        return {
            "lang": g.lang,
            "is_rtl": g.is_rtl,
            "languages": app.config["LANGUAGES"],
        }

    from .blueprints.main import bp as main_bp
    from .blueprints.auth import bp as auth_bp
    from .blueprints.projects import bp as projects_bp
    from .blueprints.admin import bp as admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(projects_bp, url_prefix="/projects")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from .errors import register_error_handlers
    register_error_handlers(app)

    return app
