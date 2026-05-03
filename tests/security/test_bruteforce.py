import pytest
from app.services.auth_service import AuthService
from app.models import User

def test_account_locked_after_five_failures(db, customer_user):
    svc = AuthService()
    for _ in range(5):
        svc.attempt_login('testcustomer', 'wrongpass', '127.0.0.1')
    db.session.commit()
    db.session.refresh(customer_user)
    assert customer_user.locked_until is not None

def test_correct_password_rejected_when_locked(db, customer_user):
    svc = AuthService()
    for _ in range(5):
        svc.attempt_login('testcustomer', 'wrongpass', '127.0.0.1')
    db.session.commit()
    ok, msg, uid = svc.attempt_login('testcustomer', 'Test1234!', '127.0.0.1')
    assert ok is False
    assert 'locked' in msg.lower()

def test_rate_limiter_blocks_rapid_requests(app):
    from app.middleware.rate_limiter import RateLimiter
    limiter = RateLimiter()
    with app.app_context():
        key = 'login:10.0.0.2'
        for _ in range(5):
            limiter.record_attempt(key)
        assert limiter.is_blocked(key) is True
