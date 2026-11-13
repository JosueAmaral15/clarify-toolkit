"""
Clarify REST API Module

FastAPI-based REST API for Clarify application.
Provides endpoints for status, JSON operations, and GUI control.
"""
# pylint: disable=import-error  # fastapi/uvicorn optional dependencies
# pylint: disable=missing-class-docstring  # API class is self-explanatory
# pylint: disable=missing-function-docstring  # FastAPI route decorators are self-documenting

import ipaddress
import os
import secrets
from threading import Thread

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field
import uvicorn


AUTH_TOKEN_ENV = "CLARIFY_API_TOKEN"
MIN_AUTH_TOKEN_BYTES = 32
MAX_AUTH_TOKEN_BYTES = 512
_BEARER_AUTH = HTTPBearer(auto_error=False)


class TranslationRequest(BaseModel):
    """Strict request accepted by the translation endpoint."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    json_payload: object = Field(alias="json")
    lang: str = Field(min_length=1, max_length=32, pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class ClarifyAPI(Thread):
    def __init__(
        self,
        app,
        host: str = "127.0.0.1",
        port: int = 8000,
        *,
        allow_remote: bool = False,
        token_env: str = AUTH_TOKEN_ENV,
    ):
        super().__init__(daemon=True)
        self._validate_bind(host, allow_remote)
        self.app = app
        self.host = host
        self.port = port
        self._auth_token = self._load_auth_token(token_env)
        self.api = FastAPI(title="Clarify REST API")
        self._setup_routes()

    @staticmethod
    def _validate_bind(host: str, allow_remote: bool) -> None:
        normalized = host.strip().lower()
        try:
            is_loopback = normalized == "localhost" or ipaddress.ip_address(normalized).is_loopback
        except ValueError:
            is_loopback = normalized == "localhost"
        if not is_loopback and not allow_remote:
            raise ValueError("Remote REST API binding requires allow_remote=True")

    @staticmethod
    def _load_auth_token(token_env: str) -> str:
        token = os.environ.get(token_env)
        if token is None:
            raise RuntimeError(
                f"REST API authentication is not configured; set {token_env} before startup"
            )
        encoded = token.encode("utf-8")
        if (
            not token.isascii()
            or any(character.isspace() or ord(character) < 33 for character in token)
            or not MIN_AUTH_TOKEN_BYTES <= len(encoded) <= MAX_AUTH_TOKEN_BYTES
        ):
            raise ValueError(
                "REST API authentication token must be 32-512 non-whitespace ASCII bytes"
            )
        return token

    def _require_authentication(
        self,
        credentials: HTTPAuthorizationCredentials | None = Depends(_BEARER_AUTH),
    ) -> None:
        supplied = credentials.credentials if credentials is not None else ""
        valid_scheme = credentials is not None and credentials.scheme.lower() == "bearer"
        if not valid_scheme or not secrets.compare_digest(supplied, self._auth_token):
            raise HTTPException(
                status_code=401,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def _setup_routes(self):
        @self.api.get("/status")
        def status():
            return {"status": "ok"}

        @self.api.get("/json", dependencies=[Depends(self._require_authentication)])
        def get_json():
            data = self.app.get_current_json()
            if data is None:
                raise HTTPException(status_code=404, detail="No JSON document is loaded")
            return JSONResponse(content=data)

        @self.api.post("/translate", dependencies=[Depends(self._require_authentication)])
        def translate(payload: TranslationRequest):
            return {"translated": self.app.translate_json(payload.json_payload, payload.lang)}

    def run(self):
        uvicorn.run(self.api, host=self.host, port=self.port)
