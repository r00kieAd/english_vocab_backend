from sqlalchemy.orm import Session
from models.scores import ScoreSheet
from schemas.scores import ScoreCreate
from sqlalchemy import desc, func


def get_all_scores(db: Session):
    """Get all scores ordered by score value descending"""
    return db.query(ScoreSheet).order_by(desc(ScoreSheet.high_score)).all()

def get_high_score(db: Session):
    """Get the highest score entry"""
    return db.query(ScoreSheet).order_by(desc(ScoreSheet.high_score)).first()

def create_score(db: Session, score: ScoreCreate):
    """Create a new score entry"""
    db_score = ScoreSheet(
        high_score=score.high_score,
        high_scorer=score.high_scorer
    )
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score

def delete_score_by_username(db: Session, username: str):
    all_records = db.query(ScoreSheet).all()
    
    deleted_count = db.query(ScoreSheet).filter(
        func.lower(ScoreSheet.high_scorer) == func.lower(username)
    ).delete()
    
    print(f"DEBUG: Deleted count: {deleted_count}")
    db.commit()
    
    return deleted_count