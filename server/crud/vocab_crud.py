from sqlalchemy.orm import Session
from models.vocab import EnglishVocab
from schemas.vocab import VocabCreate, VocabUpdate, VocabCount, VocabTypes

def get_all_vocab(db: Session):
    return db.query(EnglishVocab).all()

def get_vocab_by_word(db: Session, word: str):
    return db.query(EnglishVocab).filter(EnglishVocab.word == word).first()

def get_vocab_by_type(db: Session, word_type: str, count: int = 0):
    query = db.query(EnglishVocab).filter(EnglishVocab.word_type == word_type)
    if count is not None and count > 0:
        return query.limit(count).all()
    return query.all()

def get_vocab_by_count(db: Session, word_type: str):
    count = db.query(EnglishVocab).filter(EnglishVocab.word_type == word_type).count()
    return VocabCount(word_type=word_type, count=count)

def get_all_word_types(db: Session):
    types = (db.query(EnglishVocab.word_type).distinct().all())
    type_list = [t[0] for t in types]
    return VocabTypes(word_types=type_list)

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