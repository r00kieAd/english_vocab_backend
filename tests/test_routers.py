import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from schemas.vocab import VocabCreate
from schemas.scores import ScoreCreate
from crud.vocab_crud import create_vocab
from crud.score_crud import create_score


class TestVocabRouter:
    """Integration tests for vocab router endpoints"""
    
    def test_vocab_root_endpoint_empty(self, test_client: TestClient, test_db_session: Session):
        """Test GET /vocabs/ returns info with 0 words"""
        response = test_client.get("/vocabs/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["api_active"] is True
        assert data["total_words"] == 0
        assert "endpoints" in data
    
    def test_vocab_root_endpoint_with_data(self, test_client: TestClient, test_db_session: Session):
        """Test GET /vocabs/ returns correct word count"""
        # Create some vocabs
        vocab1 = VocabCreate(word="hello", word_type="noun")
        vocab2 = VocabCreate(word="world", word_type="noun")
        create_vocab(test_db_session, vocab1)
        create_vocab(test_db_session, vocab2)
        
        response = test_client.get("/vocabs/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_words"] == 2
    
    def test_create_vocab_success(self, test_client: TestClient, test_db_session: Session):
        """Test creating a new vocabulary entry"""
        payload = {
            "word": "python",
            "word_type": "noun",
            "meaning": "a snake",
            "example": "Python is a snake"
        }
        
        response = test_client.post("/vocabs/create", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["word"] == "python"
        assert data["word_type"] == "noun"
        assert data["meaning"] == "a snake"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_vocab_minimal(self, test_client: TestClient, test_db_session: Session):
        """Test creating a vocab with only required field"""
        payload = {"word": "test"}
        
        response = test_client.post("/vocabs/create", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["word"] == "test"
    
    def test_create_vocab_duplicate_word(self, test_client: TestClient, test_db_session: Session):
        """Test creating vocab with duplicate word returns 400"""
        payload = {"word": "duplicate"}
        
        # Create first vocab
        response1 = test_client.post("/vocabs/create", json=payload)
        assert response1.status_code == 200
        
        # Try creating with same word
        response2 = test_client.post("/vocabs/create", json=payload)
        
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]
    
    def test_read_vocabs_empty(self, test_client: TestClient, test_db_session: Session):
        """Test GET /vocabs/read returns empty list"""
        response = test_client.get("/vocabs/read")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_read_vocabs_with_data(self, test_client: TestClient, test_db_session: Session):
        """Test GET /vocabs/read returns all vocabs"""
        # Create vocabs
        payload1 = {"word": "first", "meaning": "first meaning"}
        payload2 = {"word": "second", "meaning": "second meaning"}
        
        test_client.post("/vocabs/create", json=payload1)
        test_client.post("/vocabs/create", json=payload2)
        
        response = test_client.get("/vocabs/read")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        words = [v["word"] for v in data]
        assert "first" in words
        assert "second" in words
    
    def test_update_vocab_success(self, test_client: TestClient, test_db_session: Session):
        """Test updating a vocab"""
        # Create vocab
        create_payload = {"word": "original", "word_type": "noun"}
        test_client.post("/vocabs/create", json=create_payload)
        
        # Update vocab
        update_payload = {
            "word_type": "verb",
            "meaning": "updated meaning",
            "example": "updated example"
        }
        response = test_client.put("/vocabs/update/original", json=update_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["word"] == "original"
        assert data["word_type"] == "verb"
        assert data["meaning"] == "updated meaning"
        assert data["example"] == "updated example"
    
    def test_update_vocab_not_found(self, test_client: TestClient, test_db_session: Session):
        """Test updating non-existent vocab returns 404"""
        update_payload = {"word_type": "verb"}
        response = test_client.put("/vocabs/update/nonexistent", json=update_payload)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_bulk_create_vocabs_success(self, test_client: TestClient, test_db_session: Session):
        """Test bulk creating vocabs"""
        payload = [
            {"word": "bulk1", "word_type": "noun"},
            {"word": "bulk2", "word_type": "verb"},
            {"word": "bulk3", "word_type": "adjective"}
        ]
        
        response = test_client.post("/vocabs/bulk_create", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["words_received"] == 3
        assert data["words_inserted"] == 3
        assert data["existing_words"] == "none"
    
    def test_bulk_create_vocabs_with_duplicates(self, test_client: TestClient, test_db_session: Session):
        """Test bulk create handles existing words"""
        # Create one vocab first
        test_client.post("/vocabs/create", json={"word": "existing"})
        
        # Bulk create with mixture of new and existing
        payload = [
            {"word": "existing"},  # Already exists
            {"word": "new1"},
            {"word": "new2"}
        ]
        
        response = test_client.post("/vocabs/bulk_create", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["words_received"] == 3
        assert data["words_inserted"] == 2
        assert "existing" in data["existing_words"]
    
    def test_bulk_create_vocabs_empty_list(self, test_client: TestClient, test_db_session: Session):
        """Test bulk create with empty list returns 404"""
        response = test_client.post("/vocabs/bulk_create", json=[])
        
        assert response.status_code == 404
        assert "No vocabs found" in response.json()["detail"]


class TestScoreRouter:
    """Integration tests for score router endpoints"""
    
    def test_score_root_endpoint_empty(self, test_client: TestClient, test_db_session: Session):
        """Test GET /scores/ returns info with 0 scores"""
        response = test_client.get("/scores/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["api_active"] is True
        assert data["total_scores"] == 0
        assert "endpoints" in data
    
    def test_score_root_endpoint_with_data(self, test_client: TestClient, test_db_session: Session):
        """Test GET /scores/ returns correct score count"""
        # Create some scores
        score1 = ScoreCreate(high_score=100, high_scorer="User1")
        score2 = ScoreCreate(high_score=200, high_scorer="User2")
        create_score(test_db_session, score1)
        create_score(test_db_session, score2)
        
        response = test_client.get("/scores/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_scores"] == 2
    
    def test_get_all_scores_empty(self, test_client: TestClient, test_db_session: Session):
        """Test GET /scores/all_scores returns empty list"""
        response = test_client.get("/scores/all_scores")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_get_all_scores_with_data(self, test_client: TestClient, test_db_session: Session):
        """Test GET /scores/all_scores returns scores sorted by score"""
        # Create scores in random order
        create_score(test_db_session, ScoreCreate(high_score=100, high_scorer="User1"))
        create_score(test_db_session, ScoreCreate(high_score=500, high_scorer="User2"))
        create_score(test_db_session, ScoreCreate(high_score=250, high_scorer="User3"))
        
        response = test_client.get("/scores/all_scores")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Should be sorted by score descending
        assert data[0]["high_score"] == 500
        assert data[1]["high_score"] == 250
        assert data[2]["high_score"] == 100
    
    def test_get_high_score_success(self, test_client: TestClient, test_db_session: Session):
        """Test GET /scores/high_score returns highest score"""
        create_score(test_db_session, ScoreCreate(high_score=100, high_scorer="User1"))
        create_score(test_db_session, ScoreCreate(high_score=999, high_scorer="User2"))
        create_score(test_db_session, ScoreCreate(high_score=500, high_scorer="User3"))
        
        response = test_client.get("/scores/high_score")
        
        assert response.status_code == 200
        data = response.json()
        assert data["high_score"] == 999
        assert data["high_scorer"] == "User2"
    
    def test_get_high_score_empty(self, test_client: TestClient, test_db_session: Session):
        """Test GET /scores/high_score returns 404 when no scores exist"""
        response = test_client.get("/scores/high_score")
        
        assert response.status_code == 404
        assert "No scores found" in response.json()["detail"]
    
    def test_insert_score_success(self, test_client: TestClient, test_db_session: Session):
        """Test POST /scores/insert_score creates a new score"""
        payload = {"high_score": 350, "high_scorer": "TestUser"}
        
        response = test_client.post("/scores/insert_score", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["high_score"] == 350
        assert data["high_scorer"] == "TestUser"
        assert "id" in data
        assert "date_created" in data
    
    def test_insert_score_zero(self, test_client: TestClient, test_db_session: Session):
        """Test inserting score with zero value"""
        payload = {"high_score": 0, "high_scorer": "ZeroUser"}
        
        response = test_client.post("/scores/insert_score", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["high_score"] == 0
    
    def test_insert_score_negative(self, test_client: TestClient, test_db_session: Session):
        """Test inserting negative score"""
        payload = {"high_score": -50, "high_scorer": "NegativeUser"}
        
        response = test_client.post("/scores/insert_score", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["high_score"] == -50
    
    def test_delete_score_by_username_success(self, test_client: TestClient, test_db_session: Session):
        """Test DELETE /scores/delete_score/{username}"""
        # Create some scores
        create_score(test_db_session, ScoreCreate(high_score=100, high_scorer="ToDelete"))
        create_score(test_db_session, ScoreCreate(high_score=200, high_scorer="ToKeep"))
        
        response = test_client.delete("/scores/delete_score/ToDelete")
        
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 1
        assert "ToDelete" in data["message"]
        
        # Verify deletion
        remaining_response = test_client.get("/scores/all_scores")
        remaining_data = remaining_response.json()
        assert len(remaining_data) == 1
        assert remaining_data[0]["high_scorer"] == "ToKeep"
    
    def test_delete_score_by_username_multiple_records(self, test_client: TestClient, test_db_session: Session):
        """Test deleting multiple records for same username"""
        create_score(test_db_session, ScoreCreate(high_score=100, high_scorer="MultiUser"))
        create_score(test_db_session, ScoreCreate(high_score=200, high_scorer="MultiUser"))
        create_score(test_db_session, ScoreCreate(high_score=300, high_scorer="Other"))
        
        response = test_client.delete("/scores/delete_score/MultiUser")
        
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 2
    
    def test_delete_score_by_username_case_insensitive(self, test_client: TestClient, test_db_session: Session):
        """Test that deletion is case-insensitive"""
        create_score(test_db_session, ScoreCreate(high_score=100, high_scorer="CaseTest"))
        
        response = test_client.delete("/scores/delete_score/casetest")
        
        assert response.status_code == 200
        assert response.json()["deleted_count"] == 1
    
    def test_delete_score_by_username_not_found(self, test_client: TestClient, test_db_session: Session):
        """Test deleting non-existent username returns 404"""
        create_score(test_db_session, ScoreCreate(high_score=100, high_scorer="Existing"))
        
        response = test_client.delete("/scores/delete_score/NonExistent")
        
        assert response.status_code == 404
        assert "No score found" in response.json()["detail"]
    
    def test_delete_score_by_username_empty_database(self, test_client: TestClient, test_db_session: Session):
        """Test deleting from empty database returns 404"""
        response = test_client.delete("/scores/delete_score/AnyUser")
        
        assert response.status_code == 404


class TestCrossRouterIntegration:
    """Integration tests across vocabs and scores"""
    
    def test_api_has_both_routers(self, test_client: TestClient):
        """Test that both routers are registered"""
        # Check vocab root
        vocab_response = test_client.get("/vocabs/")
        assert vocab_response.status_code == 200
        
        # Check score root
        score_response = test_client.get("/scores/")
        assert score_response.status_code == 200
    
    def test_isolated_databases(self, test_client: TestClient, test_db_session: Session):
        """Test that vocab and score operations don't interfere"""
        # Create vocab
        vocab_payload = {"word": "test", "word_type": "noun"}
        vocab_response = test_client.post("/vocabs/create", json=vocab_payload)
        assert vocab_response.status_code == 200
        
        # Create score
        score_payload = {"high_score": 100, "high_scorer": "TestUser"}
        score_response = test_client.post("/scores/insert_score", json=score_payload)
        assert score_response.status_code == 200
        
        # Both databases should have their data
        vocabs_response = test_client.get("/vocabs/read")
        assert len(vocabs_response.json()) == 1
        
        scores_response = test_client.get("/scores/all_scores")
        assert len(scores_response.json()) == 1
