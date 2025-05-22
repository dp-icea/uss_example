import httpx
from fastapi import HTTPException
from http import HTTPStatus
from pprint import pprint
from schemas.error import ResponseError
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

        try:
            response = await super().request(method, url, **kwargs)
        except ConnectionRefusedError as e:
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE.value,
                detail=ResponseError(
                    message="Connection refused. The service might be down.",
                    data=str(e),
                ).model_dump(mode="json"),
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                detail=ResponseError(
                    message="Request error occurred.",
                    data=str(e),
                ).model_dump(mode="json"),
            )

        if response.status_code == HTTPStatus.UNAUTHORIZED.value or response.status_code == HTTPStatus.FORBIDDEN.value:
            await auth.refresh_token(aud=self._aud, scope=scope)
            token = await auth.get_token(aud=self._aud, scope=scope)
            headers["Authorization"] = f"Bearer {token}"
            kwargs["headers"] = headers
            response = await super().request(method, url, **kwargs)

        return response
