"""Create tables and FTS5 virtual table + sync triggers."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models import install_fts


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        # Install FTS5 + triggers using a raw connection
        with db.engine.begin() as conn:
            install_fts(conn)
        print("Database initialized at:", app.config["SQLALCHEMY_DATABASE_URI"])


if __name__ == "__main__":
    main()
