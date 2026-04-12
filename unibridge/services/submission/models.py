from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    abstract = Column(String, nullable=False)
    university = Column(String, nullable=False)
    contributors = Column(String, nullable=False)   # comma-separated names
    domain = Column(String, nullable=False)
    ip_type = Column(String, nullable=False)        # "patent" or "paper"
    legal_status = Column(String, default="PENDING")
    submitted_by = Column(Integer, nullable=False)  # user_id of the submitter
    submitted_by_email = Column(String, nullable=False)
    status = Column(String, default="pending")      # "pending" | "approved" | "rejected"
    admin_note = Column(String, nullable=True)      # reason for rejection or approval note
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
