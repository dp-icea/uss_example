from http import HTTPStatus
from typing import Any, List
from enum import Enum
from uuid import UUID
from threading import Lock
from fastapi import HTTPException
from pydantic import BaseModel, HttpUrl
from models.operational_intent import OperationalIntentModel
from config.config import Settings
from config.config import Settings
from services.auth_service import Scope, AuthAsyncClient
from schemas.flight_type import FlightType
from schemas.error import ResponseError
from schemas.constraints import ConstraintQueryResponse
from schemas.operational_intent_reference import OperationCreateResponse, OperationQueryResponse, OperationCreateRequest, NewSubscription

class USSService:
    def __init__(self, base_url: HttpUrl, manager: str):
        settings = Settings()
        self._base_url = str(base_url)
        self._manager = manager
        
        if not self._base_url:
            raise ValueError("Base URL must be provided when initiating an object of USSService.")

        if not self._manager:
            raise ValueError("Manager must be provided when initiating an object of USSService.")

        self._client = AuthAsyncClient(aud=self._manager, base_url=self._base_url)

    async def close(self):
        await self._client.aclose()

    async def query_operational_intent(self, entity_id: UUID) -> OperationalIntentModel:
        """
        Query the operational intent from another USS that owns the entity.
        """

        # TODO: Doesnt make sense for the URL to have `/uss/v1/`
        # how do they upgrade the api system?
        # should be just "/operational_intents/{entity_id}", because
        # then eventually they will start to anounce their request as  /uss/v2/
        response = await self._client.request(
            "get",
            f"/uss/v1/operational_intents/{entity_id}",
            scope=Scope.STRATEGIC_COORDINATION,
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message=f"Error querying USS {self._manager} at {self._base_url} for operational intent.",
                    data=response.json(),
                ).model_dump(mode="json"),
            )

        operational_intent = OperationalIntentModel.model_validate(response.json()["operational_intent"])

        return operational_intent

