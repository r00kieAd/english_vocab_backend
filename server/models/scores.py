from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database.database import Base

class ScoreSheet(Base):
    __tablename__ = "high_score"

    id = Column(Integer, primary_key=True, index=True)
    high_score = Column(Integer, unique=False)
    high_scorer = Column(String, unique=False)
    date_created = Column(DateTime, default=datetime.utcnow)