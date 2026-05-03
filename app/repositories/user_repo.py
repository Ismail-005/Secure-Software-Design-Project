from datetime import datetime
from app.extensions import db
from app.models.user import User, UserRole
from app.models.otp_token import OTPToken

class UserRepository:
    def find_by_username(self, username: str) -> User | None:
        return User.query.filter_by(username=username).first()

    def find_by_email(self, email: str) -> User | None:
        return User.query.filter_by(email=email).first()

    def find_by_id(self, user_id: int) -> User | None:
        return db.session.get(User, user_id)

    def find_all(self) -> list[User]:
        return User.query.all()

    def create(self, username: str, email: str, password_hash: str, role: str) -> User:
        user = User(username=username, email=email,
                    password_hash=password_hash, role=UserRole[role])
        db.session.add(user)
        db.session.flush()
        return user

    def increment_failed_logins(self, user_id: int) -> None:
        User.query.filter_by(id=user_id).update(
            {'failed_login_attempts': User.failed_login_attempts + 1}
        )

    def lock_account(self, user_id: int, until: datetime) -> None:
        User.query.filter_by(id=user_id).update({'locked_until': until})

    def unlock_account(self, user_id: int) -> None:
        User.query.filter_by(id=user_id).update(
            {'failed_login_attempts': 0, 'locked_until': None}
        )

    def clear_expired_locks(self, now: datetime) -> int:
        return User.query.filter(User.locked_until <= now).update(
            {'failed_login_attempts': 0, 'locked_until': None}
        )

    def reset_failed_logins(self, user_id: int) -> None:
        User.query.filter_by(id=user_id).update(
            {'failed_login_attempts': 0, 'locked_until': None}
        )

    def update_role(self, user_id: int, role: str) -> None:
        User.query.filter_by(id=user_id).update({'role': UserRole[role]})

    def create_otp(self, user_id: int, token_hash: str, expires_at: datetime) -> OTPToken:
        otp = OTPToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        db.session.add(otp)
        db.session.flush()
        return otp

    def find_valid_otp(self, user_id: int) -> OTPToken | None:
        return OTPToken.query.filter_by(user_id=user_id, used=False).filter(
            OTPToken.expires_at > datetime.utcnow()
        ).first()

    def mark_otp_used(self, otp_id: int) -> None:
        OTPToken.query.filter_by(id=otp_id).update({'used': True})
