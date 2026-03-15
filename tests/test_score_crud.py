from datetime import datetime, timezone

from crud import score_crud
from schemas.scores import Score, ScoreCreate


def test_get_all_scores_orders_by_high_score(monkeypatch):
    records = [
        {"id": 1, "high_score": 10, "high_scorer": "alpha", "date_modified": "2026-03-10T00:00:00Z"},
        {"id": 2, "high_score": 50, "high_scorer": "bravo", "date_modified": "2026-03-10T00:00:01Z"},
        {"id": 3, "high_score": 30, "high_scorer": "charlie", "date_modified": "2026-03-10T00:00:02Z"},
    ]
    called = {}

    def fake_request(method, url, **kwargs):
        called["method"] = method
        called["url"] = url
        return records

    monkeypatch.setattr(score_crud, "_request", fake_request)

    results = score_crud.get_all_scores()

    assert called["method"] == "GET"
    assert [score.high_score for score in results] == [50, 30, 10]
    assert results[0].high_scorer == "bravo"


def test_get_high_score_returns_none_when_no_scores(monkeypatch):
    monkeypatch.setattr(score_crud, "get_all_scores", lambda: [])
    assert score_crud.get_high_score() is None


def test_get_high_score_returns_highest(monkeypatch):
    sample_scores = [
        Score(id=1, high_score=10, high_scorer="alpha", date_created=datetime.now(timezone.utc)),
        Score(id=2, high_score=100, high_scorer="beta", date_created=datetime.now(timezone.utc)),
        Score(id=3, high_score=50, high_scorer="charlie", date_created=datetime.now(timezone.utc)),
    ]
    monkeypatch.setattr(
        score_crud,
        "get_all_scores",
        lambda: sorted(sample_scores, key=lambda s: s.high_score, reverse=True),
    )

    result = score_crud.get_high_score()

    assert result.high_score == 100
    assert result.high_scorer == "beta"


def test_get_top_scores_limits(monkeypatch):
    sample_scores = [
        Score(id=1, high_score=30, high_scorer="alpha", date_created=datetime.now(timezone.utc)),
        Score(id=2, high_score=20, high_scorer="beta", date_created=datetime.now(timezone.utc)),
        Score(id=3, high_score=10, high_scorer="charlie", date_created=datetime.now(timezone.utc)),
        Score(id=4, high_score=5, high_scorer="delta", date_created=datetime.now(timezone.utc)),
    ]
    monkeypatch.setattr(score_crud, "get_all_scores", lambda: sample_scores)

    top_scores = score_crud.get_top_scores(3)

    assert len(top_scores) == 3
    assert top_scores[0].high_score == 30


def test_get_all_scores_dedupes(monkeypatch):
    records = [
        {"id": 1, "high_score": 5, "high_scorer": "tester", "date_modified": "2026-03-10T01:00:00Z"},
        {"id": 2, "high_score": 8, "high_scorer": "Tester", "date_modified": "2026-03-10T01:10:00Z"},
        {"id": 3, "high_score": 7, "high_scorer": "tester", "date_modified": "2026-03-10T01:05:00Z"},
    ]

    monkeypatch.setattr(score_crud, "_request", lambda *args, **kwargs: records)

    results = score_crud.get_all_scores()

    assert len(results) == 1
    assert results[0].high_score == 8
    assert results[0].id == 2


def test_create_score_posts_payload(monkeypatch):
    score_create = ScoreCreate(high_score=75, high_scorer="tester")
    called = {}

    def fake_request(method, url, **kwargs):
        called["method"] = method
        called["url"] = url
        called["json"] = kwargs.get("json")
        return {"id": 10, "high_score": 75, "high_scorer": "tester", "date_modified": "2026-03-10T01:00:00Z"}

    monkeypatch.setattr(score_crud, "get_all_scores", lambda: [])
    monkeypatch.setattr(score_crud, "_request", fake_request)

    result = score_crud.create_score(score_create)

    assert called["method"] == "POST"
    assert called["json"] == score_create.model_dump()
    assert result.id == 10
    assert result.high_scorer == "tester"
    assert result.date_created.isoformat().startswith("2026-03-10T01:00:00")


def test_create_score_updates_when_higher(monkeypatch):
    existing = Score(id=1, high_score=50, high_scorer="lonefox", date_created=datetime.now(timezone.utc))
    called = {}

    def fake_request(method, url, **kwargs):
        called["method"] = method
        called["url"] = url
        called["json"] = kwargs.get("json")
        return {"id": 1, "high_score": 60, "high_scorer": "lonefox", "date_modified": "2026-03-10T02:00:00Z"}

    monkeypatch.setattr(score_crud, "get_all_scores", lambda: [existing])
    monkeypatch.setattr(score_crud, "_format_update_url", lambda record_id: f"https://example/{record_id}")
    monkeypatch.setattr(score_crud, "_request", fake_request)

    result = score_crud.create_score(ScoreCreate(high_score=60, high_scorer="loneFox"))

    assert called["method"] == "PUT"
    assert called["url"] == "https://example/1"
    assert result.high_score == 60


def test_create_score_returns_existing_when_lower(monkeypatch):
    existing = Score(id=1, high_score=50, high_scorer="lonefox", date_created=datetime.now(timezone.utc))
    monkeypatch.setattr(score_crud, "get_all_scores", lambda: [existing])
    monkeypatch.setattr(score_crud, "_request", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("Should not call _request")))

    result = score_crud.create_score(ScoreCreate(high_score=40, high_scorer="loneFox"))

    assert result.high_score == 50


def test_delete_score_by_username_deletes_matches(monkeypatch):
    sample = [
        Score(id=1, high_score=100, high_scorer="Match", date_created=datetime.now(timezone.utc)),
        Score(id=2, high_score=200, high_scorer="Other", date_created=datetime.now(timezone.utc)),
        Score(id=3, high_score=150, high_scorer="match", date_created=datetime.now(timezone.utc)),
    ]
    deleted_urls = []

    def fake_request(method, url, **kwargs):
        if method == "DELETE":
            deleted_urls.append(url)
            return None
        return []

    monkeypatch.setattr(score_crud, "get_all_scores", lambda: sample)
    monkeypatch.setattr(score_crud, "_format_update_url", lambda record_id: f"https://example/{record_id}")
    monkeypatch.setattr(score_crud, "_request", fake_request)

    deleted = score_crud.delete_score_by_username("match")

    assert deleted == 2
    assert deleted_urls == ["https://example/1", "https://example/3"]


def test_delete_score_by_username_returns_zero_when_not_found(monkeypatch):
    monkeypatch.setattr(score_crud, "get_all_scores", lambda: [])
    called = False

    def fake_request(method, url, **kwargs):
        nonlocal called
        called = True
        return None

    monkeypatch.setattr(score_crud, "_request", fake_request)

    deleted = score_crud.delete_score_by_username("missing")

    assert deleted == 0
    assert not called
