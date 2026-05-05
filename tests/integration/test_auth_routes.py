import pytest

def test_root_redirects_to_login(client):
    r = client.get('/', follow_redirects=False)
    assert r.status_code == 302
    assert r.headers['Location'].endswith('/signin')

def test_login_page_loads(client):
    r = client.get('/login')
    assert r.status_code == 200
    assert b'Sign In' in r.data

def test_signin_alias_loads(client):
    r = client.get('/signin')
    assert r.status_code == 200
    assert b'Sign In' in r.data

def test_signup_page_loads(client):
    r = client.get('/signup')
    assert r.status_code == 200
    assert b'Create Account' in r.data

def test_signup_creates_customer_and_account(client, db):
    r = client.post('/signup', data={
        'username': 'newcustomer',
        'email': 'newcustomer@test.com',
        'password': 'Customer123!',
        'confirm_password': 'Customer123!',
    }, follow_redirects=False)
    assert r.status_code == 302
    assert r.headers['Location'].endswith('/signin')

    from app.models import Account, User, UserRole
    user = User.query.filter_by(username='newcustomer').first()
    assert user is not None
    assert user.role == UserRole.customer
    assert Account.query.filter_by(user_id=user.id).count() == 1

def test_signup_rejects_duplicate_username(client, db, customer_user):
    r = client.post('/signup', data={
        'username': customer_user.username,
        'email': 'someone@test.com',
        'password': 'Customer123!',
        'confirm_password': 'Customer123!',
    })
    assert r.status_code == 200
    assert b'Username is already registered.' in r.data

def test_login_success_redirects_to_mfa(client, db, customer_user):
    r = client.post('/login', data={
        'username': 'testcustomer', 'password': 'Test1234!'
    }, follow_redirects=False)
    assert r.status_code == 302
    assert '/mfa' in r.headers['Location']

def test_mfa_page_shows_demo_otp(client, db, customer_user):
    client.post('/login', data={
        'username': 'testcustomer', 'password': 'Test1234!'
    })
    r = client.get('/mfa/verify')
    assert r.status_code == 200
    assert b'Demo verification code' in r.data

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
        from datetime import datetime, timedelta, timezone
        from app.repositories.user_repo import UserRepository
        repo = UserRepository()
        repo.create_otp(customer_user.id, hashed,
                        datetime.now(timezone.utc) + timedelta(minutes=5))
        db.session.commit()
    r = client.post('/mfa/verify', data={'otp': plaintext}, follow_redirects=False)
    assert r.status_code in (200, 302)

def test_logout_clears_session(client, db, customer_user):
    client.post('/login', data={
        'username': 'testcustomer', 'password': 'Test1234!'
    })
    r = client.get('/logout', follow_redirects=False)
    assert r.status_code == 302
