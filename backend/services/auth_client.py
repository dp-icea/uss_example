import httpx
from http import HTTPStatus
from typing import Any
from services.auth_service import AuthService

class AuthClient(httpx.AsyncClient):
    """
    Custom HTTP client for authentication.
    """
    def __init__(self, aud: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._aud = aud
    
    async def request(self, method: str, url: httpx.URL | str, **kwargs: Any) -> httpx.Response:
        auth = AuthService.get_instance()
        scope = kwargs.pop("scope", None)
        
        if scope is None:
            raise ValueError("Scope must be provided in the request for authentication.")

        token = await auth.get_token(aud=self._aud, scope=scope)
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        kwargs["headers"] = headers
        response = await super().request(method, url, **kwargs)

        if response.status_code == HTTPStatus.UNAUTHORIZED.value or response.status_code == HTTPStatus.FORBIDDEN.value:
            await auth.refresh_token(aud=self._aud, scope=scope)
            token = await auth.get_token(aud=self._aud, scope=scope)
            headers["Authorization"] = f"Bearer {token}"
            kwargs["headers"] = headers
            response = await super().request(method, url, **kwargs)

        return response
