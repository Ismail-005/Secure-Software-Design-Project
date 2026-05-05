import pytest

def login_as(client, app, user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
        import datetime
        sess['last_active'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sess['ip'] = '127.0.0.1'

def test_sqli_in_login_username(client, db):
    payloads = ["' OR '1'='1", "'; DROP TABLE users; --", "admin'--"]
    for payload in payloads:
        r = client.post('/login', data={
            'username': payload, 'password': 'anything'
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b'Invalid' in r.data, f"SQLi payload not rejected: {payload}"

def test_sqli_in_transfer_amount(client, app, db, customer_user, customer_account):
    login_as(client, app, customer_user)
    r = client.post(f'/accounts/{customer_account.id}/deposit', data={
        'amount': "1; DROP TABLE transactions;--",
        'nonce': 'sqli-test-nonce'
    }, follow_redirects=True)
    # Should reject with 400/form validation error, not 500
    assert r.status_code != 500
