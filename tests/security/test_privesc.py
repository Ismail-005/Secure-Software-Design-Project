import pytest

def login_as(client, user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
        import datetime
        sess['last_active'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sess['ip'] = '127.0.0.1'

def test_customer_cannot_access_admin_users(client, db, customer_user):
    login_as(client, customer_user)
    r = client.get('/admin/users')
    assert r.status_code == 403

def test_customer_cannot_access_audit_logs(client, db, customer_user):
    login_as(client, customer_user)
    r = client.get('/admin/audit-logs')
    assert r.status_code == 403

def test_customer_cannot_access_fraud_review(client, db, customer_user):
    login_as(client, customer_user)
    r = client.get('/admin/fraud-review')
    assert r.status_code == 403

def test_unauthenticated_cannot_access_dashboard(client):
    r = client.get('/dashboard', follow_redirects=False)
    assert r.status_code == 302

def test_admin_can_access_audit_logs(client, db, admin_user):
    login_as(client, admin_user)
    r = client.get('/admin/audit-logs')
    assert r.status_code == 200

def test_admin_can_unblock_locked_user(client, db, admin_user, customer_user):
    from datetime import datetime, timedelta, timezone
    from app.repositories.user_repo import UserRepository
    repo = UserRepository()
    repo.lock_account(customer_user.id, datetime.now(timezone.utc) + timedelta(minutes=30))
    db.session.commit()

    login_as(client, admin_user)
    r = client.post(f'/admin/users/{customer_user.id}/unlock', follow_redirects=False)
    assert r.status_code == 302

    db.session.refresh(customer_user)
    assert customer_user.locked_until is None
    assert customer_user.failed_login_attempts == 0
