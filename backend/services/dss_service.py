from http import HTTPStatus
from typing import List
from uuid import UUID
from fastapi import HTTPException
from pydantic import HttpUrl

from config.config import Settings
from config.config import Settings
from services.auth_service import AuthAsyncClient
from schema_types.auth import Audition, Scope
from schema_types.flight import FlightType
from schema_types.operational_intent import OperationalIntentState
from schemas.operational_intent import AreaOfInterestSchema
from schemas.error import ResponseError
from schemas.constraint_reference import (
    ConstraintReferenceQueryResponse,
    ConstraintReferenceQueryRequest
)
from schemas.operational_intent_reference import (
    OperationalIntentReferenceQueryRequest,
    OperationalIntentReferenceQueryResponse,
    NewSubscription,
    OperationalIntentReferenceGetResponse,
    OperationalIntentReferenceCreateRequest,
    OperationalIntentReferenceCreateResponse,
    OperationalIntentReferenceDeleteResponse,
)

class DSSService:
    def __init__(self):
        settings = Settings()
        self._base_url = settings.DSS_URL
        
        if not self._base_url:
            raise ValueError("DSS_URL must be set in the environment variables.")

        self._client = AuthAsyncClient(base_url=self._base_url, aud=Audition.DSS.value)

    async def close(self):
        await self._client.aclose()

    async def query_constraint_references(self, area_of_interest: AreaOfInterestSchema) -> ConstraintReferenceQueryResponse:
            
        """
        Query all constraint references from the DSS.
        """
        body = ConstraintReferenceQueryRequest(
            area_of_interest=area_of_interest,
        )

        response = await self._client.request(
            "post",
            "/constraint_references/query",
            scope=Scope.CONSTRAINT_PROCESSING,
            json=body.model_dump(mode="json"),
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error querying DSS constraint references.",
                    data=response.json(),
                ).model_dump(mode="json"),
            )

        return ConstraintReferenceQueryResponse.model_validate(response.json())

    async def query_operational_intent_references(self, area_of_interest: AreaOfInterestSchema) -> OperationalIntentReferenceQueryResponse:
        """
        Query all operational intents from the DSS.
        """
        body = OperationalIntentReferenceQueryRequest(
                area_of_interest=area_of_interest,
        )

        response = await self._client.request(
            "post",
            "/operational_intent_references/query",
            scope=Scope.STRATEGIC_COORDINATION,
            json=body.model_dump(mode="json"),
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error querying DSS operational intents.",
                    data=response.json(),
                ).model_dump(mode="json"),
            )

        return OperationalIntentReferenceQueryResponse.model_validate(response.json())

    async def create_operational_intent(self, entity_id: UUID, area_of_interest: AreaOfInterestSchema, keys: List[str]=[]) -> OperationalIntentReferenceCreateResponse:
        """
        Create a new operational intent in the DSS.
        """
        app_domain = Settings().DOMAIN

        if not app_domain:
            raise ValueError("DOMAIN must be set in the environment variables.")

        body = OperationalIntentReferenceCreateRequest(
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

        return OperationalIntentReferenceCreateResponse.model_validate(response.json())

    async def get_operational_intent_reference(self, entity_id: UUID) -> OperationalIntentReferenceGetResponse:
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

        return OperationalIntentReferenceGetResponse.model_validate(response.json())

    async def delete_operational_intent_reference(self, entity_id: UUID, ovn: str) -> OperationalIntentReferenceDeleteResponse:
        """
        Delete the operational intent reference from the DSS.
        """
        response = await self._client.request(
            "delete",
            f"/operational_intent_references/{entity_id}/{ovn}",
            scope=Scope.STRATEGIC_COORDINATION,
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error deleting operational intent reference in the DSS.",
                    data=response.json(),
                ).model_dump(mode="json"),
            )

        
        return OperationalIntentReferenceDeleteResponse.model_validate(response.json())


