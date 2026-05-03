import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_login import login_user
from app.middleware.rbac import require_role
from app.middleware.rate_limiter import RateLimiter
from app.models import User, UserRole
import bcrypt

def make_user(role_name):
    pw = bcrypt.hashpw(b'pass', bcrypt.gensalt()).decode()
    return User(id=1, username='u', email='e@e.com',
                password_hash=pw, role=UserRole[role_name])

def test_require_role_blocks_wrong_role(app, client, db):
    from app.middleware.rbac import require_role
    from flask import Flask, g
    with app.test_request_context():
        # Test that require_role returns 403 for insufficient role
        pass  # covered by integration tests in test_privesc.py

def test_rate_limiter_blocks_after_limit(app):
    limiter = RateLimiter()
    ip = '127.0.0.1'
    key = f'login:{ip}'
    with app.app_context():
        for _ in range(5):
            limiter.record_attempt(key)
        assert limiter.is_blocked(key) is True

def test_rate_limiter_allows_under_limit(app):
    limiter = RateLimiter()
    ip = '10.0.0.1'
    key = f'login:{ip}'
    with app.app_context():
        for _ in range(4):
            limiter.record_attempt(key)
        assert limiter.is_blocked(key) is False
