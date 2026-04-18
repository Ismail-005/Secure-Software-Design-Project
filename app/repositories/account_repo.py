from decimal import Decimal
from sqlalchemy import text
from app.extensions import db
from app.models.account import Account, AccountType, AccountStatus
from app.models.ledger_entry import LedgerEntry, EntryType

class AccountRepository:
    def find_by_id(self, account_id: int) -> Account | None:
        return db.session.get(Account, account_id)

    def find_by_account_number(self, number: str) -> Account | None:
        return Account.query.filter_by(account_number=number).first()

    def find_by_user_id(self, user_id: int) -> list[Account]:
        return Account.query.filter_by(user_id=user_id).all()

    def find_all(self) -> list[Account]:
        return Account.query.all()

    def create(self, user_id: int, account_type: str) -> Account:
        account = Account(user_id=user_id, account_type=AccountType[account_type])
        db.session.add(account)
        db.session.flush()
        return account

    def update_status(self, account_id: int, status: str) -> None:
        Account.query.filter_by(id=account_id).update(
            {'status': AccountStatus[status]}
        )

    def get_balance(self, account_id: int) -> Decimal:
        result = db.session.execute(
            text("""
                SELECT COALESCE(SUM(
                    CASE WHEN entry_type = 'CREDIT' THEN amount ELSE -amount END
                ), 0)
                FROM ledger_entries WHERE account_id = :account_id
            """),
            {'account_id': account_id}
        ).scalar()
        return Decimal(str(result))

    def create_ledger_entry(self, account_id: int, transaction_id: int,
                            entry_type: str, amount: Decimal) -> LedgerEntry:
        entry = LedgerEntry(
            account_id=account_id,
            transaction_id=transaction_id,
            entry_type=EntryType[entry_type],
            amount=amount,
        )
        db.session.add(entry)
        db.session.flush()
        return entry
