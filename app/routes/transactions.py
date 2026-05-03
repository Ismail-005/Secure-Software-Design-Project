import uuid
from decimal import Decimal, InvalidOperation
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, HiddenField
from wtforms.validators import DataRequired, NumberRange
from app.middleware.session_guard import session_guard
from app.services.transaction_service import TransactionService
from app.services.account_service import AccountService
from app.extensions import db

transactions_bp = Blueprint('transactions', __name__)

class AmountForm(FlaskForm):
    amount = DecimalField(validators=[DataRequired(), NumberRange(min=0.01)])
    nonce = HiddenField()

class TransferForm(FlaskForm):
    amount = DecimalField(validators=[DataRequired(), NumberRange(min=0.01)])
    to_account_number = StringField(validators=[DataRequired()])
    nonce = HiddenField()

@transactions_bp.route('/accounts/<int:account_id>/deposit', methods=['GET', 'POST'])
@login_required
@session_guard
def deposit(account_id):
    svc = AccountService()
    account = svc.get_account(account_id)
    if not account or account.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('accounts.dashboard'))
    form = AmountForm()
    if not form.nonce.data:
        form.nonce.data = str(uuid.uuid4())
    if form.validate_on_submit():
        try:
            txn_svc = TransactionService()
            txn_svc.deposit(account_id, form.amount.data,
                            form.nonce.data, current_user.id, request.remote_addr)
            db.session.commit()
            flash(f'Deposited PKR {form.amount.data:.2f} successfully.', 'success')
            return redirect(url_for('accounts.account_detail', account_id=account_id))
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'error')
    return render_template('transactions/deposit.html', form=form, account=account)

@transactions_bp.route('/accounts/<int:account_id>/withdraw', methods=['GET', 'POST'])
@login_required
@session_guard
def withdraw(account_id):
    svc = AccountService()
    account = svc.get_account(account_id)
    if not account or account.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('accounts.dashboard'))
    form = AmountForm()
    if not form.nonce.data:
        form.nonce.data = str(uuid.uuid4())
    if form.validate_on_submit():
        try:
            txn_svc = TransactionService()
            txn_svc.withdraw(account_id, form.amount.data,
                             form.nonce.data, current_user.id, request.remote_addr)
            db.session.commit()
            flash(f'Withdrew PKR {form.amount.data:.2f} successfully.', 'success')
            return redirect(url_for('accounts.account_detail', account_id=account_id))
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'error')
    return render_template('transactions/withdraw.html', form=form, account=account)

@transactions_bp.route('/accounts/<int:account_id>/transfer', methods=['GET', 'POST'])
@login_required
@session_guard
def transfer(account_id):
    svc = AccountService()
    account = svc.get_account(account_id)
    if not account or account.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('accounts.dashboard'))
    form = TransferForm()
    if not form.nonce.data:
        form.nonce.data = str(uuid.uuid4())
    if form.validate_on_submit():
        from app.repositories.account_repo import AccountRepository
        to_account = AccountRepository().find_by_account_number(form.to_account_number.data)
        if not to_account:
            flash('Destination account not found.', 'error')
        else:
            try:
                txn_svc = TransactionService()
                txn_svc.transfer(account_id, to_account.id, form.amount.data,
                                 form.nonce.data, current_user.id, request.remote_addr)
                db.session.commit()
                flash(f'Transferred PKR {form.amount.data:.2f} successfully.', 'success')
                return redirect(url_for('accounts.account_detail', account_id=account_id))
            except ValueError as e:
                db.session.rollback()
                flash(str(e), 'error')
    return render_template('transactions/transfer.html', form=form, account=account)
