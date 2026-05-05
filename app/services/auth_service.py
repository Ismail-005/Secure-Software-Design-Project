import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from flask import current_app

from app.repositories.user_repo import UserRepository
from app.services.audit_service import AuditService

class AuthService:
    def __init__(self):
        self._users = UserRepository()
        self._audit = AuditService()

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    def generate_otp(self) -> tuple[str, str]:
        plaintext = f"{secrets.randbelow(1_000_000):06d}"
        hashed = bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt()).decode()
        return plaintext, hashed

    def _resolve_lock_status(self, user) -> tuple[bool, bool]:
        """Returns (is_currently_locked, lock_has_expired)."""
        locked_until = user.locked_until
        if not locked_until:
            return False, False
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)
        if locked_until > datetime.now(timezone.utc):
            return True, False
        return False, True

    def attempt_login(self, username: str, password: str,
                      ip: str) -> tuple[bool, str, int | None]:
        user = self._users.find_by_username(username)
        if not user:
            self._audit.log(None, 'LOGIN_FAILURE', ip, {'username': username})
            return False, 'Invalid credentials.', None

        is_locked, lock_expired = self._resolve_lock_status(user)
        if is_locked:
            self._audit.log(user.id, 'LOGIN_FAILURE', ip, {
                'username': username, 'reason': 'account_locked',
            })
            return False, 'Account locked. Try again later.', None
        if lock_expired:
            self._users.unlock_account(user.id)
            user.locked_until = None
            user.failed_login_attempts = 0

        if not self.verify_password(password, user.password_hash):
            self._users.increment_failed_logins(user.id)
            if user.failed_login_attempts + 1 >= 5:
                lock_until = datetime.now(timezone.utc) + timedelta(minutes=30)
                self._users.lock_account(user.id, lock_until)
                self._audit.log(user.id, 'ACCOUNT_LOCKED', ip, {'username': username})
            else:
                self._audit.log(user.id, 'LOGIN_FAILURE', ip, {'username': username})
            return False, 'Invalid credentials.', None

        self._audit.log(user.id, 'LOGIN_SUCCESS', ip, {'username': username})
        return True, 'OK', user.id

    def verify_otp(self, user_id: int, otp_plaintext: str) -> bool:
        otp = self._users.find_valid_otp(user_id)
        if not otp:
            return False
        if not bcrypt.checkpw(otp_plaintext.encode(), otp.token_hash.encode()):
            return False
        self._users.mark_otp_used(otp.id)
        self._users.reset_failed_logins(user_id)
        return True

    def create_otp_for_user(self, user_id: int) -> str:
        plaintext, hashed = self.generate_otp()
        expiry = datetime.now(timezone.utc) + timedelta(
            seconds=current_app.config['OTP_EXPIRY_SECONDS']
        )
        self._users.create_otp(user_id, hashed, expiry)
        return plaintext
