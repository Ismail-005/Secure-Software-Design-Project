import pytest
from app import create_app
from app.extensions import db as _db
from app.models import User, UserRole, Account, AccountType
import bcrypt

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def customer_user(db):
    pw = bcrypt.hashpw(b'Test1234!', bcrypt.gensalt()).decode()
    user = User(username='testcustomer', email='c@test.com',
                password_hash=pw, role=UserRole.customer)
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def admin_user(db):
    pw = bcrypt.hashpw(b'Admin1234!', bcrypt.gensalt()).decode()
    user = User(username='testadmin', email='a@test.com',
                password_hash=pw, role=UserRole.admin)
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def customer_account(db, customer_user):
    account = Account(user_id=customer_user.id,
                      account_type=AccountType.savings)
    db.session.add(account)
    db.session.commit()
    return account
