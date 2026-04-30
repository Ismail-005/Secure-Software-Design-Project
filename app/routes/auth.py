import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from app.services.auth_service import AuthService
from app.repositories.user_repo import UserRepository
from app.extensions import db

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])

class MFAForm(FlaskForm):
    otp = StringField(validators=[DataRequired()])

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('accounts.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        svc = AuthService()
        ok, msg, user_id = svc.attempt_login(
            form.username.data, form.password.data, request.remote_addr
        )
        db.session.commit()
        if ok:
            svc.create_otp_for_user(user_id)
            db.session.commit()
            session['pending_user_id'] = user_id
            flash('OTP sent. Enter it below.', 'info')
            return redirect(url_for('auth.mfa_verify'))
        flash(msg, 'error')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/mfa/verify', methods=['GET', 'POST'])
def mfa_verify():
    user_id = session.get('pending_user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    form = MFAForm()
    if form.validate_on_submit():
        svc = AuthService()
        if svc.verify_otp(user_id, form.otp.data):
            db.session.commit()
            repo = UserRepository()
            user = repo.find_by_id(user_id)
            login_user(user)
            session.pop('pending_user_id', None)
            session['ip'] = request.remote_addr
            session['last_active'] = __import__('datetime').datetime.utcnow().isoformat()
            return redirect(url_for('accounts.dashboard'))
        flash('Invalid or expired OTP.', 'error')
    return render_template('auth/mfa.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))
