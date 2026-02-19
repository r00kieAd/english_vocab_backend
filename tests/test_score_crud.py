import pytest
from sqlalchemy.orm import Session
from datetime import datetime

from models.scores import ScoreSheet
from schemas.scores import ScoreCreate
from crud.score_crud import (
    get_all_scores,
    get_high_score,
    create_score,
    delete_score_by_username,
)


class TestGetAllScores:
    """Test get_all_scores function"""
    
    def test_get_all_scores_empty(self, test_db_session: Session):
        """Test getting all scores when database is empty"""
        scores = get_all_scores(test_db_session)
        assert scores == []
    
    def test_get_all_scores_ordered_by_high_score(self, test_db_session: Session):
        """Test that scores are returned ordered by high_score descending"""
        # Create scores in random order
        score1 = ScoreCreate(high_score=100, high_scorer="Alice")
        score2 = ScoreCreate(high_score=500, high_scorer="Bob")
        score3 = ScoreCreate(high_score=250, high_scorer="Charlie")
        
        create_score(test_db_session, score1)
        create_score(test_db_session, score2)
        create_score(test_db_session, score3)
        
        scores = get_all_scores(test_db_session)
        
        assert len(scores) == 3
        assert scores[0].high_score == 500
        assert scores[1].high_score == 250
        assert scores[2].high_score == 100
    
    def test_get_all_scores_with_duplicate_scores(self, test_db_session: Session):
        """Test getting scores when multiple users have same score"""
        score1 = ScoreCreate(high_score=300, high_scorer="User1")
        score2 = ScoreCreate(high_score=300, high_scorer="User2")
        score3 = ScoreCreate(high_score=200, high_scorer="User3")
        
        create_score(test_db_session, score1)
        create_score(test_db_session, score2)
        create_score(test_db_session, score3)
        
        scores = get_all_scores(test_db_session)
        
        assert len(scores) == 3
        # Top two should be 300
        assert scores[0].high_score == 300
        assert scores[1].high_score == 300
        assert scores[2].high_score == 200


class TestGetHighScore:
    """Test get_high_score function"""
    
    def test_get_high_score_with_one_entry(self, test_db_session: Session):
        """Test getting high score when only one entry exists"""
        score = ScoreCreate(high_score=150, high_scorer="SingleUser")
        created = create_score(test_db_session, score)
        
        result = get_high_score(test_db_session)
        
        assert result is not None
        assert result.high_score == 150
        assert result.high_scorer == "SingleUser"
    
    def test_get_high_score_with_multiple_entries(self, test_db_session: Session):
        """Test that get_high_score returns the highest score"""
        score1 = ScoreCreate(high_score=100, high_scorer="User1")
        score2 = ScoreCreate(high_score=999, high_scorer="User2")
        score3 = ScoreCreate(high_score=500, high_scorer="User3")
        
        create_score(test_db_session, score1)
        create_score(test_db_session, score2)
        create_score(test_db_session, score3)
        
        result = get_high_score(test_db_session)
        
        assert result.high_score == 999
        assert result.high_scorer == "User2"
    
    def test_get_high_score_empty_database(self, test_db_session: Session):
        """Test get_high_score when database is empty"""
        result = get_high_score(test_db_session)
        assert result is None
    
    def test_get_high_score_after_updates(self, test_db_session: Session):
        """Test that high score updates correctly as new scores are added"""
        score1 = ScoreCreate(high_score=100, high_scorer="User1")
        create_score(test_db_session, score1)
        
        result = get_high_score(test_db_session)
        assert result.high_score == 100
        
        # Add higher score
        score2 = ScoreCreate(high_score=300, high_scorer="User2")
        create_score(test_db_session, score2)
        
        result = get_high_score(test_db_session)
        assert result.high_score == 300


