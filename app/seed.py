import bcrypt
from app import create_app
from app.extensions import db
from app.models import User, UserRole

def seed():
    app = create_app()
    with app.app_context():
        if User.query.filter_by(username='admin').first():
            print("Already seeded.")
            return
        password_hash = bcrypt.hashpw(b'Admin123!', bcrypt.gensalt()).decode()
        admin = User(
            username='admin2',
            email='admin2@scbs.local',
            password_hash=password_hash,
            role=UserRole.admin,
        )
        db.session.add(admin)

        customer_hash = bcrypt.hashpw(b'Customer1!', bcrypt.gensalt()).decode()
        customer = User(
            username='alice',
            email='alice@scbs.local',
            password_hash=customer_hash,
            role=UserRole.customer,
        )
        db.session.add(customer)
        db.session.commit()
        print("Seeded: admin / Admin1234!  and  alice / Customer1!")

if __name__ == '__main__':
    seed()
