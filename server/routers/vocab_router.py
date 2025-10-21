from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.vocab import VocabCreate, VocabUpdate, Vocab
from crud import vocab_crud
from database.database import SessionLocal, engine

router = APIRouter(
    prefix="/vocabs",
    tags=["vocabs"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=dict)
def get_vocab_info(db: Session = Depends(get_db)):
    """Get information about the vocabulary endpoints"""
    vocab_count = len(vocab_crud.get_all_vocab(db))
    return {
        "api_active": True,
        "total_words": vocab_count,
        "endpoints": {
            "get all vocabs": "/vocabs/read",
            "create vocab": "/vocabs/create",
            "update vocab": "/vocabs/update/{word}"
        }
    }

@router.post("/create", response_model=Vocab)
def create_vocab(vocab: VocabCreate, db: Session = Depends(get_db)):
    existing = vocab_crud.get_vocab_by_word(db, vocab.word)
    if existing:
        raise HTTPException(status_code=400, detail="Word already exists")
    return vocab_crud.create_vocab(db, vocab)

@router.get("/read", response_model=list[Vocab])
def read_vocabs(db: Session = Depends(get_db)):
    return vocab_crud.get_all_vocab(db)

@router.put("/update/{word}", response_model=Vocab)
def update_vocab(word: str, vocab_update: VocabUpdate, db: Session = Depends(get_db)):
    db_vocab = vocab_crud.get_vocab_by_word(db, word)
    if not db_vocab:
        raise HTTPException(status_code=404, detail="Word not found")
    return vocab_crud.update_vocab(db, db_vocab, vocab_update)