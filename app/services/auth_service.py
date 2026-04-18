import bcrypt
import random
from datetime import datetime, timedelta
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
        plaintext = f"{random.randint(0, 999999):06d}"
        hashed = bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt()).decode()
        return plaintext, hashed

    def attempt_login(self, username: str, password: str,
                      ip: str) -> tuple[bool, str, int | None]:
        user = self._users.find_by_username(username)
        if not user:
            return False, 'Invalid credentials.', None

        if user.locked_until and user.locked_until > datetime.utcnow():
            return False, 'Account locked. Try again later.', None

        if not self.verify_password(password, user.password_hash):
            self._users.increment_failed_logins(user.id)
            if user.failed_login_attempts + 1 >= 5:
                lock_until = datetime.utcnow() + timedelta(minutes=30)
                self._users.lock_account(user.id, lock_until)
                self._audit.log(user.id, 'ACCOUNT_LOCKED', ip, {})
            else:
                self._audit.log(user.id, 'LOGIN_FAILURE', ip, {})
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
        expiry = datetime.utcnow() + timedelta(
            seconds=current_app.config['OTP_EXPIRY_SECONDS']
        )
        self._users.create_otp(user_id, hashed, expiry)
        return plaintext
