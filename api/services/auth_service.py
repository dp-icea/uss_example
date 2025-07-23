import httpx
import jwt
from typing import Any
from http import HTTPStatus
from fastapi import HTTPException
from datetime import datetime
from threading import Lock

from schemas.error import ResponseError
from config.config import Settings
from config.logger import MessageLogger
from schema_types.auth import Scope


class AuthAsyncClient(httpx.AsyncClient):
    """
    Custom HTTP client for authentication.
    """

    def __init__(self, aud: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._aud = aud

    async def request(self, method: str, url: httpx.URL | str, **kwargs: Any) -> httpx.Response:
        scope = kwargs.pop("scope", None)

        if scope is None:
            raise ValueError(
                "Scope must be provided in the request for authentication.")

        try:
            MessageLogger.log(
                f"Message Sent",
                data={
                    "method": method,
                    "base_url": str(self.base_url),
                    "url": str(url),
                    "aud": self._aud,
                    "scope": scope,
                    "body": kwargs.get("json", None),
                },
            )

            res = await super().request(
                method,
                url,
                auth=ServiceTokenMiddleware(
                    aud=self._aud,
                    scope=scope
                ),
                **kwargs
            )

            MessageLogger.log(
                f"Response Received",
                data={
                    "status_code": res.status_code,
                    "url": str(res.url),
                    "headers": dict(res.headers),
                    "body": res.json() if res.content else None,
                },
            )

            return res
        except ConnectionRefusedError as e:
            MessageLogger.log(
                f"Connection refused",
                data={
                    "request": {
                        "method": method,
                        "base_url": str(self.base_url),
                        "url": str(url),
                        "aud": self._aud,
                        "scope": scope,
                        "body": kwargs.get("json", None),
                    },
                    "error": str(e),
                },
            )

            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE.value,
                detail=ResponseError(
                    message="Connection refused. The service might be down.",
                    data=str(e),
                ).model_dump(mode="json"),
            )
        except httpx.RequestError as e:
            MessageLogger.log(
                f"Request error",
                data={
                    "request": {
                        "method": method,
                        "base_url": str(self.base_url),
                        "url": str(url),
                        "aud": self._aud,
                        "scope": scope,
                        "body": kwargs.get("json", None),
                    },
                    "error": str(e),
                },
            )

            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                detail=ResponseError(
                    message="Request error occurred.",
                    data=str(e),
                ).model_dump(mode="json"),
            )


class ServiceTokenMiddleware(httpx.Auth):
    def __init__(self, aud: str, scope: Scope) -> None:
        self._aud = aud
        self._scope = scope

    def sync_auth_flow(self, request: httpx.Request):
        raise RuntimeError(
            "This middleware is designed for asynchronous use only. Use async_auth_flow instead.")

    async def async_auth_flow(self, request: httpx.Request):
        auth = AuthService.get_instance()
        token = await auth.get_token(aud=self._aud, scope=self._scope)
        request.headers["Authorization"] = f"Bearer {token}"
        response = yield request
        if response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
            await auth.refresh_token(aud=self._aud, scope=self._scope)
            token = await auth.get_token(aud=self._aud, scope=self._scope)
            request.headers["Authorization"] = f"Bearer {token}"
            yield request


class AuthService:
    _instance = None
    _lock = Lock()

    def __init__(self):
        settings = Settings()

        self._tokens = {}
        self._base_url = settings.AUTH_URL
        self._auth_key = settings.AUTH_KEY

        if not self._base_url or not self._auth_key:
            raise ValueError(
                "AUTH_URL and AUTH_KEY must be set in the environment variables.")

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

        MessageLogger.log(
            f"Requesting new token",
            data={
                "aud": aud,
                "scope": scope.value,
                "params": params,
            },
        )

        response = await self._client.get(
            "/token",
            params=params,
        )

        MessageLogger.log(
            f"Token response received",
            data={
                "status_code": response.status_code,
                "body": response.json() if response.content else None,
            },
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error getting DSS token.",
                    data=response.json() if response.content else None,
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
