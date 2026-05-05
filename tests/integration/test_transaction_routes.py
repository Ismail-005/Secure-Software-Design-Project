import datetime
import pytest
from decimal import Decimal
from app.services.transaction_service import TransactionService


def login_as(client, user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
        sess['last_active'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sess['ip'] = '127.0.0.1'


# ── deposit ───────────────────────────────────────────────────────────────────

def test_deposit_get_renders_form(client, db, customer_user, customer_account):
    login_as(client, customer_user)
    r = client.get(f'/accounts/{customer_account.id}/deposit')
    assert r.status_code == 200
    assert b'nonce' in r.data.lower() or b'deposit' in r.data.lower()

def test_deposit_access_denied_for_other_account(client, db, customer_user, other_customer):
    _, other_account = other_customer
    login_as(client, customer_user)
    r = client.post(f'/accounts/{other_account.id}/deposit',
                    data={'amount': '100', 'nonce': 'denied-dep-1'},
                    follow_redirects=False)
    assert r.status_code == 302

def test_deposit_replay_shows_error(client, db, customer_user, customer_account):
    svc = TransactionService()
    svc.deposit(customer_account.id, Decimal('100'), 'dup-nonce-dep-1',
                customer_user.id, '127.0.0.1')
    db.session.commit()

    login_as(client, customer_user)
    r = client.post(f'/accounts/{customer_account.id}/deposit',
                    data={'amount': '100', 'nonce': 'dup-nonce-dep-1'},
                    follow_redirects=True)
    assert r.status_code == 200
    assert b'replay' in r.data.lower() or b'duplicate' in r.data.lower()


# ── withdraw ──────────────────────────────────────────────────────────────────

def test_withdraw_get_renders_form(client, db, customer_user, customer_account):
    login_as(client, customer_user)
    r = client.get(f'/accounts/{customer_account.id}/withdraw')
    assert r.status_code == 200

def test_withdraw_access_denied_for_other_account(client, db, customer_user, other_customer):
    _, other_account = other_customer
    login_as(client, customer_user)
    r = client.post(f'/accounts/{other_account.id}/withdraw',
                    data={'amount': '10', 'nonce': 'denied-wdw-1'},
                    follow_redirects=False)
    assert r.status_code == 302

def test_withdraw_insufficient_funds_shows_error(client, db, customer_user, customer_account):
    login_as(client, customer_user)
    r = client.post(f'/accounts/{customer_account.id}/withdraw',
                    data={'amount': '9999', 'nonce': 'insuf-wdw-route-1'},
                    follow_redirects=True)
    assert r.status_code == 200
    assert b'insufficient' in r.data.lower()


# ── transfer ──────────────────────────────────────────────────────────────────

def test_transfer_get_renders_form(client, db, customer_user, customer_account):
    login_as(client, customer_user)
    r = client.get(f'/accounts/{customer_account.id}/transfer')
    assert r.status_code == 200

def test_transfer_access_denied_for_other_account(client, db, customer_user, other_customer):
    _, other_account = other_customer
    login_as(client, customer_user)
    r = client.post(f'/accounts/{other_account.id}/transfer',
                    data={'amount': '10', 'to_account_number': '0000000000',
                          'nonce': 'denied-xfer-1'},
                    follow_redirects=False)
    assert r.status_code == 302

def test_transfer_destination_not_found(client, db, customer_user, customer_account):
    login_as(client, customer_user)
    r = client.post(f'/accounts/{customer_account.id}/transfer',
                    data={'amount': '10', 'to_account_number': '0000000000',
                          'nonce': 'dest-notfound-1'},
                    follow_redirects=True)
    assert r.status_code == 200
    assert b'not found' in r.data.lower()

def test_transfer_insufficient_funds_shows_error(client, db, customer_user, customer_account,
                                                  other_customer):
    _, other_account = other_customer
    login_as(client, customer_user)
    r = client.post(f'/accounts/{customer_account.id}/transfer',
                    data={'amount': '9999', 'to_account_number': other_account.account_number,
                          'nonce': 'insuf-xfer-route-1'},
                    follow_redirects=True)
    assert r.status_code == 200
    assert b'insufficient' in r.data.lower()
