from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import event, Index
from .extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")  # student/faculty/admin/sysadmin
    language = db.Column(db.String(5), default="en")
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    uploads = db.relationship("Project", foreign_keys="Project.uploader_id", back_populates="uploader")
    approvals = db.relationship("Project", foreign_keys="Project.approver_id", back_populates="approver")

    def has_role(self, *roles):
        return self.role in roles

    @property
    def first_name(self):
        """Return the user's given name, skipping titles like 'Dr.' / 'Prof.'."""
        TITLES = {"dr", "dr.", "prof", "prof.", "mr", "mr.", "ms", "ms.", "mrs", "mrs.", "miss"}
        if not self.full_name:
            return ""
        for token in self.full_name.split():
            if token.lower().rstrip(".") + ("." if token.endswith(".") else "") in TITLES:
                continue
            if token.lower() in TITLES:
                continue
            return token
        return self.full_name.split()[0]


project_categories = db.Table(
    "project_categories",
    db.Column("project_id", db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    db.Column("category_id", db.Integer, db.ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(80), unique=True, nullable=False)
    name_ar = db.Column(db.String(80), unique=True, nullable=False)

    projects = db.relationship("Project", secondary=project_categories, back_populates="categories")

    def localized(self, lang):
        return self.name_ar if lang == "ar" else self.name_en


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.String(500), default="")
    year = db.Column(db.Integer, nullable=False, index=True)
    department = db.Column(db.String(120), nullable=False, index=True)
    github_url = db.Column(db.String(500))
    thumbnail_path = db.Column(db.String(500))  # relative path under app/static/, or None
    status = db.Column(db.String(20), default="pending", index=True)  # pending/approved/rejected
    uploader_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    approved_at = db.Column(db.DateTime)

    uploader = db.relationship("User", foreign_keys=[uploader_id], back_populates="uploads")
    approver = db.relationship("User", foreign_keys=[approver_id], back_populates="approvals")
    files = db.relationship("ProjectFile", back_populates="project", cascade="all, delete-orphan")
    categories = db.relationship("Category", secondary=project_categories, back_populates="projects")
    access_logs = db.relationship("AccessLog", back_populates="project", cascade="all, delete-orphan")


class ProjectFile(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    stored_path = db.Column(db.String(500), nullable=False)
    mimetype = db.Column(db.String(100))
    size = db.Column(db.Integer)
    kind = db.Column(db.String(20), nullable=False, default="document")  # document / video / slides
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship("Project", back_populates="files")


# Convenience accessors on Project for the three logical slots
def _files_of_kind(self, kind):
    return [f for f in self.files if f.kind == kind]

Project.document_files = property(lambda self: _files_of_kind(self, "document"))
Project.video_file = property(lambda self: (_files_of_kind(self, "video") or [None])[0])
Project.slides_file = property(lambda self: (_files_of_kind(self, "slides") or [None])[0])


class AccessLog(db.Model):
    __tablename__ = "access_log"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # view / download
    ip = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    project = db.relationship("Project", back_populates="access_logs")


Index("ix_projects_status_year", Project.status, Project.year)


# FR06: SQLite FTS5 virtual table + sync triggers
FTS_SETUP_SQL = [
    """CREATE VIRTUAL TABLE IF NOT EXISTS projects_fts USING fts5(
        title, abstract, keywords, content='projects', content_rowid='id', tokenize='unicode61'
    );""",
    """CREATE TRIGGER IF NOT EXISTS projects_ai AFTER INSERT ON projects BEGIN
        INSERT INTO projects_fts(rowid, title, abstract, keywords)
        VALUES (new.id, new.title, new.abstract, new.keywords);
    END;""",
    """CREATE TRIGGER IF NOT EXISTS projects_ad AFTER DELETE ON projects BEGIN
        INSERT INTO projects_fts(projects_fts, rowid, title, abstract, keywords)
        VALUES('delete', old.id, old.title, old.abstract, old.keywords);
    END;""",
    """CREATE TRIGGER IF NOT EXISTS projects_au AFTER UPDATE ON projects BEGIN
        INSERT INTO projects_fts(projects_fts, rowid, title, abstract, keywords)
        VALUES('delete', old.id, old.title, old.abstract, old.keywords);
        INSERT INTO projects_fts(rowid, title, abstract, keywords)
        VALUES (new.id, new.title, new.abstract, new.keywords);
    END;""",
]


def install_fts(connection):
    for stmt in FTS_SETUP_SQL:
        connection.exec_driver_sql(stmt)
