from fastapi import APIRouter, HTTPException

from schemas.scores import Score, ScoreCreate
from crud import score_crud


router = APIRouter(prefix="/scores", tags=["scores"])


@router.get("/", response_model=dict)
def get_vocab_info():
    """Return metadata about the score endpoints"""
    scores = score_crud.get_all_scores()
    return {
        "api_active": True,
        "total_scores": len(scores),
        "endpoints": {
            "get all scores": "/scores/all_scores",
            "get high score": "/scores/high_score",
            "insert score": "/scores/insert_score/",
            "delete score": "/scores/delete_score/{username}",
        },
    }


@router.get("/all_scores", response_model=list[Score])
def get_all_scores():
    return score_crud.get_all_scores()


@router.get("/high_score", response_model=list[Score])
def get_high_score():
    top_scores = score_crud.get_top_scores(3)
    if not top_scores:
        raise HTTPException(status_code=404, detail="No scores found")
    return top_scores


@router.post("/insert_score", response_model=Score)
def insert_score(score: ScoreCreate):
    return score_crud.create_score(score)


@router.delete("/delete_score/{username}")
def delete_score_by_username(username: str):
    """Delete all score entries by username (case-insensitive)"""
    deleted_count = score_crud.delete_score_by_username(username)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"No score found for username: {username}")
    return {
        "message": f"Successfully deleted {deleted_count} record(s) for user: {username}",
        "deleted_count": deleted_count,
    }
