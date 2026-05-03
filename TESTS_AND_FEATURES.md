# SCBS Tests And Features

## Test Command

Run the project test suite with the project virtual environment:

```powershell
.\venv\Scripts\python -m pytest tests -v
```

What the command means:

- `.\venv\Scripts\python` uses this project's virtual environment Python.
- `-m pytest` runs the `pytest` test runner as a Python module.
- `tests` tells pytest to run everything inside the `tests/` folder.
- `-v` enables verbose output, so every test name is printed.

Do not rely on plain `pytest` on this machine. It currently resolves to Anaconda's pytest executable, which does not have this project's dependencies installed.

## Test Coverage

The suite is organized into three groups.

### Integration Tests

Integration tests exercise full Flask routes through the test client.

They cover:

- Login page loading.
- `/signin` alias loading.
- `/signup` page loading.
- New customer registration.
- Duplicate username rejection.
- MFA verification page behavior.
- Logout behavior.
- Dashboard login requirements.
- Account dashboard display.
- Deposit route behavior.
- Withdrawal insufficient-funds behavior.

### Security Tests

Security tests verify that common web and banking risks are blocked.

They cover:

- Brute-force login lockout.
- Rate limiting.
- Customer access restrictions on admin pages.
- Unauthenticated dashboard access rejection.
- Admin access to audit logs.
- Replay attack rejection using transaction nonces.
- SQL injection payload handling.
- XSS payload escaping.

### Unit Tests

Unit tests exercise services, repositories, and middleware directly.

They cover:

- Password hashing and verification.
- OTP generation and verification.
- Account creation.
- Balance calculation.
- Account status updates.
- Audit log creation.
- Audit hash-chain verification.
- Fraud detection rules.
- RBAC middleware.
- Rate limiter behavior.
- User repository operations.
- Transaction service deposit, withdrawal, transfer, replay rejection, and insufficient-funds rejection.

## Banking Features

SCBS is a role-based secure core banking dashboard built with Flask, SQLite, SQLAlchemy, Flask-Login, Flask-WTF, and Flask-Migrate.

### Authentication

- Username/password sign-in.
- Password hashing with bcrypt.
- Failed-login tracking.
- Account lockout after repeated failures.
- Demo OTP verification for coursework use.
- Session timeout handling.
- IP-bound session guard.
- Logout clears the session.

### Sign-Up

- Public customer account creation at `/signup`.
- New users are created with the `customer` role only.
- A first savings account is created automatically.
- Staff roles remain administrator-managed.

### Roles

The system supports four roles:

- `customer`
- `teller`
- `manager`
- `admin`

Access model:

- Customers can view their own accounts and perform allowed money movement.
- Tellers, managers, and admins can view broader account data.
- Managers and admins can review fraud and audit logs.
- Admins can manage user roles and account locks.

### Accounts

- Savings and checking account types.
- Account states: active, frozen, closed.
- Customer account dashboard.
- Institution-wide account portfolio for staff roles.
- Account detail screen with current balance and transaction history.

### Transactions

- Deposit.
- Withdrawal.
- Transfer.
- Insufficient-funds protection.
- Replay protection through transaction nonces.
- Transaction status tracking.
- Fraud flagging.

### Ledger

- Balances are calculated from ledger entries.
- The app does not rely on a manually stored balance field.
- Ledger-backed balance calculation makes transaction history the source of truth.

### Fraud Detection

The fraud service checks:

- Large transfers.
- New-account transfer behavior.
- High transaction velocity.

Flagged transactions are visible to manager and admin roles.

### Audit Logging

- Login success and failure events.
- Account lock events.
- Transaction and security events.
- HMAC-backed tamper-evident hash chain.

### Security Protections

- bcrypt password hashing.
- CSRF protection.
- Role-based access control.
- Rate limiting.
- Session timeout.
- IP-bound sessions.
- SQLAlchemy parameterized database access.
- Jinja auto-escaping.
- Transaction replay prevention.
- Placeholder secret key rejection.
- Flask debug mode disabled by default.

### Frontend

- Internal banking dashboard design.
- Sign-in page.
- Create-account page.
- MFA verification page.
- Account dashboard.
- Account detail page.
- Transaction forms.
- Admin user management.
- Fraud review.
- Audit logs.
- Light/dark theme toggle with persisted preference.

## Demo Users

After seeding:

```powershell
python -m app.seed
```

Available users:

- `admin / Admin1234!`
- `alice / Customer1!`

## Demo Summary

For presentation purposes:

> SCBS is a role-based secure banking dashboard with authentication, demo OTP verification, transaction controls, fraud review, audit logging, ledger-backed balance calculation, and automated tests for brute force, access control, replay attacks, SQL injection, and XSS.

