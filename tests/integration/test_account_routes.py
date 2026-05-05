import pytest
from flask_login import login_user

def login_as(client, app, user):
    with app.app_context():
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
            import datetime
            sess['last_active'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            sess['ip'] = '127.0.0.1'

def test_dashboard_requires_login(client):
    r = client.get('/dashboard')
    assert r.status_code == 302

def test_dashboard_shows_accounts(client, app, db, customer_user, customer_account):
    login_as(client, app, customer_user)
    r = client.get('/dashboard')
    assert r.status_code == 200
    assert customer_account.account_number.encode() in r.data

def test_deposit_increases_balance(client, app, db, customer_user, customer_account):
    login_as(client, app, customer_user)
    r = client.post(f'/accounts/{customer_account.id}/deposit', data={
        'amount': '500', 'nonce': 'test-nonce-dep-1'
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b'500' in r.data

def test_withdraw_insufficient_funds(client, app, db, customer_user, customer_account):
    login_as(client, app, customer_user)
    r = client.post(f'/accounts/{customer_account.id}/withdraw', data={
        'amount': '999', 'nonce': 'test-nonce-wdw-1'
    }, follow_redirects=True)
    assert b'Insufficient' in r.data
