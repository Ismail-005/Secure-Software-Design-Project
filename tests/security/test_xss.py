import pytest

XSS_PAYLOAD = '<script>alert("xss")</script>'

def login_as(client, app, user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
        import datetime
        sess['last_active'] = datetime.datetime.utcnow().isoformat()
        sess['ip'] = '127.0.0.1'

def test_xss_not_reflected_in_login_error(client, db):
    r = client.post('/login', data={
        'username': XSS_PAYLOAD, 'password': 'pass'
    }, follow_redirects=True)
    # Jinja2 auto-escaping should prevent raw script tag in output
    assert b'<script>' not in r.data

def test_xss_escaped_in_flash_messages(client, app, db, customer_user, customer_account):
    login_as(client, app, customer_user)
    r = client.post(f'/accounts/{customer_account.id}/transfer', data={
        'to_account_number': XSS_PAYLOAD,
        'amount': '10',
        'nonce': 'xss-test-nonce-1'
    }, follow_redirects=True)
    assert b'<script>' not in r.data
