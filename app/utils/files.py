import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def is_allowed(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def save_upload(file_storage):
    """Save an uploaded werkzeug FileStorage; return (stored_path, original_filename, mimetype, size)."""
    original = secure_filename(file_storage.filename or "file")
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else "bin"
    unique = f"{uuid.uuid4().hex}.{ext}"
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    full = os.path.join(folder, unique)
    file_storage.save(full)
    size = os.path.getsize(full)
    return full, original, file_storage.mimetype or "application/octet-stream", size


def save_thumbnail(file_storage):
    """Save an image into uploads/thumbs/. Returns the static-relative URL path
    (e.g. 'uploads/thumbs/<uuid>.png') so it can be passed to url_for('static', filename=...).
    """
    original = secure_filename(file_storage.filename or "thumb")
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else "png"
    unique = f"{uuid.uuid4().hex}.{ext}"
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], "thumbs")
    os.makedirs(folder, exist_ok=True)
    full = os.path.join(folder, unique)
    file_storage.save(full)
    # Path relative to app/static/ — what the template needs
    return f"uploads/thumbs/{unique}"
