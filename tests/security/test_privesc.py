import pytest

def login_as(client, user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
        import datetime
        sess['last_active'] = datetime.datetime.utcnow().isoformat()
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
