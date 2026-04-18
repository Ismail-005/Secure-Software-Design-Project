# SCBS Setup Instructions

Follow these steps to complete the final setup of your Secure Core Banking System (SCBS) now that the code has been fully generated.

### 1. Update your `.env` file
The project uses the `postgres` user, but the password in `.env` is currently set to a placeholder (`password`). 
Open `.env` and change the database URLs to match the password you set during your PostgreSQL installation:
```env
DATABASE_URL=postgresql://postgres:YOUR_REAL_PASSWORD@localhost/scbs
TEST_DATABASE_URL=postgresql://postgres:YOUR_REAL_PASSWORD@localhost/scbs_test
```

### 2. Create the Databases
Open your SQL client (like **pgAdmin 4** or **psql**) and run these two commands to create the required databases:
```sql
CREATE DATABASE scbs;
CREATE DATABASE scbs_test;
```

### 3. Activate Virtual Environment & Install Dependencies
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

### 4. Initialize the Database Schema
Now we need to tell Flask-Migrate to read the SQLAlchemy models and build the tables in your PostgreSQL database. Run these commands in your terminal:
```bash
flask --app run db init
flask --app run db migrate -m "initial schema"
flask --app run db upgrade
```

### 5. Seed the Initial Data
Populate the database with the initial Admin and Customer accounts so you can log in:
```bash
python app/seed.py
```
*(This will print a confirmation that it created the users `admin` and `alice`)*.

### 6. Run the Application
Start the Flask development server:
```bash
flask --app run run --debug
```
You can now open your browser and go to `http://127.0.0.1:5000` to see the core banking system in action!

### 7. Run the Security & Unit Tests (Optional)
To verify that all the fraud detection, RBAC, HMAC chaining, and security rules are working correctly, you can run the test suite:
```bash
pytest tests/ -v
```
