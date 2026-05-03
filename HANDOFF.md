# SCBS Handoff

## Current State

SCBS is a Flask-based secure core banking coursework project. It currently uses SQLite, role-based access control, demo OTP verification, ledger-backed account balances, fraud review, audit logging, and a custom internal-dashboard frontend.

The frontend has been redesigned around `DESIGN.md`:

- Warm neutral light theme.
- Dark theme support.
- Left navigation for authenticated users.
- Proper sign-in page.
- Customer sign-up page.
- MFA verification page.
- Styled account, transaction, fraud, audit, and admin screens.

## Important Commands

Install dependencies after activating the virtual environment:

```powershell
pip install -r requirements.txt
```

Apply migrations:

```powershell
flask --app run.py db upgrade
```

Seed demo users:

```powershell
python -m app.seed
```

Run the app:

```powershell
flask --app run.py run
```

Run tests:

```powershell
.\venv\Scripts\python -m pytest tests -v
```

Use the explicit venv Python for tests. Plain `pytest` may resolve to Anaconda on this machine and fail with missing dependencies.

## Main Routes

- `/` redirects to `/signin`.
- `/login` loads the same sign-in flow.
- `/signin` loads the sign-in flow.
- `/signup` creates a customer account and initial savings account.
- `/mfa/verify` verifies the current login attempt.
- `/dashboard` shows the user's accounts.
- `/accounts/<id>` shows account detail and transaction history.
- `/accounts/<id>/deposit` posts a deposit.
- `/accounts/<id>/withdraw` posts a withdrawal.
- `/accounts/<id>/transfer` initiates a transfer.
- `/admin/accounts` shows institution-wide accounts for staff roles.
- `/admin/users` manages users for admins.
- `/admin/audit-logs` shows audit logs for manager/admin roles.
- `/admin/fraud-review` shows fraud-flagged transactions for manager/admin roles.

## Demo Users

After running the seed command:

- Admin: `admin / Admin1234!`
- Customer: `alice / Customer1!`

## Environment

Expected local `.env` values:

```env
SECRET_KEY=<strong-random-secret>
DATABASE_URL=sqlite:///scbs.db
TEST_DATABASE_URL=sqlite:///scbs_test.db
TEST_SECRET_KEY=test-secret-key
SESSION_TYPE=filesystem
OTP_EXPIRY_SECONDS=300
DEMO_SHOW_OTP=true
RATE_LIMIT_WINDOW=60
RATE_LIMIT_MAX=5
FRAUD_TRANSFER_THRESHOLD=10000
FRAUD_TXN_HOURLY_LIMIT=5
```

`DEMO_SHOW_OTP=true` makes the MFA screen display the current OTP for coursework/demo use. This is not real MFA because the same app displays the code.

## Security Notes

Implemented protections:

- bcrypt password hashing.
- CSRF protection through Flask-WTF.
- Role-based access checks.
- Session timeout and IP binding.
- Rate limiting.
- Account lockout after failed logins.
- Replay protection through transaction nonces.
- SQLAlchemy parameterized queries.
- Jinja auto-escaping.
- HMAC-backed audit log hash chain.
- Startup rejection for missing or placeholder `SECRET_KEY`.
- Flask debug mode is not forced on.

Known non-production limitation:

- OTP delivery is demo-only and displayed in-app when `DEMO_SHOW_OTP=true`.

## Recent Verification

The latest full test run passed:

```text
59 passed
```

Warnings remain around `datetime.utcnow()` deprecations and Flask-Session filesystem backend deprecation. They do not block the coursework demo, but they are good cleanup targets.

## Good Next Steps

- Replace `datetime.utcnow()` with timezone-aware UTC timestamps.
- Move Flask-Session away from the deprecated filesystem backend.
- Add a production MFA option if this ever moves beyond coursework.
- Add browser-level visual QA for the redesigned UI.
- Review migration history and generated SQLite files before submitting or sharing the repo.

