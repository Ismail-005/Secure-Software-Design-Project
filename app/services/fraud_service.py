from datetime import datetime, timedelta, timezone
from decimal import Decimal

from flask import current_app

from app.models import Transaction, TransactionType, Account
from app.repositories.transaction_repo import TransactionRepository

class FraudService:
    def __init__(self):
        self._txns = TransactionRepository()

    def evaluate(self, txn: Transaction, from_account: Account) -> bool:
        threshold = Decimal(str(current_app.config['FRAUD_TRANSFER_THRESHOLD']))
        hourly_limit = current_app.config['FRAUD_TXN_HOURLY_LIMIT']

        if txn.amount > threshold:
            return True

        created_at = from_account.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - created_at
        if age < timedelta(hours=24) and txn.transaction_type == TransactionType.transfer:
            return True

        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_count = self._txns.count_recent_by_account(
            txn.from_account_id, one_hour_ago
        )
        if recent_count >= hourly_limit:
            return True

        return False
