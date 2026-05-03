from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp
from app.services.account_service import AccountService
from app.services.auth_service import AuthService
from app.repositories.user_repo import UserRepository
from app.extensions import db

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])

class SignupForm(FlaskForm):
    username = StringField(validators=[
        DataRequired(),
        Length(min=3, max=80),
        Regexp(r'^[A-Za-z0-9_.-]+$', message='Use letters, numbers, dots, dashes, or underscores.'),
    ])
    email = StringField(validators=[
        DataRequired(),
        Length(max=120),
        Regexp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', message='Enter a valid email address.'),
    ])
    password = PasswordField(validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.'),
    ])

class MFAForm(FlaskForm):
    otp = StringField(validators=[DataRequired()])

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('accounts.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
@auth_bp.route('/signin', methods=['GET', 'POST'])
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
            plaintext_otp = svc.create_otp_for_user(user_id)
            db.session.commit()
            session['pending_user_id'] = user_id
            if current_app.config.get('DEMO_SHOW_OTP'):
                session['demo_otp'] = plaintext_otp
                flash('Verification code generated. Demo mode is showing it below.', 'info')
            else:
                session.pop('demo_otp', None)
                flash('Verification code generated for this login attempt.', 'info')
            return redirect(url_for('auth.mfa_verify'))
        flash(msg, 'error')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('accounts.dashboard'))
    form = SignupForm()
    if form.validate_on_submit():
        users = UserRepository()
        username = form.username.data.strip()
        email = form.email.data.strip().lower()

        if users.find_by_username(username):
            flash('Username is already registered.', 'error')
            return render_template('auth/signup.html', form=form)
        if users.find_by_email(email):
            flash('Email is already registered.', 'error')
            return render_template('auth/signup.html', form=form)

        auth = AuthService()
        user = users.create(username, email, auth.hash_password(form.password.data), 'customer')
        AccountService().create_account(user.id, 'savings')
        db.session.commit()
        flash('Customer profile created. Sign in to continue.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/signup.html', form=form)

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
            session.pop('demo_otp', None)
            session['ip'] = request.remote_addr
            session['last_active'] = __import__('datetime').datetime.utcnow().isoformat()
            return redirect(url_for('accounts.dashboard'))
        flash('Invalid or expired OTP.', 'error')
    return render_template(
        'auth/mfa.html',
        form=form,
        demo_show_otp=current_app.config.get('DEMO_SHOW_OTP', False),
        demo_otp=session.get('demo_otp'),
    )

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))
