from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from flask_babel import gettext as _
from sqlalchemy import func, desc
from ..extensions import db
from ..models import Project, User, AccessLog, Category, ProjectFile
from ..forms import RejectForm, UserAdminForm
from ..utils.security import role_required, hash_password
from ..utils.mailer import send_email

bp = Blueprint("admin", __name__)


@bp.before_request
@login_required
@role_required("doc")
def _gate():
    pass


@bp.route("/")
def dashboard():
    pending_count = db.session.query(func.count(Project.id)).filter(Project.status == "pending").scalar()
    total_projects = db.session.query(func.count(Project.id)).filter(Project.status == "approved").scalar()
    user_count = db.session.query(func.count(User.id)).scalar()
    return render_template("admin/dashboard.html", pending_count=pending_count,
                           total_projects=total_projects, user_count=user_count)


@bp.route("/approvals")
def approvals():
    pending = db.session.query(Project).filter(Project.status == "pending").order_by(Project.created_at.desc()).all()
    reject_form = RejectForm()
    return render_template("admin/approvals.html", pending=pending, reject_form=reject_form)


@bp.route("/approvals/<int:pid>/approve", methods=["POST"])
def approve(pid):
    project = db.session.get(Project, pid)
    if not project:
        abort(404)
    project.status = "approved"
    project.approver_id = current_user.id
    project.approved_at = datetime.utcnow()
    db.session.commit()
    send_email(project.uploader.email, _("Your project '%(t)s' was approved", t=project.title),
               _("Your submission is now publicly available in GPAS."))
    flash(_("Project approved."), "success")
    return redirect(url_for("admin.approvals"))


@bp.route("/approvals/<int:pid>/reject", methods=["POST"])
def reject(pid):
    project = db.session.get(Project, pid)
    if not project:
        abort(404)
    form = RejectForm()
    if form.validate_on_submit():
        project.status = "rejected"
        project.approver_id = current_user.id
        project.rejection_reason = form.reason.data
        db.session.commit()
        send_email(project.uploader.email, _("Your project '%(t)s' was rejected", t=project.title),
                   _("Reason: %(r)s", r=form.reason.data))
        flash(_("Project rejected."), "info")
    else:
        flash(_("A rejection reason is required."), "danger")
    return redirect(url_for("admin.approvals"))


@bp.route("/users")
def users():
    all_users = db.session.query(User).order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@bp.route("/users/new", methods=["GET", "POST"])
def user_new():
    form = UserAdminForm()
    if form.validate_on_submit():
        if not form.password.data:
            flash(_("Password is required for new users."), "danger")
            return render_template("admin/user_form.html", form=form, mode="new")
        if db.session.query(User).filter_by(email=form.email.data.lower().strip()).first():
            flash(_("Email already in use."), "danger")
            return render_template("admin/user_form.html", form=form, mode="new")
        user = User(
            email=form.email.data.lower().strip(),
            full_name=form.full_name.data.strip(),
            role=form.role.data,
            password_hash=hash_password(form.password.data),
            email_verified=True,
        )
        db.session.add(user)
        db.session.commit()
        flash(_("User created."), "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, mode="new")


@bp.route("/users/<int:uid>/edit", methods=["GET", "POST"])
def user_edit(uid):
    user = db.session.get(User, uid)
    if not user:
        abort(404)
    form = UserAdminForm(obj=user)
    if form.validate_on_submit():
        user.full_name = form.full_name.data.strip()
        user.email = form.email.data.lower().strip()
        user.role = form.role.data
        if form.password.data:
            user.password_hash = hash_password(form.password.data)
        db.session.commit()
        flash(_("User updated."), "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, mode="edit", user=user)


@bp.route("/users/<int:uid>/delete", methods=["POST"])
def user_delete(uid):
    user = db.session.get(User, uid)
    if not user:
        abort(404)
    if user.id == current_user.id:
        flash(_("You cannot delete your own account."), "danger")
        return redirect(url_for("admin.users"))
    db.session.delete(user)
    db.session.commit()
    flash(_("User deleted."), "info")
    return redirect(url_for("admin.users"))


@bp.route("/reports")
def reports():
    since = datetime.utcnow() - timedelta(days=30)
    totals = {
        "approved": db.session.query(func.count(Project.id)).filter(Project.status == "approved").scalar(),
        "pending": db.session.query(func.count(Project.id)).filter(Project.status == "pending").scalar(),
        "rejected": db.session.query(func.count(Project.id)).filter(Project.status == "rejected").scalar(),
        "users": db.session.query(func.count(User.id)).scalar(),
        "downloads_30d": db.session.query(func.count(AccessLog.id)).filter(AccessLog.action == "download", AccessLog.created_at >= since).scalar(),
        "views_30d": db.session.query(func.count(AccessLog.id)).filter(AccessLog.action == "view", AccessLog.created_at >= since).scalar(),
    }
    top_views = (
        db.session.query(Project, func.count(AccessLog.id).label("c"))
        .join(AccessLog, AccessLog.project_id == Project.id)
        .filter(AccessLog.action == "view")
        .group_by(Project.id).order_by(desc("c")).limit(5).all()
    )
    top_downloads = (
        db.session.query(Project, func.count(AccessLog.id).label("c"))
        .join(AccessLog, AccessLog.project_id == Project.id)
        .filter(AccessLog.action == "download")
        .group_by(Project.id).order_by(desc("c")).limit(5).all()
    )
    by_dept = (
        db.session.query(Project.department, func.count(Project.id).label("c"))
        .filter(Project.status == "approved")
        .group_by(Project.department).order_by(desc("c")).all()
    )
    by_year = (
        db.session.query(Project.year, func.count(Project.id).label("c"))
        .filter(Project.status == "approved")
        .group_by(Project.year).order_by(Project.year.desc()).all()
    )
    return render_template("admin/reports.html", totals=totals, top_views=top_views,
                           top_downloads=top_downloads, by_dept=by_dept, by_year=by_year)
