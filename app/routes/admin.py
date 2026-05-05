from datetime import datetime, timedelta, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.middleware.rbac import require_role
from app.middleware.session_guard import session_guard
from app.repositories.user_repo import UserRepository
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.audit_repo import AuditRepository
from app.services.account_service import AccountService
from app.repositories.account_repo import AccountRepository
from app.services.transaction_service import TransactionService
from app.extensions import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users')
@login_required
@session_guard
@require_role('admin')
def users():
    repo = UserRepository()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
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
    UserRepository().lock_account(user_id, datetime.now(timezone.utc) + timedelta(days=365))
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
    accounts = AccountRepository().find_all()
    account_map = {a.id: a.account_number for a in accounts}
    return render_template('admin/audit_logs.html', logs=logs, account_map=account_map)

@admin_bp.route('/fraud-review')
@login_required
@session_guard
@require_role('manager', 'admin')
def fraud_review():
    flagged = TransactionRepository().find_fraud_flagged()
    accounts = AccountRepository().find_all()
    account_map = {a.id: a.account_number for a in accounts}
    return render_template('admin/fraud_review.html', transactions=flagged, account_map=account_map)

@admin_bp.route('/fraud/<int:txn_id>/approve', methods=['POST'])
@login_required
@session_guard
@require_role('manager', 'admin')
def approve_fraud(txn_id):
    from flask_login import current_user
    try:
        TransactionService().complete_pending(txn_id, current_user.id, request.remote_addr)
        db.session.commit()
        flash('Transaction approved and funds transferred.', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('admin.fraud_review'))

@admin_bp.route('/fraud/<int:txn_id>/reject', methods=['POST'])
@login_required
@session_guard
@require_role('manager', 'admin')
def reject_fraud(txn_id):
    lock_user = request.form.get('lock_user') == '1'
    txn_repo = TransactionRepository()
    txn = txn_repo.find_by_id(txn_id)
    if txn:
        txn_repo.update_status(txn_id, 'failed')
        if lock_user and txn.from_account_id:
            account = AccountRepository().find_by_id(txn.from_account_id)
            if account:
                UserRepository().lock_account(account.user_id,
                                              datetime.now(timezone.utc) + timedelta(days=365))
    db.session.commit()
    msg = 'Transaction rejected and user locked.' if lock_user else 'Transaction rejected.'
    flash(msg, 'warning')
    return redirect(url_for('admin.fraud_review'))

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
