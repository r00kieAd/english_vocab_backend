import pytest

from server.llm_client import gemini
from server.schemas.llm_client import ClientResponse


class DummyContent:
    text = "dummy output"


class DummyGoogleAPIError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@pytest.fixture(autouse=True)
def reset_response(monkeypatch):
    # Ensure ClientResponse uses the real class so equality checks remain stable
    monkeypatch.setattr(gemini, "ClientResponse", ClientResponse)


def test_ask_gemini_returns_success(monkeypatch):
    def fake_generate_content(*, model, config, contents):
        return DummyContent()

    monkeypatch.setattr(gemini.client.models, "generate_content", fake_generate_content)

    response = gemini.ask_gemini("prompt", "instruction")

    assert response.status_code == 200
    assert response.details == DummyContent.text


def test_ask_gemini_handles_google_api_error(monkeypatch):
    def raise_api_error(*, model, config, contents):
        raise DummyGoogleAPIError(code=418, message="teapot error")

    monkeypatch.setattr(gemini.client.models, "generate_content", raise_api_error)
    monkeypatch.setattr(gemini.exceptions, "GoogleAPICallError", DummyGoogleAPIError)

    response = gemini.ask_gemini("prompt", "instruction")

    assert response.status_code == 418
    assert response.details == "teapot error"


def test_ask_gemini_handles_unknown_exception(monkeypatch):
    def raise_value_error(*, model, config, contents):
        raise ValueError("boom")

    monkeypatch.setattr(gemini.client.models, "generate_content", raise_value_error)

    response = gemini.ask_gemini("prompt", "instruction")

    assert response.status_code == 500
    assert "[Gemini Error]" in response.details
