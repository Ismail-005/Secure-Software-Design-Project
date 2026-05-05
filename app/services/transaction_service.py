from decimal import Decimal

from app.models import Transaction
from app.repositories.account_repo import AccountRepository
from app.repositories.transaction_repo import TransactionRepository
from app.services.audit_service import AuditService
from app.services.fraud_service import FraudService

class TransactionService:
    def __init__(self):
        self._accounts = AccountRepository()
        self._txns = TransactionRepository()
        self._audit = AuditService()
        self._fraud = FraudService()

    def _check_nonce(self, nonce: str) -> None:
        if self._txns.nonce_exists(nonce):
            raise ValueError('Duplicate transaction nonce — replay attack detected.')

    def deposit(self, account_id: int, amount: Decimal, nonce: str,  # pylint: disable=too-many-arguments
                user_id: int, ip: str) -> Transaction:
        self._check_nonce(nonce)
        txn = self._txns.create(nonce, None, account_id, 'deposit', amount)
        self._accounts.create_ledger_entry(account_id, txn.id, 'CREDIT', amount)
        self._txns.update_status(txn.id, 'completed')
        self._audit.log(user_id, 'DEPOSIT', ip, {'account_id': account_id,
                                                   'amount': str(amount)})
        return txn

    def withdraw(self, account_id: int, amount: Decimal, nonce: str,  # pylint: disable=too-many-arguments
                 user_id: int, ip: str) -> Transaction:
        self._check_nonce(nonce)
        balance = self._accounts.get_balance(account_id)
        if balance < amount:
            raise ValueError('Insufficient funds.')
        txn = self._txns.create(nonce, account_id, None, 'withdrawal', amount)
        self._accounts.create_ledger_entry(account_id, txn.id, 'DEBIT', amount)
        self._txns.update_status(txn.id, 'completed')
        self._audit.log(user_id, 'WITHDRAWAL', ip, {'account_id': account_id,
                                                      'amount': str(amount)})
        return txn

    def transfer(self, from_account_id: int, to_account_id: int,  # pylint: disable=too-many-arguments
                 amount: Decimal, nonce: str, user_id: int, ip: str) -> Transaction:
        self._check_nonce(nonce)
        balance = self._accounts.get_balance(from_account_id)
        if balance < amount:
            raise ValueError('Insufficient funds.')

        from_account = self._accounts.find_by_id(from_account_id)
        to_account = self._accounts.find_by_id(to_account_id)
        txn = self._txns.create(nonce, from_account_id, to_account_id,
                                'transfer', amount)

        fraud_flag = self._fraud.evaluate(txn, from_account)
        if fraud_flag:
            self._txns.update_fraud_flag(txn.id, True)
            self._audit.log(user_id, 'TRANSFER_HELD', ip, {
                'from': from_account.account_number,
                'to': to_account.account_number,
                'amount': str(amount),
            })
            return txn

        self._accounts.create_ledger_entry(from_account_id, txn.id, 'DEBIT', amount)
        self._accounts.create_ledger_entry(to_account_id, txn.id, 'CREDIT', amount)
        self._txns.update_status(txn.id, 'completed')
        self._audit.log(user_id, 'TRANSFER', ip, {
            'from': from_account.account_number,
            'to': to_account.account_number,
            'amount': str(amount),
        })
        return txn

    def complete_pending(self, txn_id: int, admin_user_id: int, ip: str) -> Transaction:
        txn = self._txns.find_by_id(txn_id)
        if txn is None:
            raise ValueError('Transaction not found.')
        balance = self._accounts.get_balance(txn.from_account_id)
        if balance < txn.amount:
            raise ValueError('Insufficient funds.')
        self._accounts.create_ledger_entry(txn.from_account_id, txn.id, 'DEBIT', txn.amount)
        self._accounts.create_ledger_entry(txn.to_account_id, txn.id, 'CREDIT', txn.amount)
        self._txns.update_status(txn.id, 'completed')
        self._txns.update_fraud_flag(txn.id, False)
        self._audit.log(admin_user_id, 'FRAUD_APPROVED', ip, {
            'txn_id': txn_id, 'amount': str(txn.amount),
        })
        return txn
