import enum
from datetime import datetime
from app.extensions import db

class TransactionType(enum.Enum):
    transfer = 'transfer'
    deposit = 'deposit'
    withdrawal = 'withdrawal'

class TransactionStatus(enum.Enum):
    pending = 'pending'
    completed = 'completed'
    failed = 'failed'

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    nonce = db.Column(db.String(64), unique=True, nullable=False)
    from_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    to_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.Enum(TransactionStatus), nullable=False,
                       default=TransactionStatus.pending)
    fraud_flagged = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    ledger_entries = db.relationship('LedgerEntry', backref='transaction', lazy=True)