class TestCreateScore:
    """Test create_score function"""
    
    def test_create_score_basic(self, test_db_session: Session):
        """Test creating a score entry"""
        score_create = ScoreCreate(high_score=250, high_scorer="TestUser")
        
        result = create_score(test_db_session, score_create)
        
        assert result.id is not None
        assert result.high_score == 250
        assert result.high_scorer == "TestUser"
        assert result.date_created is not None
    
    def test_create_score_zero_score(self, test_db_session: Session):
        """Test creating a score with zero value"""
        score_create = ScoreCreate(high_score=0, high_scorer="NewUser")
        
        result = create_score(test_db_session, score_create)
        
        assert result.high_score == 0
        assert result.high_scorer == "NewUser"
    
    def test_create_score_negative_score(self, test_db_session: Session):
        """Test creating a score with negative value"""
        score_create = ScoreCreate(high_score=-100, high_scorer="NegativeUser")
        
        result = create_score(test_db_session, score_create)
        
        assert result.high_score == -100
    
    def test_create_score_large_score(self, test_db_session: Session):
        """Test creating a score with large value"""
        score_create = ScoreCreate(high_score=999999, high_scorer="HighScorer")
        
        result = create_score(test_db_session, score_create)
        
        assert result.high_score == 999999
    
    def test_create_score_duplicate_usernames(self, test_db_session: Session):
        """Test that duplicate usernames are allowed"""
        score1 = ScoreCreate(high_score=100, high_scorer="SameUser")
        score2 = ScoreCreate(high_score=200, high_scorer="SameUser")
        
        result1 = create_score(test_db_session, score1)
        result2 = create_score(test_db_session, score2)
        
        assert result1.high_scorer == "SameUser"
        assert result2.high_scorer == "SameUser"
        assert result1.id != result2.id  # Different records
    
    def test_create_score_timestamps(self, test_db_session: Session):
        """Test that date_created is set"""
        before_create = datetime.utcnow()
        score_create = ScoreCreate(high_score=123, high_scorer="TimeUser")
        result = create_score(test_db_session, score_create)
        after_create = datetime.utcnow()
        
        assert before_create <= result.date_created <= after_create


class TestDeleteScoreByUsername:
    """Test delete_score_by_username function"""
    
    def test_delete_score_by_username_single_record(self, test_db_session: Session):
        """Test deleting a single score by username"""
        score = ScoreCreate(high_score=100, high_scorer="ToBeDeleted")
        create_score(test_db_session, score)
        
        deleted_count = delete_score_by_username(test_db_session, "ToBeDeleted")
        
        assert deleted_count == 1
        remaining = get_all_scores(test_db_session)
        assert len(remaining) == 0
    
    def test_delete_score_by_username_multiple_records(self, test_db_session: Session):
        """Test deleting multiple scores for same username"""
        score1 = ScoreCreate(high_score=100, high_scorer="User")
        score2 = ScoreCreate(high_score=200, high_scorer="User")
        score3 = ScoreCreate(high_score=300, high_scorer="Other")
        
        create_score(test_db_session, score1)
        create_score(test_db_session, score2)
        create_score(test_db_session, score3)
        
        deleted_count = delete_score_by_username(test_db_session, "User")
        
        assert deleted_count == 2
        remaining = get_all_scores(test_db_session)
        assert len(remaining) == 1
        assert remaining[0].high_scorer == "Other"
    
    def test_delete_score_by_username_case_insensitive(self, test_db_session: Session):
        """Test that deletion is case-insensitive"""
        score = ScoreCreate(high_score=100, high_scorer="CaseSensitive")
        create_score(test_db_session, score)
        
        # Try deleting with different case
        deleted_count = delete_score_by_username(test_db_session, "casesensitive")
        
        assert deleted_count == 1
        remaining = get_all_scores(test_db_session)
        assert len(remaining) == 0
    
    def test_delete_score_by_username_nonexistent_user(self, test_db_session: Session):
        """Test deleting a non-existent user returns 0"""
        score = ScoreCreate(high_score=100, high_scorer="ExistingUser")
        create_score(test_db_session, score)
        
        deleted_count = delete_score_by_username(test_db_session, "NonexistentUser")
        
        assert deleted_count == 0
        # Check that no records were deleted
        remaining = get_all_scores(test_db_session)
        assert len(remaining) == 1
    
    def test_delete_score_by_username_empty_database(self, test_db_session: Session):
        """Test deleting from empty database"""
        deleted_count = delete_score_by_username(test_db_session, "AnyUser")
        
        assert deleted_count == 0
    
    def test_delete_score_by_username_mixed_case_entries(self, test_db_session: Session):
        """Test deleting when multiple case variations exist"""
        score1 = ScoreCreate(high_score=100, high_scorer="TestUser")
        score2 = ScoreCreate(high_score=200, high_scorer="testuser")
        score3 = ScoreCreate(high_score=300, high_scorer="TESTUSER")
        
        create_score(test_db_session, score1)
        create_score(test_db_session, score2)
        create_score(test_db_session, score3)
        
        # Delete with any case variation
        deleted_count = delete_score_by_username(test_db_session, "testuser")
        
        assert deleted_count == 3  # All case variations should be deleted
        remaining = get_all_scores(test_db_session)
        assert len(remaining) == 0
