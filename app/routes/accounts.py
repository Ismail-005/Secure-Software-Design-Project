from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.middleware.rbac import require_role
from app.middleware.session_guard import session_guard
from app.services.account_service import AccountService

accounts_bp = Blueprint('accounts', __name__)

@accounts_bp.route('/dashboard')
@login_required
@session_guard
def dashboard():
    svc = AccountService()
    accounts = svc.get_accounts_for_user(current_user.id)
    balances = {a.id: svc.get_balance(a.id) for a in accounts}
    return render_template('accounts/dashboard.html',
                           accounts=accounts, balances=balances)

@accounts_bp.route('/accounts/<int:account_id>')
@login_required
@session_guard
def account_detail(account_id):
    svc = AccountService()
    account = svc.get_account(account_id)
    if not account:
        abort(404)
    if current_user.role.value == 'customer' and account.user_id != current_user.id:
        abort(403)
    from app.repositories.transaction_repo import TransactionRepository
    txns = TransactionRepository().find_by_account(account_id)
    balance = svc.get_balance(account_id)
    return render_template('accounts/detail.html',
                           account=account, balance=balance, transactions=txns)
