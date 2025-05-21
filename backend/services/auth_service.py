import httpx
import jwt
from fastapi import HTTPException
from datetime import datetime
from threading import Lock
from config.config import Settings
from enum import Enum

DSS_AUD = "dss"

class Scope(str, Enum):
    CONSTRAINT_PROCESSING = "utm.constraint_processing"
    STRATEGIC_COORDINATION = "utm.strategic_coordination"
    CONSTRAINT_MANAGEMENT = "utm.constraint_management"

class AuthService:
    _instance = None
    _lock = Lock()

    def __init__(self):
        settings = Settings()

        self._tokens = {}
        self._base_url = settings.AUTH_URL
        self._auth_key = settings.AUTH_KEY
        
        if not self._base_url or not self._auth_key:
            raise ValueError("AUTH_URL and AUTH_KEY must be set in the environment variables.")

        self._client = httpx.AsyncClient(base_url=self._base_url)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    async def get_token(self, aud: str, scope: Scope = Scope.CONSTRAINT_PROCESSING) -> str:
        if aud != DSS_AUD:
            raise HTTPException(
                status_code=400,
                detail="Invalid audience. Only DSS communication is supported so far.",
            )

        if DSS_AUD not in self._tokens or scope not in self._tokens[DSS_AUD] or not self._is_token_valid(self._tokens[DSS_AUD][scope]):
            await self.refresh_token(aud=aud, scope=scope)

        return self._tokens[DSS_AUD][scope]

    async def refresh_token(self, aud: str, scope: Scope = Scope.CONSTRAINT_PROCESSING):
        if aud != DSS_AUD:
            raise HTTPException(
                status_code=400,
                detail="Invalid audience. Only DSS communication is supported so far.",
            )

        if DSS_AUD not in self._tokens or scope not in self._tokens[DSS_AUD] or not self._is_token_valid(self._tokens[DSS_AUD][scope]):
            await self.refresh_dss_token(scope = scope)

    def _is_token_valid(self, token: str) -> bool:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = payload.get("exp", None)
        if exp is None:
            return False
        exp = datetime.fromtimestamp(exp)
        now = datetime.now()

        if exp >= now:
            return True

        return False

    async def refresh_dss_token(self, scope: Scope = Scope.CONSTRAINT_PROCESSING):
        params = {
            # TODO: Ask for the reason of this intended_audience
            "intended_audience": "localhost",
            "scope": scope.value,
            "apikey": self._auth_key,
            "grant_type": "client_credentials"
        }

        response = await self._client.get(
            "/token",
            params=params,
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error getting DSS token: {response.text}",
            )

        if DSS_AUD not in self._tokens:
            self._tokens[DSS_AUD] = {}

        self._tokens[DSS_AUD][scope] = response.json().get("access_token")

    async def close(self):
        await self._client.aclose()
