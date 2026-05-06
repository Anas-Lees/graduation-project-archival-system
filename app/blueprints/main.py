from flask import Blueprint, render_template, redirect, url_for, request, session
from sqlalchemy import func
from ..extensions import db
from ..models import Project, Category

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    recent = (
        db.session.query(Project)
        .filter(Project.status == "approved")
        .order_by(Project.approved_at.desc().nullslast(), Project.created_at.desc())
        .limit(6)
        .all()
    )
    counts = {
        "total": db.session.query(func.count(Project.id)).filter(Project.status == "approved").scalar() or 0,
        "departments": db.session.query(func.count(func.distinct(Project.department))).filter(Project.status == "approved").scalar() or 0,
        "years": db.session.query(func.count(func.distinct(Project.year))).filter(Project.status == "approved").scalar() or 0,
    }
    # Popular categories — count approved projects per category, top 8
    popular = (
        db.session.query(Category, func.count(Project.id).label("c"))
        .join(Category.projects)
        .filter(Project.status == "approved")
        .group_by(Category.id)
        .order_by(func.count(Project.id).desc())
        .limit(8).all()
    )
    return render_template("index.html", recent=recent, counts=counts, popular=popular)


@bp.route("/lang/<code>")
def set_lang(code):
    if code in ("en", "ar"):
        session["lang"] = code
    return redirect(request.referrer or url_for("main.index"))


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/privacy")
def privacy():
    return render_template("privacy.html")
