import enum
from datetime import datetime
from app.extensions import db

class EntryType(enum.Enum):
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'

class LedgerEntry(db.Model):
    __tablename__ = 'ledger_entries'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    entry_type = db.Column(db.Enum(EntryType), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
