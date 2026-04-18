import hmac
import hashlib
import json
from flask import current_app
from app.repositories.audit_repo import AuditRepository
from app.models import AuditLog

class AuditService:
    def __init__(self):
        self._repo = AuditRepository()

    def _compute_hash(self, prev_hash: str, action: str,
                      user_id: int | None, details: dict) -> str:
        secret = current_app.config['SECRET_KEY'].encode()
        payload = f"{prev_hash}|{action}|{user_id}|{json.dumps(details, sort_keys=True)}"
        return hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()

    def log(self, user_id: int | None, action: str,
            ip_address: str | None, details: dict = None) -> None:
        details = details or {}
        prev_hash = self._repo.get_latest_hash()
        chain_hash = self._compute_hash(prev_hash, action, user_id, details)
        self._repo.create(user_id, action, ip_address, details, chain_hash)

    def verify_chain(self) -> bool:
        logs = AuditLog.query.order_by(AuditLog.id).all()
        prev_hash = 'GENESIS'
        for log in logs:
            expected = self._compute_hash(prev_hash, log.action,
                                          log.user_id, log.details or {})
            if expected != log.chain_hash:
                return False
            prev_hash = log.chain_hash
        return True
