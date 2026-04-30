import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PLACEHOLDER_SECRET_KEYS = {
    '',
    'change-me-to-a-random-64-char-string',
    'dev-secret-key-change-me',
    'supersecretkey-change-me-in-production-64-chars-long-random',
}


def _sqlite_url(filename: str) -> str:
    return f"sqlite:///{(BASE_DIR / filename).as_posix()}"


def is_placeholder_secret(secret_key: str | None) -> bool:
    return secret_key is None or secret_key.strip() in PLACEHOLDER_SECRET_KEYS


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', _sqlite_url('scbs.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = os.environ.get('SESSION_TYPE', 'filesystem')
    SESSION_PERMANENT = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    OTP_EXPIRY_SECONDS = int(os.environ.get('OTP_EXPIRY_SECONDS', 300))
    RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', 60))
    RATE_LIMIT_MAX = int(os.environ.get('RATE_LIMIT_MAX', 5))
    FRAUD_TRANSFER_THRESHOLD = int(os.environ.get('FRAUD_TRANSFER_THRESHOLD', 10000))
    FRAUD_TXN_HOURLY_LIMIT = int(os.environ.get('FRAUD_TXN_HOURLY_LIMIT', 5))


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = os.environ.get('TEST_SECRET_KEY', 'test-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', _sqlite_url('scbs_test.db'))
    WTF_CSRF_ENABLED = False
    SESSION_TYPE = 'filesystem'


config = {
    'default': Config,
    'testing': TestingConfig,
}
