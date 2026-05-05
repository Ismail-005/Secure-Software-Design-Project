from datetime import datetime
from decimal import Decimal
from app.extensions import db
from app.models.transaction import Transaction, TransactionType, TransactionStatus

class TransactionRepository:
    def create(self, nonce: str, from_account_id: int | None,  # pylint: disable=too-many-arguments
               to_account_id: int | None, transaction_type: str,
               amount: Decimal) -> Transaction:
        txn = Transaction(
            nonce=nonce,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            transaction_type=TransactionType[transaction_type],
            amount=amount,
        )
        db.session.add(txn)
        db.session.flush()
        return txn

    def find_by_id(self, txn_id: int) -> Transaction | None:
        return db.session.get(Transaction, txn_id)

    def find_by_account(self, account_id: int) -> list[Transaction]:
        return Transaction.query.filter(
            (Transaction.from_account_id == account_id) |
            (Transaction.to_account_id == account_id)
        ).order_by(Transaction.created_at.desc()).all()

    def nonce_exists(self, nonce: str) -> bool:
        return Transaction.query.filter_by(nonce=nonce).first() is not None

    def count_recent_by_account(self, account_id: int, since: datetime) -> int:
        return Transaction.query.filter(
            (Transaction.from_account_id == account_id) |
            (Transaction.to_account_id == account_id),
            Transaction.created_at >= since,
        ).count()

    def update_status(self, txn_id: int, status: str) -> None:
        Transaction.query.filter_by(id=txn_id).update(
            {'status': TransactionStatus[status]}
        )

    def update_fraud_flag(self, txn_id: int, flagged: bool) -> None:
        Transaction.query.filter_by(id=txn_id).update({'fraud_flagged': flagged})

    def find_fraud_flagged(self) -> list[Transaction]:
        return Transaction.query.filter_by(
            fraud_flagged=True, status=TransactionStatus.pending
        ).order_by(Transaction.created_at.desc()).all()
