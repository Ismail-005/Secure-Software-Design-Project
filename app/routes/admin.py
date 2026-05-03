from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.middleware.rbac import require_role
from app.middleware.session_guard import session_guard
from app.repositories.user_repo import UserRepository
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.audit_repo import AuditRepository
from app.services.account_service import AccountService
from app.extensions import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users')
@login_required
@session_guard
@require_role('admin')
def users():
    repo = UserRepository()
    now = datetime.utcnow()
    if repo.clear_expired_locks(now):
        db.session.commit()
    all_users = repo.find_all()
    return render_template('admin/users.html', users=all_users, now=now)

@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
@session_guard
@require_role('admin')
def update_role(user_id):
    new_role = request.form.get('role')
    valid_roles = ('customer', 'teller', 'manager', 'admin')
    if new_role not in valid_roles:
        flash('Invalid role.', 'error')
        return redirect(url_for('admin.users'))
    UserRepository().update_role(user_id, new_role)
    db.session.commit()
    flash('Role updated.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/lock', methods=['POST'])
@login_required
@session_guard
@require_role('admin', 'manager')
def lock_user(user_id):
    UserRepository().lock_account(user_id, datetime.utcnow() + timedelta(days=365))
    db.session.commit()
    flash('User locked.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/unlock', methods=['POST'])
@login_required
@session_guard
@require_role('admin', 'manager')
def unlock_user(user_id):
    UserRepository().unlock_account(user_id)
    db.session.commit()
    flash('User unlocked.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/audit-logs')
@login_required
@session_guard
@require_role('admin', 'manager')
def audit_logs():
    logs = AuditRepository().find_all(limit=200)
    return render_template('admin/audit_logs.html', logs=logs)

@admin_bp.route('/fraud-review')
@login_required
@session_guard
@require_role('manager', 'admin')
def fraud_review():
    flagged = TransactionRepository().find_fraud_flagged()
    return render_template('admin/fraud_review.html', transactions=flagged)

@admin_bp.route('/accounts')
@login_required
@session_guard
@require_role('teller', 'manager', 'admin')
def all_accounts():
    from app.repositories.account_repo import AccountRepository
    accounts = AccountRepository().find_all()
    svc = AccountService()
    balances = {a.id: svc.get_balance(a.id) for a in accounts}
    return render_template('accounts/dashboard.html', accounts=accounts, balances=balances)
