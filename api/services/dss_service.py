from http import HTTPStatus
from typing import List
from uuid import UUID
from fastapi import HTTPException
from typing import List
from pydantic import HttpUrl

from config.config import Settings
from config.logger import MessageLogger
from schema_types.availability import USSAvailability
from schemas.availability import USSAvailabilityRequest, USSAvailabilityResponse
from schemas.constraint import ConstraintSchema
from services.auth_service import AuthAsyncClient
from schema_types.auth import Audition, Scope
from schema_types.flight import FlightType
from schema_types.operational_intent import OperationalIntentState
from schema_types.ovn import ovn
from schema_types.subscription import NewSubscriptionSchema
from schemas.area_of_interest import AreaOfInterestSchema
from schemas.operational_intent import OperationalIntentSchema
from schemas.error import ResponseError
from schemas.report import (
    ExchangeSchema,
    ReportRequest,
    ReportResponse,
)
from schemas.subscription import (
    SubscriptionCreateRequest,
    SubscriptionCreateResponse,
    SubscriptionGetResponse,
)
from schemas.constraint_reference import (
    ConstraintReferenceDeleteResponse,
    ConstraintReferenceQueryResponse,
    ConstraintReferenceQueryRequest,
    ConstraintReferenceCreateRequest,
    ConstraintReferenceCreateResponse,
    ConstraintReferenceUpdateRequest,
    ConstraintReferenceUpdateResponse,
)
from schemas.operational_intent_reference import (
    OperationalIntentReferenceQueryRequest,
    OperationalIntentReferenceQueryResponse,
    OperationalIntentReferenceGetResponse,
    OperationalIntentReferenceCreateRequest,
    OperationalIntentReferenceCreateResponse,
    OperationalIntentReferenceDeleteResponse,
    OperationalIntentReferenceUpdateRequest,
    OperationalIntentReferenceUpdateResponse
)


