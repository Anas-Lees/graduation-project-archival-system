import re
from datetime import datetime
from collections import Counter
from flask import Blueprint, render_template, request, abort, send_file, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text, func, distinct
from flask_babel import gettext as _
from ..extensions import db
from ..models import Project, ProjectFile, Category, AccessLog
from ..forms import ProjectForm
from ..utils.security import role_required
from ..utils.files import save_upload, save_thumbnail
from ..utils.search import build_fts_query
from ..utils.mailer import send_email

bp = Blueprint("projects", __name__)


def _filter_choices():
    years = [y[0] for y in db.session.query(distinct(Project.year)).filter(Project.status == "approved").order_by(Project.year.desc()).all()]
    departments = [d[0] for d in db.session.query(distinct(Project.department)).filter(Project.status == "approved").order_by(Project.department).all()]
    categories = db.session.query(Category).order_by(Category.name_en).all()
    return years, departments, categories


@bp.route("/")
def browse():
    page = max(1, request.args.get("page", 1, type=int))
    per_page = current_app.config["PROJECTS_PER_PAGE"]
    year = request.args.get("year", type=int)
    department = (request.args.get("department") or "").strip() or None
    category_id = request.args.get("category", type=int)

    q = db.session.query(Project).filter(Project.status == "approved")
    if year:
        q = q.filter(Project.year == year)
    if department:
        q = q.filter(Project.department == department)
    if category_id:
        q = q.filter(Project.categories.any(Category.id == category_id))
    q = q.order_by(Project.year.desc(), Project.created_at.desc())

    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    years, departments, categories = _filter_choices()
    return render_template("projects/browse.html", items=items, total=total, page=page, per_page=per_page,
                           years=years, departments=departments, categories=categories,
                           q="", year=year, department=department, category_id=category_id, mode="browse")


@bp.route("/search")
def search():
    q_raw = (request.args.get("q") or "").strip()
    page = max(1, request.args.get("page", 1, type=int))
    per_page = current_app.config["PROJECTS_PER_PAGE"]
    year = request.args.get("year", type=int)
    department = (request.args.get("department") or "").strip() or None
    category_id = request.args.get("category", type=int)

    items, total = [], 0
    if q_raw:
        match = build_fts_query(q_raw)
        if match:
            sql = text("SELECT rowid FROM projects_fts WHERE projects_fts MATCH :m ORDER BY rank")
            ids = [row[0] for row in db.session.execute(sql, {"m": match}).fetchall()]
            if ids:
                base = db.session.query(Project).filter(Project.id.in_(ids), Project.status == "approved")
                if year:
                    base = base.filter(Project.year == year)
                if department:
                    base = base.filter(Project.department == department)
                if category_id:
                    base = base.filter(Project.categories.any(Category.id == category_id))
                # Preserve FTS rank order
                rank = {pid: i for i, pid in enumerate(ids)}
                rows = base.all()
                rows.sort(key=lambda p: rank.get(p.id, 1e9))
                total = len(rows)
                items = rows[(page - 1) * per_page: page * per_page]

    years, departments, categories = _filter_choices()
    return render_template("projects/browse.html", items=items, total=total, page=page, per_page=per_page,
                           years=years, departments=departments, categories=categories,
                           q=q_raw, year=year, department=department, category_id=category_id, mode="search")


@bp.route("/<int:pid>")
def view(pid):
    project = db.session.get(Project, pid)
    if not project or project.status != "approved":
        # Allow uploader/admin to preview pending
        if not project or not current_user.is_authenticated or not (
            current_user.has_role("doc") or project.uploader_id == current_user.id
        ):
            abort(404)
    log = AccessLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        project_id=project.id, action="view",
        ip=request.remote_addr, user_agent=(request.user_agent.string or "")[:255],
    )
    db.session.add(log)
    db.session.commit()
    return render_template("projects/view.html", project=project)


def _file_for_request(pid, fid):
    f = db.session.get(ProjectFile, fid)
    if not f or f.project_id != pid:
        abort(404)
    project = f.project
    if project.status != "approved" and not (
        current_user.is_authenticated and (
            current_user.has_role("doc") or project.uploader_id == current_user.id
        )
    ):
        abort(403)
    return f


