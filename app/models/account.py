import enum
import random
import string
from datetime import datetime
from app.extensions import db

class AccountType(enum.Enum):
    savings = 'savings'
    checking = 'checking'

class AccountStatus(enum.Enum):
    active = 'active'
    frozen = 'frozen'
    closed = 'closed'

def _gen_account_number():
    return ''.join(random.choices(string.digits, k=10))

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False,
                               default=_gen_account_number)
    account_type = db.Column(db.Enum(AccountType), nullable=False)
    status = db.Column(db.Enum(AccountStatus), nullable=False,
                       default=AccountStatus.active)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    ledger_entries = db.relationship('LedgerEntry', backref='account', lazy=True)
