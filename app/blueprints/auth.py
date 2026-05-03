from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_babel import gettext as _
from ..extensions import db
from ..models import User
from ..forms import RegisterForm, LoginForm
from ..utils.security import hash_password, verify_password
from ..utils.mailer import send_email

bp = Blueprint("auth", __name__)

VERIFY_SALT = "email-verify"


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        existing = db.session.query(User).filter_by(email=form.email.data.lower().strip()).first()
        if existing:
            flash(_("An account with that email already exists."), "danger")
            return render_template("auth/register.html", form=form)
        user = User(
            email=form.email.data.lower().strip(),
            full_name=form.full_name.data.strip(),
            password_hash=hash_password(form.password.data),
            role="student",
            email_verified=False,
        )
        db.session.add(user)
        db.session.commit()
        token = _serializer().dumps(user.email, salt=VERIFY_SALT)
        verify_url = url_for("auth.verify", token=token, _external=True)
        send_email(user.email, _("Verify your GPAS account"),
                   _("Welcome to GPAS! Please verify your email by visiting: %(url)s", url=verify_url))
        flash(_("Account created. Check email.log to verify your account."), "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@bp.route("/verify/<token>")
def verify(token):
    try:
        email = _serializer().loads(token, salt=VERIFY_SALT, max_age=60 * 60 * 24)
    except SignatureExpired:
        flash(_("Verification link expired."), "danger")
        return redirect(url_for("auth.login"))
    except BadSignature:
        flash(_("Invalid verification link."), "danger")
        return redirect(url_for("auth.login"))
    user = db.session.query(User).filter_by(email=email).first()
    if user and not user.email_verified:
        user.email_verified = True
        db.session.commit()
        flash(_("Email verified! You can now sign in."), "success")
    return redirect(url_for("auth.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data.lower().strip()).first()
        if not user or not verify_password(form.password.data, user.password_hash):
            flash(_("Invalid email or password."), "danger")
            return render_template("auth/login.html", form=form)
        login_user(user, remember=form.remember.data)
        flash(_("Welcome back, %(name)s!", name=user.full_name), "success")
        nxt = request.args.get("next")
        return redirect(nxt or url_for("main.index"))
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash(_("You have been signed out."), "info")
    return redirect(url_for("main.index"))
