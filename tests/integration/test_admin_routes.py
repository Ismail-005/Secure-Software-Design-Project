import datetime
import pytest
from decimal import Decimal
from app.models import Account, AccountType, Transaction, TransactionType, TransactionStatus
from app.models.ledger_entry import LedgerEntry, EntryType


def login_as(client, user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
        sess['last_active'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sess['ip'] = '127.0.0.1'


def _fund_account(db, account, amount, nonce):
    txn = Transaction(
        nonce=nonce,
        from_account_id=None,
        to_account_id=account.id,
        transaction_type=TransactionType.deposit,
        amount=amount,
        status=TransactionStatus.completed,
    )
    db.session.add(txn)
    db.session.flush()
    db.session.add(LedgerEntry(
        account_id=account.id,
        transaction_id=txn.id,
        entry_type=EntryType.CREDIT,
        amount=amount,
    ))
    db.session.flush()


def _make_fraud_txn(db, from_account, to_account, nonce):
    txn = Transaction(
        nonce=nonce,
        from_account_id=from_account.id,
        to_account_id=to_account.id,
        transaction_type=TransactionType.transfer,
        amount=Decimal('100'),
        status=TransactionStatus.pending,
        fraud_flagged=True,
    )
    db.session.add(txn)
    db.session.commit()
    return txn


# ── /admin/users ──────────────────────────────────────────────────────────────

def test_admin_users_page_loads(client, db, admin_user):
    login_as(client, admin_user)
    r = client.get('/admin/users')
    assert r.status_code == 200

def test_customer_forbidden_from_users_page(client, db, customer_user):
    login_as(client, customer_user)
    r = client.get('/admin/users')
    assert r.status_code == 403


# ── /admin/users/<id>/role ────────────────────────────────────────────────────

def test_update_role_valid(client, db, admin_user, customer_user):
    login_as(client, admin_user)
    r = client.post(f'/admin/users/{customer_user.id}/role',
                    data={'role': 'teller'}, follow_redirects=False)
    assert r.status_code == 302
    db.session.refresh(customer_user)
    from app.models import UserRole
    assert customer_user.role == UserRole.teller

def test_update_role_invalid_flashes_error(client, db, admin_user, customer_user):
    login_as(client, admin_user)
    r = client.post(f'/admin/users/{customer_user.id}/role',
                    data={'role': 'superuser'}, follow_redirects=True)
    assert r.status_code == 200
    assert b'Invalid role' in r.data


# ── /admin/users/<id>/lock ────────────────────────────────────────────────────

def test_lock_user(client, db, admin_user, customer_user):
    login_as(client, admin_user)
    r = client.post(f'/admin/users/{customer_user.id}/lock', follow_redirects=False)
    assert r.status_code == 302
    db.session.refresh(customer_user)
    assert customer_user.locked_until is not None


# ── /admin/audit-logs ─────────────────────────────────────────────────────────

def test_audit_logs_loads_for_manager(client, db, manager_user):
    login_as(client, manager_user)
    r = client.get('/admin/audit-logs')
    assert r.status_code == 200


# ── /admin/fraud-review ───────────────────────────────────────────────────────

def test_fraud_review_page_loads(client, db, admin_user):
    login_as(client, admin_user)
    r = client.get('/admin/fraud-review')
    assert r.status_code == 200


# ── /admin/fraud/<id>/approve ─────────────────────────────────────────────────

def test_approve_fraud_success(client, db, admin_user, customer_user, customer_account):
    dest = Account(user_id=admin_user.id, account_type=AccountType.savings)
    db.session.add(dest)
    db.session.flush()
    _fund_account(db, customer_account, Decimal('500'), 'fund-approve-1')
    fraud_txn = _make_fraud_txn(db, customer_account, dest, 'approve-fraud-1')

    login_as(client, admin_user)
    r = client.post(f'/admin/fraud/{fraud_txn.id}/approve', follow_redirects=True)
    assert r.status_code == 200
    assert b'approved' in r.data.lower()

def test_approve_fraud_not_found_flashes_error(client, db, admin_user):
    login_as(client, admin_user)
    r = client.post('/admin/fraud/99999/approve', follow_redirects=True)
    assert r.status_code == 200
    assert b'not found' in r.data.lower()


# ── /admin/fraud/<id>/reject ──────────────────────────────────────────────────

def test_reject_fraud_marks_failed(client, db, admin_user, customer_user, customer_account):
    dest = Account(user_id=admin_user.id, account_type=AccountType.savings)
    db.session.add(dest)
    db.session.flush()
    fraud_txn = _make_fraud_txn(db, customer_account, dest, 'reject-fraud-1')

    login_as(client, admin_user)
    r = client.post(f'/admin/fraud/{fraud_txn.id}/reject',
                    data={'lock_user': '0'}, follow_redirects=True)
    assert r.status_code == 200
    assert b'rejected' in r.data.lower()
    db.session.refresh(fraud_txn)
    assert fraud_txn.status == TransactionStatus.failed

def test_reject_fraud_with_lock_locks_user(client, db, admin_user, customer_user, customer_account):
    dest = Account(user_id=admin_user.id, account_type=AccountType.savings)
    db.session.add(dest)
    db.session.flush()
    fraud_txn = _make_fraud_txn(db, customer_account, dest, 'reject-fraud-lock-1')

    login_as(client, admin_user)
    r = client.post(f'/admin/fraud/{fraud_txn.id}/reject',
                    data={'lock_user': '1'}, follow_redirects=True)
    assert r.status_code == 200
    db.session.refresh(customer_user)
    assert customer_user.locked_until is not None

def test_reject_fraud_nonexistent_txn_does_not_crash(client, db, admin_user):
    login_as(client, admin_user)
    r = client.post('/admin/fraud/99999/reject',
                    data={'lock_user': '0'}, follow_redirects=False)
    assert r.status_code == 302


# ── /admin/accounts ───────────────────────────────────────────────────────────

def test_all_accounts_loads(client, db, admin_user, customer_account):
    login_as(client, admin_user)
    r = client.get('/admin/accounts')
    assert r.status_code == 200
