from functools import wraps
from flask import abort
from flask_login import current_user

def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role.value not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator
