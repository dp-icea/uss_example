import httpx
from http import HTTPStatus
from enum import Enum
from uuid import UUID
from typing import Any
from threading import Lock
from fastapi import HTTPException
from pydantic import BaseModel
from config.config import Settings
from services.auth_service import AuthService, Scope, DSS_AUD
from schemas.operational_intent import AreaOfInterestSchema
from schemas.error import ResponseError
from schemas.constraints import ConstraintQueryResponse
from schemas.operational_intent_reference import OperationCreateResponse, OperationQueryResponse

class OperationalIntentState(str, Enum):
    """
    Enum for the operational intent state.
    """
    ACCEPTED = "Accepted"

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
            raise HTTPException(
                status_code=500,
                detail=ResponseError(
                    message="Scope or audience not provided in the request.",
                    data=None,
                ).model_dump(mode="json"),
            )

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

class DSSService:
    _instance = None
    _lock = Lock()

    def __init__(self):
        settings = Settings()
        self._base_url = settings.DSS_URL
        
        if not self._base_url:
            raise ValueError("DSS_URL must be set in the environment variables.")

        print(f"DSS URL: {self._base_url}")

        self._client = AuthClient(aud=DSS_AUD, base_url=self._base_url)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    async def close(self):
        await self._client.aclose()

    async def query_constraint_references(self, area_of_interest: AreaOfInterestSchema) -> ConstraintQueryResponse:
        """
        Query all constraint references from the DSS.
        """
        body = {
            "area_of_interest": area_of_interest.model_dump(mode="json"),
        }

        response = await self._client.request(
            "post",
            "/constraint_references/query",
            scope=Scope.CONSTRAINT_PROCESSING,
            json=body,
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error querying DSS constraint references.",
                    data=response.json(),
                ).model_dump(mode="json"),
            )

        constraint = ConstraintQueryResponse.model_validate(response.json())

        return constraint

    async def query_operational_intents(self, area_of_interest: BaseModel) -> OperationQueryResponse:
        """
        Query all operational intents from the DSS.
        """
        body = {
            "area_of_interest": area_of_interest.model_dump(mode="json"),
        }

        response = await self._client.request(
            "post",
            "/operational_intent_references/query",
            scope=Scope.STRATEGIC_COORDINATION,
            json=body,
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error querying DSS operational intents.",
                    data=response.json(),
                ).model_dump(mode="json"),
            )

        operational_intents = OperationQueryResponse.model_validate(response.json())

        return operational_intents

    async def create_operational_intent(self, entity_id: UUID, area_of_interest: AreaOfInterestSchema) -> OperationCreateResponse:

        """
        Create a new operational intent in the DSS.
        """
        body = {
            "extents": [
                area_of_interest.model_dump(mode="json"),
            ],
            # TODO: Add this when I am solving conflicts
            "key": [],
            "state": OperationalIntentState.ACCEPTED.value,
            "uss_base_url": "https://localhost:8000",
            # TODO: Add this later when supporting already created subscriptions
            # "subscription_id": "foo"
            "new_subscription": {
                    "uss_base_url": "string",
                    "notify_for_constraints": True,
            },
            # TODO: Add this later to support other flight types
            "flight_type": "VLOS",
        }

        response = await self._client.request(
            "put",
            f"/operational_intent_references/{entity_id}",
            scope=Scope.STRATEGIC_COORDINATION,
            json=body,
        )

        if response.status_code != HTTPStatus.CREATED.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error creating operational intent.",
                    data=response.json(),
                ).model_dump(mode="json"),
            )

        operational_intent = OperationCreateResponse.model_validate(response.json())

        return operational_intent


