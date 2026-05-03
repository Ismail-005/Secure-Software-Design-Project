import enum
from datetime import datetime
from flask_login import UserMixin
from app.extensions import db

class UserRole(enum.Enum):
    customer = 'customer'
    teller = 'teller'
    manager = 'manager'
    admin = 'admin'

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.customer)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    accounts = db.relationship('Account', backref='owner', lazy=True)
    otp_tokens = db.relationship('OTPToken', backref='user', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)
