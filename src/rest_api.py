"""
Clarify REST API Module

FastAPI-based REST API for Clarify application.
Provides endpoints for status, JSON operations, and GUI control.
"""
# pylint: disable=import-error  # fastapi/uvicorn optional dependencies
# pylint: disable=missing-class-docstring  # API class is self-explanatory
# pylint: disable=missing-function-docstring  # FastAPI route decorators are self-documenting

from threading import Thread
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

class ClarifyAPI(Thread):
    def __init__(self, app, host='127.0.0.1', port=8000):
        super().__init__(daemon=True)
        self.app = app
        self.host = host
        self.port = port
        self.api = FastAPI()
        self._setup_routes()

    def _setup_routes(self):
        @self.api.get("/status")
        def status():
            return {"status": "ok"}

        @self.api.get("/json")
        def get_json():
            data = self.app.get_current_json()
            if data is None:
                raise HTTPException(status_code=404, detail="Nenhum JSON carregado.")
            return JSONResponse(content=data)

        @self.api.post("/translate")
        def translate(payload: dict):
            # Example: delegates to app function
            return {"translated": self.app.translate_json(payload.get("json"), payload.get("lang"))}

    def run(self):
        uvicorn.run(self.api, host=self.host, port=self.port)
