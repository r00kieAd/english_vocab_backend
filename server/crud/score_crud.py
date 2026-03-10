import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from fastapi import HTTPException
from dotenv import load_dotenv
from pydantic import ValidationError

from schemas.scores import Score, ScoreCreate

_env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_env_path)

_DB_API_URI = os.getenv("DB_API_URI", "").strip()
_SCORE_READ = os.getenv("SCORE_READ", "").strip()
_SCORE_ADD = os.getenv("SCORE_ADD", "").strip()
_SCORE_UPDATED = os.getenv("SCORE_UPDATED", "").strip()

_HTTP_CLIENT = httpx.Client(timeout=10.0)


def _require_env(name: str, value: str) -> str:
    if not value:
        raise RuntimeError(f"{name} environment variable is required for score CRUD")
    return value


def _absolute_url(path: str) -> str:
    base = _require_env("DB_API_URI", _DB_API_URI).rstrip("/")
    trimmed, sep, query = path.partition("?")
    trimmed = trimmed.strip("/")
    url = f"{base}/{trimmed}" if trimmed else base
    if query:
        url = f"{url}?{query}"
    return url


def _format_update_url(record_id: int) -> str:
    template = _require_env("SCORE_UPDATED", _SCORE_UPDATED)
    path_part, _, query = template.partition("?")
    if "{id}" in path_part:
        formatted = path_part.format(id=record_id)
    else:
        trimmed = re.sub(r"/\d+$", "/", path_part).rstrip("/")
        formatted = f"{trimmed}/{record_id}"
    if query:
        formatted = f"{formatted}?{query}"
    return _absolute_url(formatted)


def _extract_records(payload: Any) -> list[dict]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("results", "records", "data"):
            if isinstance(payload.get(key), list):
                return payload[key]
        return [payload]
    return []


def _normalize_record(record: dict) -> dict:
    normalized = dict(record)
    if "date_created" not in normalized and "date_modified" in normalized:
        normalized["date_created"] = normalized["date_modified"]
    if "date_modified" not in normalized and "date_created" in normalized:
        normalized["date_modified"] = normalized["date_created"]
    for attr in ("high_score", "high_scorer"):
        if normalized.get(attr) is None:
            normalized[attr] = _find_value(record, attr)
    for timestamp in ("date_created", "date_modified"):
        parsed = _parse_timestamp(normalized.get(timestamp))
        if parsed is not None:
            normalized[timestamp] = parsed
    return normalized


def _find_value(record: dict, target: str) -> Any | None:
    target_stripped = target.replace("_", "").lower()
    for key, value in record.items():
        if key.replace("_", "").lower() == target_stripped:
            return value
    return record.get(target)


def _find_high_scorer(scores: list[Score], name: str) -> Score | None:
    match = name.strip().lower()
    for score in scores:
        if score.high_scorer.lower() == match:
            return score
    return None


def _parse_timestamp(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if value is None:
        return None
    if isinstance(value, str):
        if re.fullmatch(r"\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2})?", value):
            today = datetime.now().date().isoformat()
            value = f"{today}T{value}"
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return None


def _request(method: str, url: str, **kwargs: Any) -> Any:
    try:
        response = _HTTP_CLIENT.request(method, url, **kwargs)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code or 502
        detail = exc.response.text or "Failed to reach score persistence layer"
        raise HTTPException(status_code=status, detail=detail)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    try:
        return response.json()
    except ValueError:
        return None


def get_all_scores() -> list[Score]:
    url = _absolute_url(_require_env("SCORE_READ", _SCORE_READ))
    payload = _request("GET", url)
    records = _extract_records(payload)
    scores: list[Score] = []
    for record in records:
        normalized = _normalize_record(record)
        try:
            scores.append(Score(**normalized))
        except ValidationError:
            continue
    return sorted(scores, key=lambda s: s.high_score, reverse=True)


def get_top_scores(limit: int = 3) -> list[Score]:
    all_scores = get_all_scores()
    return all_scores[:limit]


def get_high_score() -> Score | None:
    top_scores = get_top_scores(1)
    return top_scores[0] if top_scores else None


def create_score(score: ScoreCreate) -> Score:
    top_scores = get_all_scores()
    existing = _find_high_scorer(top_scores, score.high_scorer)
    if existing:
        if score.high_score <= existing.high_score:
            return existing
        update_url = _format_update_url(existing.id)
        update_payload = {
            "high_score": score.high_score,
            "high_scorer": existing.high_scorer,
        }
        response_data = _request("PUT", update_url, json=update_payload)
        if not isinstance(response_data, dict):
            raise HTTPException(status_code=502, detail="Unexpected response from score API")
        return Score(**_normalize_record(response_data))
    url = _absolute_url(_require_env("SCORE_ADD", _SCORE_ADD))
    payload = score.model_dump()
    response_data = _request("POST", url, json=payload)
    if not isinstance(response_data, dict):
        raise HTTPException(status_code=502, detail="Unexpected response from score API")
    return Score(**_normalize_record(response_data))


def delete_score_by_username(username: str) -> int:
    matches = [
        score for score in get_all_scores()
        if score.high_scorer.lower() == username.lower()
    ]
    if not matches:
        return 0
    for score in matches:
        _request("DELETE", _format_update_url(score.id))
    return len(matches)
