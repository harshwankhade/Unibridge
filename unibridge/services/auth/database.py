"""
database.py
-----------
SQLAlchemy engine, session factory, and declarative base for the Auth Service.
Uses SQLite for simplicity; swap DATABASE_URL for Postgres in production.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ensure the directory exists (needed on first startup with a fresh volume)
os.makedirs("./auth_store", exist_ok=True)

DATABASE_URL = "sqlite:///./auth_store/auth.db"  # lives in the persisted auth_store volume

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
