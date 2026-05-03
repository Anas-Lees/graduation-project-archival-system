from functools import wraps
from flask import abort
from flask_login import current_user
from passlib.hash import bcrypt


def hash_password(plain: str) -> str:
    # NFR03: bcrypt
    return bcrypt.using(rounds=12).hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.verify(plain, hashed)
    except Exception:
        return False


def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_role(*roles):
                abort(403)
            return fn(*args, **kwargs)
        return decorated
    return wrapper
