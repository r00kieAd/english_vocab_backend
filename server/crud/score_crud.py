from sqlalchemy.orm import Session
from models.scores import ScoreSheet
from schemas.scores import ScoreCreate
from sqlalchemy import desc


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