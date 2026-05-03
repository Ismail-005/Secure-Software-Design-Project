# SCBS Setup Instructions

Follow these steps to configure and run the Secure Core Banking System (SCBS).

### 1. Update your `.env` file
Set a strong application secret key before you run the app. The database now defaults to SQLite files in the project root:
```env
SECRET_KEY=YOUR_RANDOM_SECRET_KEY
DATABASE_URL=sqlite:///scbs.db
TEST_DATABASE_URL=sqlite:///scbs_test.db
DEMO_SHOW_OTP=true
```

### 2. Activate Virtual Environment & Install Dependencies
Ensure your terminal is using the project's Python environment. If using `uv`:
```bash
uv pip install -r requirements.txt
```
Or if using standard `venv`:
```bash
# Windows
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Initialize the Database Schema
Tell Flask-Migrate to read the SQLAlchemy models and build the tables in your SQLite database:
```bash
flask --app run.py db init
flask --app run.py db migrate -m "initial schema"
flask --app run.py db upgrade
```

### 4. Seed the Initial Data
Populate the database with the initial Admin and Customer accounts so you can log in:
```bash
  python -m app.seed
```
*(This will print a confirmation that it created the users `admin` and `alice`.)*

### 5. Run the Application
Start the Flask development server:
```bash
flask --app run.py run
```
You can now open your browser and go to `http://127.0.0.1:5000` to use the application.
With `DEMO_SHOW_OTP=true`, the MFA screen will display the current login code inside the app so the coursework flow remains usable without SMS, email, or an authenticator app.

### 6. Run the Tests
To verify the application behavior, run:
```bash
pytest tests/ -v
```
