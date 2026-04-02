"""
models.py
---------
SQLAlchemy ORM models for the Auth Service.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    email           = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role            = Column(String, nullable=False)          # "industry" | "university" | "admin"
    created_at      = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role!r}>"
