from http import HTTPStatus
from uuid import UUID
from fastapi import HTTPException
from pprint import pprint
from typing import Optional, List
from pydantic import HttpUrl

from config.config import Settings
from config.config import Settings
from schemas.constraint import ConstraintGetResponse, ConstraintNotificationRequest, ConstraintSchema
from services.auth_service import AuthAsyncClient
from schemas.report import (
    ExchangeSchema,
    ReportRequest,
    ReportResponse,
)
from schemas.operational_intent import (
    OperationalIntentGetResponse, 
    OperationalIntentSchema,
    OperationalIntentNotificationRequest,
)
from schemas.error import ResponseError
from schema_types.subscription import SubscriptionBaseSchema
from schema_types.auth import Scope

class USSService:
    def __init__(self, base_url: HttpUrl):
        self._base_url = str(base_url)
        self._aud = base_url.host
        
        if not self._base_url:
            raise ValueError("Base URL must be provided when initiating an object of USSService.")

        if not self._aud:
            raise ValueError("Manager must be provided when initiating an object of USSService.")

        self._client = AuthAsyncClient(aud=self._aud, base_url=self._base_url)

    async def close(self):
        await self._client.aclose()

    async def get_operational_intent(self, entity_id: UUID) -> OperationalIntentGetResponse:
        """
        Query the operational intent from another USS that owns the entity.
        """

        response = await self._client.request(
            "get",
            f"/uss/v1/operational_intents/{entity_id}",
            scope=Scope.STRATEGIC_COORDINATION,
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message=f"Error querying USS {self._aud} at {self._base_url} for operational intent.",
                    data=response.json() if response.content else None,
                ).model_dump(mode="json"),
            )

        pprint(response.json())
        return OperationalIntentGetResponse.model_validate(response.json())

    async def get_constraint(self, entity_id: UUID) -> ConstraintGetResponse:
        """
        Query the constraint from another USS that owns the entity.
        """

        response = await self._client.request(
            "get",
            f"/uss/v1/constraints/{entity_id}",
            scope=Scope.CONSTRAINT_PROCESSING,
        )

        if response.status_code != HTTPStatus.OK.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message=f"Error querying USS {self._aud} at {self._base_url} for constraint.",
                    data=response.json() if response.content else None,
                ).model_dump(mode="json"),
            )

        pprint(response.json())

        return ConstraintGetResponse.model_validate(response.json())

    async def notify_operational_intent(self, subscriptions: List[SubscriptionBaseSchema], operational_intent_id: UUID, operational_intent: Optional[OperationalIntentSchema]) -> None:
        """
        Notify the USS about an operational intent.
        """

        body = OperationalIntentNotificationRequest(
            operational_intent_id=operational_intent_id,
            operational_intent=operational_intent,
            subscriptions=subscriptions,
        )

        response = await self._client.request(
            "post",
            "/uss/v1/operational_intents/",
            json=body.model_dump(mode="json"),
            scope=Scope.STRATEGIC_COORDINATION,
        )

        if response.status_code != HTTPStatus.NO_CONTENT.value:
            # Print the raw response for debugging purposes
            print(f"Response content: {response.headers}")

            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message=f"Error notifying USS {self._aud} at {self._base_url} about operational intent.",
                    data=response.json() if response.content else None,
                ).model_dump(mode="json"),
            )

    async def notify_constraint(self, subscriptions: List[SubscriptionBaseSchema], constraint_id: UUID, constraint: Optional[ConstraintSchema]) -> None:
        """
        Notify the USS about an operational intent.
        """

        body = ConstraintNotificationRequest(
            constraint_id=constraint_id,
            constraint=constraint,
            subscriptions=subscriptions,
        )

        response = await self._client.request(
            "post",
            "/uss/v1/constraints/",
            json=body.model_dump(mode="json"),
            scope=Scope.CONSTRAINT_MANAGEMENT,
        )

        if response.status_code != HTTPStatus.NO_CONTENT.value:
            raise HTTPException(
                status_code=response.status_code,
                detail=ResponseError(
                    message=f"Error notifying USS {self._aud} at {self._base_url} about operational intent.",
                    data=response.json() if response.content else None,
                ).model_dump(mode="json"),
            )

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
            "/uss/v1/reports/",
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

