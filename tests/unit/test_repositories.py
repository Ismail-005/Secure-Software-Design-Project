import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app.repositories.user_repo import UserRepository
from app.repositories.account_repo import AccountRepository
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.audit_repo import AuditRepository
from app.models import User, UserRole, Account, AccountType

# --- UserRepository ---

def test_create_and_find_user(db):
    repo = UserRepository()
    user = repo.create('bob', 'bob@test.com', 'hash123', 'customer')
    db.session.commit()
    found = repo.find_by_username('bob')
    assert found is not None
    assert found.role == UserRole.customer

def test_find_by_id(db):
    repo = UserRepository()
    user = repo.create('carol', 'carol@test.com', 'hash456', 'teller')
    db.session.commit()
    found = repo.find_by_id(user.id)
    assert found.username == 'carol'

def test_increment_failed_logins(db):
    repo = UserRepository()
    user = repo.create('dave', 'dave@test.com', 'hash', 'customer')
    db.session.commit()
    repo.increment_failed_logins(user.id)
    db.session.commit()
    db.session.refresh(user)
    assert user.failed_login_attempts == 1

def test_lock_and_reset_account(db):
    repo = UserRepository()
    user = repo.create('eve', 'eve@test.com', 'hash', 'customer')
    db.session.commit()
    until = datetime.utcnow() + timedelta(minutes=30)
    repo.lock_account(user.id, until)
    db.session.commit()
    db.session.refresh(user)
    assert user.locked_until is not None
    repo.reset_failed_logins(user.id)
    db.session.commit()
    db.session.refresh(user)
    assert user.failed_login_attempts == 0
    assert user.locked_until is None

# --- AccountRepository ---

def test_create_account_and_get_balance(db, customer_user):
    repo = AccountRepository()
    account = repo.create(customer_user.id, 'savings')
    db.session.commit()
    balance = repo.get_balance(account.id)
    assert balance == Decimal('0')

def test_find_accounts_by_user(db, customer_user):
    repo = AccountRepository()
    repo.create(customer_user.id, 'savings')
    repo.create(customer_user.id, 'checking')
    db.session.commit()
    accounts = repo.find_by_user_id(customer_user.id)
    assert len(accounts) == 2
