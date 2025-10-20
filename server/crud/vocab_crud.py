from sqlalchemy.orm import Session
from models.vocab import EnglishVocab
from schemas.vocab import VocabCreate, VocabUpdate

def get_all_vocab(db: Session):
    return db.query(EnglishVocab).all()

def get_vocab_by_word(db: Session, word: str):
    return db.query(EnglishVocab).filter(EnglishVocab.word == word).first()

def create_vocab(db: Session, vocab: VocabCreate):
    db_vocab = EnglishVocab(**vocab.dict())
    db.add(db_vocab)
    db.commit()
    db.refresh(db_vocab)
    return db_vocab

def update_vocab(db: Session, db_vocab: EnglishVocab, vocab_update: VocabUpdate):
    for key, value in vocab_update.dict(exclude_unset=True).items():
        setattr(db_vocab, key, value)
    db.commit()
    db.refresh(db_vocab)
    return db_vocab