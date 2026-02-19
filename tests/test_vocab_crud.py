import pytest
from sqlalchemy.orm import Session
from datetime import datetime

from models.vocab import EnglishVocab
from schemas.vocab import VocabCreate, VocabUpdate
from crud.vocab_crud import (
    get_all_vocab,
    get_vocab_by_word,
    create_vocab,
    update_vocab,
)


class TestGetAllVocab:
    """Test get_all_vocab function"""
    
    def test_get_all_vocab_empty(self, test_db_session: Session):
        """Test getting all vocabs when database is empty"""
        vocabs = get_all_vocab(test_db_session)
        assert vocabs == []
    
    def test_get_all_vocab_with_data(self, test_db_session: Session):
        """Test getting all vocabs when data exists"""
        # Create test data
        vocab1 = VocabCreate(word="hello", word_type="noun", meaning="greeting", example="Hello world")
        vocab2 = VocabCreate(word="world", word_type="noun", meaning="earth", example="Welcome to the world")
        
        create_vocab(test_db_session, vocab1)
        create_vocab(test_db_session, vocab2)
        
        vocabs = get_all_vocab(test_db_session)
        
        assert len(vocabs) == 2
        words = [v.word for v in vocabs]
        assert "hello" in words
        assert "world" in words


class TestGetVocabByWord:
    """Test get_vocab_by_word function"""
    
    def test_get_vocab_by_word_found(self, test_db_session: Session):
        """Test retrieving an existing vocab"""
        vocab_create = VocabCreate(word="python", word_type="noun", meaning="a snake", example="I saw a python")
        created = create_vocab(test_db_session, vocab_create)
        
        result = get_vocab_by_word(test_db_session, "python")
        
        assert result is not None
        assert result.word == "python"
        assert result.word_type == "noun"
        assert result.meaning == "a snake"
    
    def test_get_vocab_by_word_not_found(self, test_db_session: Session):
        """Test retrieving a non-existent vocab"""
        result = get_vocab_by_word(test_db_session, "nonexistent")
        assert result is None
    
    def test_get_vocab_by_word_case_sensitive(self, test_db_session: Session):
        """Test that word lookup is case-sensitive"""
        vocab_create = VocabCreate(word="Apple", word_type="noun", meaning="a fruit", example="I ate an Apple")
        create_vocab(test_db_session, vocab_create)
        
        # Should find exact match
        result = get_vocab_by_word(test_db_session, "Apple")
        assert result is not None
        
        # Should not find with different case
        result = get_vocab_by_word(test_db_session, "apple")
        assert result is None


class TestCreateVocab:
    """Test create_vocab function"""
    
    def test_create_vocab_basic(self, test_db_session: Session):
        """Test creating a vocabulary entry"""
        vocab_create = VocabCreate(
            word="serendipity",
            word_type="noun",
            meaning="finding something good by chance",
            example="It was pure serendipity"
        )
        
        result = create_vocab(test_db_session, vocab_create)
        
        assert result.id is not None
        assert result.word == "serendipity"
        assert result.word_type == "noun"
        assert result.meaning == "finding something good by chance"
        assert result.example == "It was pure serendipity"
        assert result.created_at is not None
        assert result.updated_at is not None
    
    def test_create_vocab_minimal(self, test_db_session: Session):
        """Test creating a vocab with only required field"""
        vocab_create = VocabCreate(word="test")
        
        result = create_vocab(test_db_session, vocab_create)
        
        assert result.id is not None
        assert result.word == "test"
        assert result.word_type is None
        assert result.meaning is None
        assert result.example is None
    
    def test_create_vocab_duplicate_word(self, test_db_session: Session):
        """Test that duplicate words raise an error"""
        vocab_create = VocabCreate(word="duplicate")
        
        create_vocab(test_db_session, vocab_create)
        
        # Trying to create the same word should raise IntegrityError
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            create_vocab(test_db_session, vocab_create)
            test_db_session.commit()
    
    def test_create_vocab_timestamps(self, test_db_session: Session):
        """Test that created_at and updated_at are set"""
        before_create = datetime.utcnow()
        vocab_create = VocabCreate(word="timestamp_test")
        result = create_vocab(test_db_session, vocab_create)
        after_create = datetime.utcnow()
        
        assert before_create <= result.created_at <= after_create
        assert before_create <= result.updated_at <= after_create


class TestUpdateVocab:
    """Test update_vocab function"""
    
    def test_update_vocab_all_fields(self, test_db_session: Session):
        """Test updating all fields of a vocab"""
        # Create initial vocab
        vocab_create = VocabCreate(
            word="original",
            word_type="noun",
            meaning="original meaning",
            example="original example"
        )
        db_vocab = create_vocab(test_db_session, vocab_create)
        
        # Update all fields
        vocab_update = VocabUpdate(
            word_type="verb",
            meaning="updated meaning",
            example="updated example"
        )
        result = update_vocab(test_db_session, db_vocab, vocab_update)
        
        assert result.word == "original"  # word should not change
        assert result.word_type == "verb"
        assert result.meaning == "updated meaning"
        assert result.example == "updated example"
    
    def test_update_vocab_partial_fields(self, test_db_session: Session):
        """Test updating only some fields"""
        vocab_create = VocabCreate(
            word="partial",
            word_type="noun",
            meaning="partial meaning"
        )
        db_vocab = create_vocab(test_db_session, vocab_create)
        original_meaning = db_vocab.meaning
        
        # Update only word_type
        vocab_update = VocabUpdate(word_type="adjective")
        result = update_vocab(test_db_session, db_vocab, vocab_update)
        
        assert result.word_type == "adjective"
        assert result.meaning == original_meaning  # Should remain unchanged
        assert result.example is None
    
    def test_update_vocab_no_changes(self, test_db_session: Session):
        """Test updating with no changes"""
        vocab_create = VocabCreate(word="nochange", word_type="noun")
        db_vocab = create_vocab(test_db_session, vocab_create)
        original_updated_at = db_vocab.updated_at
        
        # Update with empty fields (exclude_unset=True)
        vocab_update = VocabUpdate()
        result = update_vocab(test_db_session, db_vocab, vocab_update)
        
        assert result.word == "nochange"
        assert result.word_type == "noun"
    
    def test_update_vocab_timestamps(self, test_db_session: Session):
        """Test that updated_at changes when updated"""
        vocab_create = VocabCreate(word="timestamp_update")
        db_vocab = create_vocab(test_db_session, vocab_create)
        original_updated_at = db_vocab.updated_at
        
        # Update the vocab
        vocab_update = VocabUpdate(meaning="new meaning")
        result = update_vocab(test_db_session, db_vocab, vocab_update)
        
        # updated_at should be updated
        assert result.updated_at >= original_updated_at
        assert result.created_at == db_vocab.created_at  # created_at should not change
