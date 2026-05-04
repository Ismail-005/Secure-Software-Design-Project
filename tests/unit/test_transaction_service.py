import pytest
from decimal import Decimal
from app.services.transaction_service import TransactionService
from app.services.account_service import AccountService

def test_deposit_increases_balance(db, customer_account):
    txn_svc = TransactionService()
    acc_svc = AccountService()
    txn_svc.deposit(customer_account.id, Decimal('500.00'), 'nonce-dep-1',
                    customer_account.user_id, '127.0.0.1')
    db.session.commit()
    assert acc_svc.get_balance(customer_account.id) == Decimal('500.00')
    from app.models import AuditLog
    log = AuditLog.query.filter_by(action='DEPOSIT').one()
    assert log.details['username'] == 'testcustomer'

def test_withdraw_decreases_balance(db, customer_account):
    txn_svc = TransactionService()
    acc_svc = AccountService()
    txn_svc.deposit(customer_account.id, Decimal('500.00'), 'nonce-dep-2',
                    customer_account.user_id, '127.0.0.1')
    txn_svc.withdraw(customer_account.id, Decimal('200.00'), 'nonce-wdw-1',
                     customer_account.user_id, '127.0.0.1')
    db.session.commit()
    assert acc_svc.get_balance(customer_account.id) == Decimal('300.00')
    from app.models import AuditLog
    log = AuditLog.query.filter_by(action='WITHDRAWAL').one()
    assert log.details['username'] == 'testcustomer'

def test_replay_attack_rejected(db, customer_account):
    txn_svc = TransactionService()
    txn_svc.deposit(customer_account.id, Decimal('100.00'), 'nonce-replay-1',
                    customer_account.user_id, '127.0.0.1')
    db.session.commit()
    with pytest.raises(ValueError, match='Duplicate'):
        txn_svc.deposit(customer_account.id, Decimal('100.00'), 'nonce-replay-1',
                        customer_account.user_id, '127.0.0.1')

def test_transfer_moves_funds(db, customer_user, customer_account):
    from datetime import datetime, timedelta
    from app.services.account_service import AccountService
    acc_svc = AccountService()
    txn_svc = TransactionService()
    # backdate account so it passes the new-account fraud rule
    customer_account.created_at = datetime.utcnow() - timedelta(days=2)
    to_account = acc_svc.create_account(customer_user.id, 'checking')
    db.session.commit()
    txn_svc.deposit(customer_account.id, Decimal('1000.00'), 'nonce-fund-1',
                    customer_user.id, '127.0.0.1')
    txn_svc.transfer(customer_account.id, to_account.id, Decimal('400.00'),
                     'nonce-xfer-1', customer_user.id, '127.0.0.1')
    db.session.commit()
    assert acc_svc.get_balance(customer_account.id) == Decimal('600.00')
    assert acc_svc.get_balance(to_account.id) == Decimal('400.00')

def test_insufficient_funds_rejected(db, customer_account):
    txn_svc = TransactionService()
    with pytest.raises(ValueError, match='Insufficient'):
        txn_svc.withdraw(customer_account.id, Decimal('999.00'), 'nonce-insuf-1',
                         customer_account.user_id, '127.0.0.1')
