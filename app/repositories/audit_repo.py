from app.extensions import db
from app.models.audit_log import AuditLog


class AuditRepository:
    def create(self, user_id: int | None, action: str, ip_address: str | None,  # pylint: disable=too-many-arguments
               details: dict, chain_hash: str) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            details=details,
            chain_hash=chain_hash,
        )
        db.session.add(log)
        db.session.flush()
        return log

    def get_latest_hash(self) -> str:
        latest = AuditLog.query.order_by(AuditLog.id.desc()).first()
        return latest.chain_hash if latest else 'GENESIS'

    def find_all(self, limit: int = 100) -> list[AuditLog]:
        return AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()
