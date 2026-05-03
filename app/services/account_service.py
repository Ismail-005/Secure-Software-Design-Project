from decimal import Decimal
from app.repositories.account_repo import AccountRepository
from app.services.audit_service import AuditService
from app.models import Account

class AccountService:
    def __init__(self):
        self._accounts = AccountRepository()
        self._audit = AuditService()

    def create_account(self, user_id: int, account_type: str) -> Account:
        return self._accounts.create(user_id, account_type)

    def get_accounts_for_user(self, user_id: int) -> list[Account]:
        return self._accounts.find_by_user_id(user_id)

    def get_account(self, account_id: int) -> Account | None:
        return self._accounts.find_by_id(account_id)

    def get_balance(self, account_id: int) -> Decimal:
        return self._accounts.get_balance(account_id)

    def freeze_account(self, account_id: int) -> None:
        self._accounts.update_status(account_id, 'frozen')

    def close_account(self, account_id: int) -> None:
        self._accounts.update_status(account_id, 'closed')

    def unfreeze_account(self, account_id: int) -> None:
        self._accounts.update_status(account_id, 'active')
