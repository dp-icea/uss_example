import httpx
import jwt
from fastapi import HTTPException
from datetime import datetime
from threading import Lock
from schemas.error import ResponseError
from config.config import Settings
from enum import Enum

DSS_AUD = "core-service"

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
        if aud not in self._tokens or scope not in self._tokens[aud] or not self._is_token_valid(self._tokens[aud][scope]):
            await self.refresh_token(aud=aud, scope=scope)

        return self._tokens[aud][scope]

    async def refresh_token(self, aud: str, scope: Scope = Scope.CONSTRAINT_PROCESSING):
        params = {
            "intended_audience": aud,
            "scope": scope.value,
            "apikey": self._auth_key,
        }

        response = await self._client.get(
            "/token",
            params=params,
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error getting DSS token.",
                    data=response.json(),
                ).model_dump(mode="json"),
            )

        if aud not in self._tokens:
            self._tokens[aud] = {}

        self._tokens[aud][scope] = response.json().get("access_token")

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

