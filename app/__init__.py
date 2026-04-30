from flask import Flask
from .extensions import db, migrate, csrf, login_manager, sess
from .config import config, is_placeholder_secret

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    if not app.config.get('TESTING') and is_placeholder_secret(app.config.get('SECRET_KEY')):
        raise RuntimeError(
            'SECRET_KEY must be set to a non-placeholder value before starting the application.'
        )

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    sess.init_app(app)

    login_manager.login_view = 'auth.login'

    from .models import User
    from .extensions import db as _db

    @login_manager.user_loader
    def load_user(user_id):
        return _db.session.get(User, int(user_id))

    from .routes.auth import auth_bp
    from .routes.accounts import accounts_bp
    from .routes.transactions import transactions_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
