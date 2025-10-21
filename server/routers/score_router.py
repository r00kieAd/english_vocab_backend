from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import SessionLocal, engine
from schemas.scores import Score, ScoreCreate
from crud import score_crud

router = APIRouter(prefix="/scores", tags=["scores"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=dict)
def get_vocab_info(db: Session = Depends(get_db)):
    """Get information about the score endpoints"""
    scores_count = len(score_crud.get_all_scores(db))
    return {
        "api_active": True,
        "total_scores": scores_count,
        "endpoints": {
            "get all scores": "/scores/all_scores",
            "get high score": "/scores/high_score",
            "insert score": "/scores/insert_score/"
        }
    }

@router.get("/all_scores", response_model=list[Score])
def get_all_scores(db: Session = Depends(get_db)):
    return score_crud.get_all_scores(db)

@router.get("/high_score", response_model=Score)
def get_high_score(db: Session = Depends(get_db)):
    score = score_crud.get_high_score(db)
    if not score:
        raise HTTPException(status_code=404, detail="No scores found")
    return score

@router.post("/insert_score", response_model=Score)
def insert_score(score: ScoreCreate, db: Session = Depends(get_db)):
    return score_crud.create_score(db, score)