@bp.route("/<int:pid>/files/<int:fid>")
@login_required
def download(pid, fid):
    f = _file_for_request(pid, fid)
    log = AccessLog(user_id=current_user.id, project_id=pid, action="download",
                    ip=request.remote_addr, user_agent=(request.user_agent.string or "")[:255])
    db.session.add(log)
    db.session.commit()
    return send_file(f.stored_path, as_attachment=True, download_name=f.filename)


@bp.route("/<int:pid>/media/<int:fid>")
def media(pid, fid):
    """Inline media (video) — same RBAC as download but served for in-page playback."""
    f = _file_for_request(pid, fid)
    return send_file(f.stored_path, mimetype=f.mimetype or "application/octet-stream",
                     as_attachment=False, conditional=True)


@bp.route("/upload", methods=["GET", "POST"])
@login_required
@role_required("student", "doc")
def upload():
    form = ProjectForm()
    cats = db.session.query(Category).order_by(Category.name_en).all()
    form.categories.choices = [(c.id, c.name_en) for c in cats]

    if form.validate_on_submit():
        project = Project(
            title=form.title.data.strip(),
            abstract=form.abstract.data.strip(),
            keywords=(form.keywords.data or "").strip(),
            year=form.year.data,
            department=form.department.data.strip(),
            github_url=(form.github_url.data or "").strip() or None,
            status="pending",
            uploader_id=current_user.id,
        )
        if form.categories.data:
            project.categories = db.session.query(Category).filter(Category.id.in_(form.categories.data)).all()

        # Optional thumbnail
        if form.thumbnail.data and form.thumbnail.data.filename:
            project.thumbnail_path = save_thumbnail(form.thumbnail.data)

        db.session.add(project)
        db.session.flush()

        # Main document (required)
        stored, original, mime, size = save_upload(form.file.data)
        db.session.add(ProjectFile(project_id=project.id, filename=original, stored_path=stored,
                                   mimetype=mime, size=size, kind="document"))

        # Optional video
        if form.video.data and form.video.data.filename:
            stored, original, mime, size = save_upload(form.video.data)
            db.session.add(ProjectFile(project_id=project.id, filename=original, stored_path=stored,
                                       mimetype=mime, size=size, kind="video"))

        # Optional slides
        if form.slides.data and form.slides.data.filename:
            stored, original, mime, size = save_upload(form.slides.data)
            db.session.add(ProjectFile(project_id=project.id, filename=original, stored_path=stored,
                                       mimetype=mime, size=size, kind="slides"))

        db.session.commit()

        # Notify all docs
        from ..models import User
        docs = db.session.query(User).filter(User.role == "doc").all()
        for d in docs:
            send_email(d.email, _("New project pending approval: %(title)s", title=project.title),
                       _("%(name)s submitted '%(title)s'. Review at /admin/approvals.",
                         name=current_user.full_name, title=project.title))
        flash(_("Project submitted and is pending admin approval."), "success")
        return redirect(url_for("projects.view", pid=project.id))
    return render_template("projects/upload.html", form=form)


@bp.route("/mine")
@login_required
def mine():
    items = db.session.query(Project).filter(Project.uploader_id == current_user.id).order_by(Project.created_at.desc()).all()
    return render_template("projects/mine.html", items=items)


# --------------------------------------------------------------------------- #
# Suggestion APIs (used by upload datalist + browse search box)               #
# --------------------------------------------------------------------------- #

_KW_SPLIT = re.compile(r"[,;|]| {2,}")


@bp.route("/api/keywords")
def api_keywords():
    """Return the most-used keywords across approved projects, ranked by frequency."""
    rows = db.session.query(Project.keywords).filter(
        Project.status == "approved", Project.keywords.isnot(None), Project.keywords != ""
    ).all()
    counter = Counter()
    for (kw,) in rows:
        for token in _KW_SPLIT.split(kw or ""):
            t = token.strip().lower()
            if 2 <= len(t) <= 40:
                counter[t] += 1
    top = [{"keyword": k, "count": c} for k, c in counter.most_common(40)]
    return jsonify(top)


@bp.route("/api/titles")
def api_titles():
    """Return up to 25 approved project titles to power search-bar autocomplete."""
    rows = db.session.query(Project.title).filter(Project.status == "approved").order_by(Project.created_at.desc()).limit(25).all()
    return jsonify([t for (t,) in rows])
