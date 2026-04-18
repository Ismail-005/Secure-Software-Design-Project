# Secure Core Banking System (SCBS)

A secure, role-based core banking system built with Python and Flask. This project implements strict security controls, atomic transactions, MFA, fraud detection, and tamper-evident audit logs.

## Features

- **Role-Based Access Control (RBAC):** Supports 4 user roles: Customer, Teller, Manager, and Admin.
- **Secure Authentication:** Passwords hashed with `bcrypt`, combined with simulated Multi-Factor Authentication (OTP).
- **Brute-Force Protection:** Account lockout after 5 failed login attempts.
- **Rate Limiting & Session Management:** Prevents abuse and enforces secure, time-bound, IP-bound sessions.
- **Atomic Transactions:** Ensures secure deposit, withdrawal, and transfer operations.
- **Double-Entry Ledger:** Ensures financial integrity without relying on stored balances.
- **Fraud Detection:** Automatically flags suspicious transactions (e.g., large transfers, new account activity, rapid succession transfers).
- **Tamper-Evident Audit Logs:** Cryptographically linked HMAC hash-chaining ensures logs cannot be silently altered.
- **Security Best Practices:** Parameterized queries (SQLi prevention), Jinja2 auto-escaping (XSS prevention), Nonce-based replay attack prevention.

## Technology Stack

- **Backend:** Python 3.11, Flask
- **Database:** PostgreSQL, SQLAlchemy, psycopg2-binary
- **Extensions:** Flask-WTF, Flask-Login, Flask-Session, Flask-Migrate
- **Security & Testing:** bcrypt, pytest, pytest-flask

## Setup and Running

Please see the [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) file for a step-by-step guide on how to configure your database, initialize the system, and run the server.

## Architecture

The application uses a Layered Flask Architecture:
`Routes (Blueprints) → Services → Repositories → PostgreSQL`

Security controls are enforced at explicit layer boundaries:
- Input validation in **Routes**.
- RBAC, Fraud Detection, and Audit Logging in **Services**.
- Parameterized queries only in **Repositories**.