class DSSService:
    def __init__(self):
        settings = Settings()

        assert settings.DSS_URL, "DSS_URL must be set in the environment variables."
        assert settings.DOMAIN, "DOMAIN must be set in the environment variables."
        assert settings.MANAGER, "MANAGER must be set in the environment variables."

        self._base_url: str = settings.DSS_URL
        self._app_domain: str = settings.DOMAIN
        self._manager: str = settings.MANAGER

        self._client = AuthAsyncClient(
            base_url=self._base_url, aud=Audition.DSS.value)

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
                    data=response.json() if response.content else None,
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
                    data=response.json() if response.content else None,
                ).model_dump(mode="json"),
            )

        return OperationalIntentReferenceQueryResponse.model_validate(response.json())

    async def create_operational_intent(self, entity_id: UUID, area_of_interest: AreaOfInterestSchema, keys: List[str] = []) -> OperationalIntentReferenceCreateResponse:
        """
        Create a new operational intent in the DSS.
        """
        body = OperationalIntentReferenceCreateRequest(
            extents=[
                area_of_interest
            ],
            key=keys,
            state=OperationalIntentState.ACCEPTED.value,
            uss_base_url=HttpUrl(self._app_domain),
            # TODO: Figure out what is a subscription.
            new_subscription=NewSubscriptionSchema(
                uss_base_url=HttpUrl(self._app_domain),
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
                    data=response.json() if response.content else None,
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
                    data=response.json() if response.content else None,
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
                    data=response.json() if response.content else None,
                ).model_dump(mode="json"),
            )

        return OperationalIntentReferenceDeleteResponse.model_validate(response.json())

    async def update_operational_intent_reference(self, entity_id: UUID, ovn: str, keys: List[ovn], operational_intent: OperationalIntentSchema) -> OperationalIntentReferenceUpdateResponse:
        """
        Update the operational intent reference state in the DSS.
        """
        body = OperationalIntentReferenceUpdateRequest(
            extents=operational_intent.details.volumes,
            # TODO: Verify ovns in the area
            key=keys,
            state=operational_intent.reference.state,
            uss_base_url=operational_intent.reference.uss_base_url,
            new_subscription=NewSubscriptionSchema(
                uss_base_url=operational_intent.reference.uss_base_url,
                notify_for_constraints=True,
            ),
            flight_type=operational_intent.reference.flight_type,
        )

        scope = Scope.STRATEGIC_COORDINATION

        if (operational_intent.reference.state == OperationalIntentState.NONCONFORMING):
            scope = Scope.CONFORMANCE_MONITORING_SA

        response = await self._client.request(
            "put",
            f"/operational_intent_references/{entity_id}/{ovn}",
            scope=scope,
            json=body.model_dump(mode="json"),
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error updating operational intent reference in the DSS.",
                    data=response.json() if response.content else None,
                ).model_dump(mode="json"),
            )

        return OperationalIntentReferenceUpdateResponse.model_validate(response.json())

    async def create_constraint_reference(self, entity_id: UUID, areas_of_interest: List[AreaOfInterestSchema]) -> ConstraintReferenceCreateResponse:
        """
        Create a new constraint in the DSS.
        """

        body = ConstraintReferenceCreateRequest(
            extents=areas_of_interest,
            uss_base_url=HttpUrl(self._app_domain),
        )

        response = await self._client.request(
            "put",
            f"/constraint_references/{entity_id}",
            scope=Scope.CONSTRAINT_MANAGEMENT,
            json=body.model_dump(mode="json"),
        )

        if response.status_code != HTTPStatus.CREATED.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error creating constraint in the DSS.",
                    data=response.json() if response.content else None,
                ).model_dump(mode="json"),
            )

        return ConstraintReferenceCreateResponse.model_validate(response.json())

    async def delete_constraint_reference(self, entity_id: UUID, ovn: str) -> ConstraintReferenceDeleteResponse:
        """
        Delete the constraint reference from the DSS.
        """
        response = await self._client.request(
            "delete",
            f"/constraint_references/{entity_id}/{ovn}",
            scope=Scope.CONSTRAINT_MANAGEMENT,
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error deleting constraint reference in the DSS.",
                    data=response.json() if response.content else None,
                ).model_dump(mode="json"),
            )

        return ConstraintReferenceDeleteResponse.model_validate(response.json())

    async def update_constraint_reference(self, entity_id: UUID, ovn: str, constraint: ConstraintSchema) -> ConstraintReferenceUpdateResponse:
        """
        Update the constraint reference in the DSS.
        """

        body = ConstraintReferenceUpdateRequest(
            extents=constraint.details.volumes,
            uss_base_url=HttpUrl(self._app_domain),
        )

        response = await self._client.request(
            "put",
            f"/constraint_references/{entity_id}/{ovn}",
            scope=Scope.CONSTRAINT_MANAGEMENT,
            json=body.model_dump(mode="json"),
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error updating constraint reference in the DSS.",
                    data=response.json() if response.content else None,
                ).model_dump(mode="json"),
            )

        return ConstraintReferenceUpdateResponse.model_validate(response.json())

    async def create_subscription(self, subscription_id: UUID, area_of_interest: AreaOfInterestSchema) -> SubscriptionCreateResponse:
        """
        Create subscription in the DSS.
        """
        body = SubscriptionCreateRequest(
            extents=area_of_interest,
            uss_base_url=HttpUrl(self._app_domain),
            notify_for_constraints=True,
            notify_for_operational_intents=True,
        )

        response = await self._client.request(
            "put",
            f"/subscriptions/{subscription_id}",
            scope=Scope.CONSTRAINT_PROCESSING,
            json=body.model_dump(mode="json"),
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error querying DSS subscriptions.",
                    data=response.json() if response.content else None,
                ).model_dump(mode="json"),
            )

        return SubscriptionCreateResponse.model_validate(response.json())

    async def get_subscription(self, subscription_id: UUID) -> SubscriptionGetResponse:
        """
        Get the subscription details from the DSS.
        """
        response = await self._client.request(
            "get",
            f"/subscriptions/{subscription_id}",
            scope=Scope.CONSTRAINT_PROCESSING,
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error getting subscription from the DSS.",
                    data=response.json() if response.content else None,
                ).model_dump(mode="json"),
            )

        return SubscriptionGetResponse.model_validate(response.json())

    async def set_availability(self, availability: USSAvailability) -> USSAvailabilityResponse:
        """
        Set the USS availability in the DSS.
        """
        body = USSAvailabilityRequest(
            old_version="",
            availability=availability,
        )

        response = await self._client.request(
            "post",
            f"/uss_availability/{self._manager}",
            scope=Scope.AVAILABILITY_ARBITRATION,
            json=body.model_dump(mode="json"),
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error setting USS availability in the DSS.",
                    data=response.json() if response.content else None,
                ).model_dump(mode="json"),
            )

        return USSAvailabilityResponse.model_validate(response.json())

    async def make_report(self, exchange: ExchangeSchema) -> ReportResponse:
        """
        Make a report in the DSS.
        """
        body = ReportRequest(
            report_id=None,
            exchange=exchange,
        )

        response = await self._client.request(
            "post",
            "/reports",
            scope=Scope.CONFORMANCE_MONITORING_SA,
            json=body.model_dump(mode="json"),
        )

        if response.status_code != HTTPStatus.CREATED.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message="Error making report in the DSS.",
                    data=response.json() if response.content else None,
                ).model_dump(mode="json"),
            )

        return ReportResponse.model_validate(response.json())
