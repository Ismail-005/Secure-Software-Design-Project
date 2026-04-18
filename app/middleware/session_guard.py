from functools import wraps
from flask import session, request, redirect, url_for, abort
from flask_login import current_user
from datetime import datetime, timedelta

SESSION_TIMEOUT_MINUTES = 30

def session_guard(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        last_active = session.get('last_active')
        if last_active:
            elapsed = datetime.utcnow() - datetime.fromisoformat(last_active)
            if elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                session.clear()
                return redirect(url_for('auth.login'))
        stored_ip = session.get('ip')
        if stored_ip and stored_ip != request.remote_addr:
            session.clear()
            abort(401)
        session['last_active'] = datetime.utcnow().isoformat()
        return f(*args, **kwargs)
    return decorated
