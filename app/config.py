import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = os.environ.get('SESSION_TYPE', 'filesystem')
    SESSION_PERMANENT = False
    WTF_CSRF_ENABLED = True
    OTP_EXPIRY_SECONDS = int(os.environ.get('OTP_EXPIRY_SECONDS', 300))
    RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', 60))
    RATE_LIMIT_MAX = int(os.environ.get('RATE_LIMIT_MAX', 5))
    FRAUD_TRANSFER_THRESHOLD = int(os.environ.get('FRAUD_TRANSFER_THRESHOLD', 10000))
    FRAUD_TXN_HOURLY_LIMIT = int(os.environ.get('FRAUD_TXN_HOURLY_LIMIT', 5))

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', 'postgresql://postgres:password@localhost/scbs_test'
    )
    WTF_CSRF_ENABLED = False
    SESSION_TYPE = 'filesystem'

config = {
    'default': Config,
    'testing': TestingConfig,
}
