from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database.database import Base

class EnglishVocab(Base):
    __tablename__ = "english_vocabs"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True, nullable=False)
    word_type = Column(String, unique=False, index=True, nullable=True)
    meaning = Column(String, nullable=True)
    example = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)