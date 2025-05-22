from http import HTTPStatus
from typing import Any, List
from enum import Enum
from uuid import UUID
from threading import Lock
from fastapi import HTTPException
from pydantic import BaseModel, HttpUrl
from config.config import Settings
from config.config import Settings
from services.auth_service import Scope, DSS_AUD
from services.auth_client import AuthClient
from schemas.operational_intent import AreaOfInterestSchema
from schemas.flight_type import FlightType
from schemas.error import ResponseError
from schemas.constraints import ConstraintQueryResponse
from schemas.operational_intent_reference import OperationCreateResponse, OperationQueryResponse, OperationCreateRequest, NewSubscription

class OperationalIntentState(str, Enum):
    """
    Enum for the operational intent state.
    """
    ACCEPTED = "Accepted"

class DSSService:
    def __init__(self):
        settings = Settings()
        self._base_url = settings.DSS_URL
        
        if not self._base_url:
            raise ValueError("DSS_URL must be set in the environment variables.")

        self._client = AuthClient(aud=DSS_AUD, base_url=self._base_url)

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

    async def create_operational_intent(self, entity_id: UUID, area_of_interest: AreaOfInterestSchema, keys: List[str]=[]) -> OperationCreateResponse:
        """
        Create a new operational intent in the DSS.
        """
        app_domain = Settings().DOMAIN

        if not app_domain:
            raise ValueError("DOMAIN must be set in the environment variables.")

        body = OperationCreateRequest(
            extents=[
                area_of_interest
            ],
            key=keys,
            state=OperationalIntentState.ACCEPTED.value,
            uss_base_url=HttpUrl(app_domain),
            # TODO: Figure out what is a subscription.
            new_subscription=NewSubscription(
                uss_base_url=HttpUrl(app_domain),
                notify_for_constraints=True,
            ),
            flight_type=FlightType.VLOS.value,
        )

        response = await self._client.request(
            "put",
            f"/operational_intent_references/{entity_id}",
            scope=Scope.STRATEGIC_COORDINATION,
            json=body.model_dump(mode="json"),
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

    async def get_operational_intent_reference(self, entity_id: UUID) -> Any:
        """
        Get the operational intent reference from the DSS.
        """

        response = await self._client.request(
            "get",
            f"/operational_intent_references/{entity_id}",
            scope=Scope.STRATEGIC_COORDINATION,
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error getting operational intent reference.",
                    data=response.json(),
                ).model_dump(mode="json"),
            )

        return response.json() 


