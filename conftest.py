import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "server")))

from database.database import Base
from models import vocab, scores
from main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_temp.db" 

@pytest.fixture(scope="function")
def test_db_engine():
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="function")
def test_client(test_db_session):
    from routers.vocab_router import get_db as vocab_get_db
    from routers.score_router import get_db as score_get_db

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    app.dependency_overrides[vocab_get_db] = override_get_db
    app.dependency_overrides[score_get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()