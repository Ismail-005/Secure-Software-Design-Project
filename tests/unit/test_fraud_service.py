import pytest
from decimal import Decimal
from unittest.mock import MagicMock
from app.services.fraud_service import FraudService
from app.models import Transaction, TransactionType, TransactionStatus, Account

def _mock_txn(amount):
    t = MagicMock(spec=Transaction)
    t.amount = Decimal(str(amount))
    t.transaction_type = TransactionType.transfer
    t.from_account_id = 1
    return t

def _mock_account(created_days_ago=10):
    from datetime import datetime, timedelta, timezone
    a = MagicMock(spec=Account)
    a.created_at = datetime.now(timezone.utc) - timedelta(days=created_days_ago)
    return a

def test_flags_large_transfer(app):
    with app.app_context():
        svc = FraudService()
        txn = _mock_txn(15000)
        account = _mock_account()
        assert svc.evaluate(txn, account) is True

def test_no_flag_on_small_transfer(app):
    with app.app_context():
        svc = FraudService()
        txn = _mock_txn(500)
        account = _mock_account()
        assert svc.evaluate(txn, account) is False

def test_flags_new_account_transfer(app):
    with app.app_context():
        svc = FraudService()
        txn = _mock_txn(100)
        account = _mock_account(created_days_ago=0)
        assert svc.evaluate(txn, account) is True
