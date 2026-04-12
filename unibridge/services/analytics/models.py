from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base


class SearchEvent(Base):
    __tablename__ = "search_events"

    id                = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id           = Column(Integer, nullable=True)          # None for unauthenticated searches
    query             = Column(String,  nullable=False)         # original user query
    translated_query  = Column(String,  nullable=True)
    category          = Column(String,  nullable=False)         # solve / benchmark / landscape
    result_count      = Column(Integer, default=0)
    top_domains       = Column(String,  nullable=True)          # comma-separated, e.g. "Computing & AI,Life Sciences"
    top_universities  = Column(String,  nullable=True)          # comma-separated
    created_at        = Column(DateTime, default=datetime.utcnow)
