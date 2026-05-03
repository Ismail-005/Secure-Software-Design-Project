import pytest
from decimal import Decimal
from app.services.transaction_service import TransactionService
from app.services.account_service import AccountService

def test_replay_attack_rejected_on_deposit(db, customer_account):
    txn_svc = TransactionService()
    acc_svc = AccountService()
    txn_svc.deposit(customer_account.id, Decimal('100'), 'replay-nonce-unique-1',
                    customer_account.user_id, '127.0.0.1')
    db.session.commit()
    with pytest.raises(ValueError, match='Duplicate'):
        txn_svc.deposit(customer_account.id, Decimal('100'), 'replay-nonce-unique-1',
                        customer_account.user_id, '127.0.0.1')

def test_replay_attack_rejected_on_transfer(db, customer_user, customer_account):
    acc_svc = AccountService()
    txn_svc = TransactionService()
    to_account = acc_svc.create_account(customer_user.id, 'checking')
    db.session.commit()
    txn_svc.deposit(customer_account.id, Decimal('500'), 'replay-fund-nonce-1',
                    customer_user.id, '127.0.0.1')
    txn_svc.transfer(customer_account.id, to_account.id, Decimal('100'),
                     'replay-xfer-nonce-1', customer_user.id, '127.0.0.1')
    db.session.commit()
    with pytest.raises(ValueError, match='Duplicate'):
        txn_svc.transfer(customer_account.id, to_account.id, Decimal('100'),
                         'replay-xfer-nonce-1', customer_user.id, '127.0.0.1')
