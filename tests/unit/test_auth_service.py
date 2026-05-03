import pytest
from unittest.mock import patch
from app.services.auth_service import AuthService

def test_hash_and_verify_password():
    svc = AuthService()
    h = svc.hash_password('MyPass123!')
    assert svc.verify_password('MyPass123!', h) is True
    assert svc.verify_password('wrong', h) is False

def test_generate_otp_returns_plaintext_and_hash():
    svc = AuthService()
    plaintext, hashed = svc.generate_otp()
    assert len(plaintext) == 6
    assert plaintext.isdigit()
    assert svc.verify_password(plaintext, hashed) is True

def test_attempt_login_success(db, customer_user):
    svc = AuthService()
    ok, msg, uid = svc.attempt_login('testcustomer', 'Test1234!', '127.0.0.1')
    assert ok is True
    assert uid == customer_user.id

def test_attempt_login_wrong_password(db, customer_user):
    svc = AuthService()
    ok, msg, uid = svc.attempt_login('testcustomer', 'wrongpass', '127.0.0.1')
    assert ok is False
    assert uid is None
    from app.models import AuditLog
    log = AuditLog.query.filter_by(action='LOGIN_FAILURE').one()
    assert log.details['username'] == 'testcustomer'

def test_attempt_login_unknown_user_audits_attempted_username(db):
    svc = AuthService()
    ok, msg, uid = svc.attempt_login('missinguser', 'wrongpass', '127.0.0.1')
    assert ok is False
    assert uid is None
    from app.models import AuditLog
    log = AuditLog.query.filter_by(action='LOGIN_FAILURE').one()
    assert log.user_id is None
    assert log.details['username'] == 'missinguser'

def test_attempt_login_locks_after_five_failures(db, customer_user):
    svc = AuthService()
    for _ in range(5):
        svc.attempt_login('testcustomer', 'bad', '127.0.0.1')
    ok, msg, uid = svc.attempt_login('testcustomer', 'Test1234!', '127.0.0.1')
    assert ok is False
    assert 'locked' in msg.lower()

def test_verify_otp(db, customer_user, app):
    svc = AuthService()
    with app.app_context():
        plaintext, _ = svc.generate_otp()
        # Store OTP for user
        from datetime import datetime, timedelta
        from app.repositories.user_repo import UserRepository
        import bcrypt
        token_hash = bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt()).decode()
        repo = UserRepository()
        repo.create_otp(customer_user.id, token_hash,
                        datetime.utcnow() + timedelta(minutes=5))
        db.session.commit()
        result = svc.verify_otp(customer_user.id, plaintext)
        assert result is True
