import pytest
from app.services.account_service import AccountService

def test_create_account(db, customer_user):
    svc = AccountService()
    account = svc.create_account(customer_user.id, 'savings')
    db.session.commit()
    assert account.id is not None
    assert account.account_number is not None

def test_get_accounts_for_user(db, customer_user):
    svc = AccountService()
    svc.create_account(customer_user.id, 'savings')
    svc.create_account(customer_user.id, 'checking')
    db.session.commit()
    accounts = svc.get_accounts_for_user(customer_user.id)
    assert len(accounts) == 2

def test_get_balance_zero_on_new_account(db, customer_account):
    svc = AccountService()
    from decimal import Decimal
    balance = svc.get_balance(customer_account.id)
    assert balance == Decimal('0')

def test_freeze_account(db, customer_account):
    svc = AccountService()
    svc.freeze_account(customer_account.id)
    db.session.commit()
    db.session.refresh(customer_account)
    from app.models import AccountStatus
    assert customer_account.status == AccountStatus.frozen
