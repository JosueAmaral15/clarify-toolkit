"""Regressions for REST API authentication (code-scanning alert #16)."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from src.rest_api import AUTH_TOKEN_ENV, ClarifyAPI


TOKEN = "test-only-token-with-at-least-32-bytes"


@pytest.fixture
def application():
    app = Mock()
    app.get_current_json.return_value = {"private": "document"}
    app.translate_json.return_value = {"translated": True}
    return app


@pytest.fixture
def api(monkeypatch, application):
    monkeypatch.setenv(AUTH_TOKEN_ENV, TOKEN)
    return ClarifyAPI(application)


@pytest.fixture
def client(api):
    with TestClient(api.api) as test_client:
        yield test_client


def _authorization(token=TOKEN):
    return {"Authorization": f"Bearer {token}"}


def test_startup_fails_closed_without_authentication(monkeypatch, application):
    monkeypatch.delenv(AUTH_TOKEN_ENV, raising=False)

    with pytest.raises(RuntimeError, match="authentication is not configured"):
        ClarifyAPI(application)


@pytest.mark.parametrize("token", ["short", "x" * 513, "x" * 31 + " ", "á" * 32])
def test_startup_rejects_weak_or_unsafe_tokens(monkeypatch, application, token):
    monkeypatch.setenv(AUTH_TOKEN_ENV, token)

    with pytest.raises(ValueError, match="32-512 non-whitespace ASCII bytes"):
        ClarifyAPI(application)


def test_remote_bind_requires_explicit_opt_in(monkeypatch, application):
    monkeypatch.setenv(AUTH_TOKEN_ENV, TOKEN)

    with pytest.raises(ValueError, match="allow_remote=True"):
        ClarifyAPI(application, host="0.0.0.0")

    assert ClarifyAPI(application, host="0.0.0.0", allow_remote=True).host == "0.0.0.0"


def test_public_status_is_fixed_and_does_not_access_application(client, application):
    response = client.get("/status")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    application.get_current_json.assert_not_called()
    application.translate_json.assert_not_called()


@pytest.mark.parametrize("headers", [{}, _authorization("wrong-token-with-at-least-32-bytes")])
def test_json_rejects_missing_or_invalid_auth_without_touching_app(
    client, application, headers
):
    response = client.get("/json", headers=headers)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert TOKEN not in response.text
    application.get_current_json.assert_not_called()


def test_json_uses_constant_time_validation_and_returns_document(
    client, application, monkeypatch
):
    compare_digest = Mock(return_value=True)
    monkeypatch.setattr("src.rest_api.secrets.compare_digest", compare_digest)

    response = client.get("/json", headers=_authorization())

    assert response.status_code == 200
    assert response.json() == {"private": "document"}
    compare_digest.assert_called_once_with(TOKEN, TOKEN)
    application.get_current_json.assert_called_once_with()


def test_json_reports_missing_document_only_after_authentication(client, application):
    application.get_current_json.return_value = None

    response = client.get("/json", headers=_authorization())

    assert response.status_code == 404
    assert response.json() == {"detail": "No JSON document is loaded"}


def test_translate_requires_authentication(client, application):
    response = client.post("/translate", json={"json": {"a": 1}, "lang": "pt-BR"})

    assert response.status_code == 401
    application.translate_json.assert_not_called()


def test_translate_rejects_undeclared_fields_before_app_call(client, application):
    response = client.post(
        "/translate",
        headers=_authorization(),
        json={"json": {"a": 1}, "lang": "pt-BR", "provider": "untrusted"},
    )

    assert response.status_code == 422
    application.translate_json.assert_not_called()


def test_translate_forwards_only_validated_fields(client, application):
    payload = {"json": {"a": 1}, "lang": "pt-BR"}

    response = client.post("/translate", headers=_authorization(), json=payload)

    assert response.status_code == 200
    assert response.json() == {"translated": {"translated": True}}
    application.translate_json.assert_called_once_with(payload["json"], payload["lang"])


def test_openapi_marks_only_sensitive_routes_as_authenticated(api):
    schema = api.api.openapi()

    assert "security" not in schema["paths"]["/status"]["get"]
    assert schema["paths"]["/json"]["get"]["security"]
    assert schema["paths"]["/translate"]["post"]["security"]


def test_run_passes_only_listener_configuration_to_uvicorn(api, monkeypatch):
    run = Mock()
    monkeypatch.setattr("src.rest_api.uvicorn.run", run)

    api.run()

    run.assert_called_once_with(api.api, host="127.0.0.1", port=8000)
    assert TOKEN not in repr(run.call_args)
