from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from schemas.vocab import VocabCreate, VocabUpdate, Vocab, VocabCount, VocabTypes
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
    vocab_count = len(vocab_crud.get_all_vocab(db))
    return {
        "api_active": True,
        "total_words": vocab_count,
        "endpoints": {
            "get all vocabs": "/vocabs/read",
            "get all vocab types": "/vocabs/read/vocab_types",
            "get vocabs by type": "/vocabs/read/{word_type}/{word_count}",
            "get count for vocab types": "/vocabs/read/count/{word_type}",
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

@router.post("/bulk_create", response_model=dict)
def bulk_create_vocab(vocabs: list[VocabCreate], db: Session = Depends(get_db)):
    if not vocabs:
        raise HTTPException(status_code=404, detail="No vocabs found in your request")
    words_received = len(vocabs)
    inserted_count = 0
    existing_words = set()
    try:
        for vocab in vocabs:
            if not vocab:
                continue
            existing = vocab_crud.get_vocab_by_word(db, vocab.word)
            if existing:
                existing_words.add(vocab.word)
            else:
                status = vocab_crud.create_vocab(db, vocab)
                inserted_count += 1
        return {
            "words_received": words_received,
            "words_inserted": inserted_count,
            "existing_words": existing_words if existing_words else "none" 
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"unexpected error: {str(e)}, records inserted: {inserted_count}")

@router.get("/read", response_model=list[Vocab])
def read_vocabs(db: Session = Depends(get_db)):
    return vocab_crud.get_all_vocab(db)

@router.get("/read/vocab_types", response_model=VocabTypes)
def read_vocab_types(db: Session = Depends(get_db)):
    return vocab_crud.get_all_word_types(db)

@router.get("/read/{word_type}", response_model=list[Vocab])
def get_vocab_list_with_type(word_type: str, word_count: Optional[int] = None, db: Session = Depends(get_db)):
    if not word_type or len(word_type.strip()) == 0:
        raise HTTPException(status_code=400, detail="Invalid word type")
    return vocab_crud.get_vocab_by_type(db, word_type, word_count)

@router.get("/read/count/{word_type}", response_model=VocabCount)
def get_vocab_count_by_type(word_type: str, db: Session = Depends(get_db)):
    if not word_type or len(word_type.strip()) == 0:
        raise HTTPException(status_code=400, detail="Invalid word type")
    return vocab_crud.get_vocab_by_count(db=db, word_type=word_type)

@router.put("/update/{word}", response_model=Vocab)
def update_vocab(word: str, vocab_update: VocabUpdate, db: Session = Depends(get_db)):
    db_vocab = vocab_crud.get_vocab_by_word(db, word)
    if not db_vocab:
        raise HTTPException(status_code=404, detail="Word not found")
    return vocab_crud.update_vocab(db, db_vocab, vocab_update)