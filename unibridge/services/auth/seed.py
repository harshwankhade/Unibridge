"""
seed.py
-------
Populates the auth database with one demo user per role if the table is empty.

Run:
    python seed.py
"""

from passlib.context import CryptContext

from database import SessionLocal, engine
from models import Base, User

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

_DEMO_USERS = [
    {"email": "industry@demo.com",    "password": "demo1234", "role": "industry"},
    {"email": "university@demo.com",  "password": "demo1234", "role": "university"},
    {"email": "admin@demo.com",       "password": "demo1234", "role": "admin"},
]


def seed() -> None:
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        count = db.query(User).count()

        if count == 0:
            for u in _DEMO_USERS:
                db.add(
                    User(
                        email=u["email"],
                        hashed_password=_pwd_ctx.hash(u["password"]),
                        role=u["role"],
                    )
                )
            db.commit()
            print("Seeded 3 demo users:")
            for u in _DEMO_USERS:
                print(f"  {u['role']:12s}  {u['email']}  /  password: {u['password']}")
        else:
            existing = db.query(User.email, User.role).all()
            print("Database already has users, skipping seed.")
            print("Existing users:")
            for email, role in existing:
                print(f"  {role:12s}  {email}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
