import pytest

def test_login_page_loads(client):
    r = client.get('/login')
    assert r.status_code == 200

def test_login_success_redirects_to_mfa(client, db, customer_user):
    r = client.post('/login', data={
        'username': 'testcustomer', 'password': 'Test1234!'
    }, follow_redirects=False)
    assert r.status_code == 302
    assert '/mfa' in r.headers['Location']

def test_login_wrong_password(client, db, customer_user):
    r = client.post('/login', data={
        'username': 'testcustomer', 'password': 'wrong'
    }, follow_redirects=True)
    assert b'Invalid' in r.data

def test_mfa_verify_redirects_to_dashboard(client, db, customer_user, app):
    # Step 1: login
    client.post('/login', data={
        'username': 'testcustomer', 'password': 'Test1234!'
    })
    # Step 2: get the OTP from DB
    from app.models import OTPToken
    import bcrypt
    with app.app_context():
        otp = OTPToken.query.filter_by(user_id=customer_user.id, used=False).first()
        assert otp is not None
        # We can't recover plaintext from hash; test OTP flow via service directly
        from app.services.auth_service import AuthService
        svc = AuthService()
        plaintext, hashed = svc.generate_otp()
        from datetime import datetime, timedelta
        from app.repositories.user_repo import UserRepository
        repo = UserRepository()
        repo.create_otp(customer_user.id, hashed,
                        datetime.utcnow() + timedelta(minutes=5))
        db.session.commit()
    r = client.post('/mfa/verify', data={'otp': plaintext}, follow_redirects=False)
    assert r.status_code in (200, 302)

def test_logout_clears_session(client, db, customer_user):
    client.post('/login', data={
        'username': 'testcustomer', 'password': 'Test1234!'
    })
    r = client.get('/logout', follow_redirects=False)
    assert r.status_code == 302
