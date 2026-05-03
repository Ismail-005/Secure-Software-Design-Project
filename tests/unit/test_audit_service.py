import pytest
from app.services.audit_service import AuditService

def test_log_creates_entry(db, customer_user):
    svc = AuditService()
    svc.log(customer_user.id, 'LOGIN_SUCCESS', '127.0.0.1', {'username': 'testcustomer'})
    db.session.commit()
    from app.models import AuditLog
    logs = AuditLog.query.all()
    assert len(logs) == 1
    assert logs[0].action == 'LOGIN_SUCCESS'

def test_chain_hash_changes_each_entry(db, customer_user):
    svc = AuditService()
    svc.log(customer_user.id, 'LOGIN_SUCCESS', '127.0.0.1', {})
    db.session.commit()
    svc.log(customer_user.id, 'TRANSFER', '127.0.0.1', {'amount': 100})
    db.session.commit()
    from app.models import AuditLog
    logs = AuditLog.query.order_by(AuditLog.id).all()
    assert logs[0].chain_hash != logs[1].chain_hash

def test_verify_chain_passes_on_untampered(db, customer_user):
    svc = AuditService()
    svc.log(customer_user.id, 'LOGIN_SUCCESS', '127.0.0.1', {})
    svc.log(customer_user.id, 'TRANSFER', '127.0.0.1', {'amount': 50})
    db.session.commit()
    assert svc.verify_chain() is True
