"""
models.py
---------
SQLAlchemy ORM model for the Submission Service.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    title               = Column(String, nullable=False)
    abstract            = Column(String, nullable=False)
    university          = Column(String, nullable=False)
    contributors        = Column(String, nullable=False)   # comma-separated names
    domain              = Column(String, nullable=False)
    ip_type             = Column(String, nullable=False)   # "patent" | "paper"
    legal_status        = Column(String, default="PENDING")
    submitted_by        = Column(Integer, nullable=False)  # user_id of submitter
    submitted_by_email  = Column(String, nullable=False)
    status              = Column(String, default="pending")  # pending | approved | rejected
    admin_note          = Column(String, nullable=True)
    created_at          = Column(DateTime, default=datetime.utcnow)
    updated_at          = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id":                 self.id,
            "title":              self.title,
            "abstract":           self.abstract,
            "university":         self.university,
            "contributors":       self.contributors,
            "domain":             self.domain,
            "ip_type":            self.ip_type,
            "legal_status":       self.legal_status,
            "submitted_by":       self.submitted_by,
            "submitted_by_email": self.submitted_by_email,
            "status":             self.status,
            "admin_note":         self.admin_note,
            "created_at":         self.created_at.isoformat() if self.created_at else None,
            "updated_at":         self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Submission id={self.id} title={self.title!r} status={self.status!r}>"
