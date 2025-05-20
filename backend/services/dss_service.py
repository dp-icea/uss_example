import httpx
from enum import Enum
from uuid import UUID
from pprint import pprint
from typing import Any
from threading import Lock
from fastapi import HTTPException
from pydantic import BaseModel
from config.config import Settings
from services.auth_service import AuthService, Scope
from schemas.constraints import ConstraintReferenceQuery
from schemas.operational_intent_reference import OperationalIntentReferenceQuery, OperationalIntentReferenceCreate

class OperationalIntentState(str, Enum):
    """
    Enum for the operational intent state.
    """
    ACCEPTED = "Accepted"

class DSSService:
    _instance = None
    _lock = Lock()

    def __init__(self):
        settings = Settings()
        self._base_url = settings.DSS_URL
        
        if not self._base_url:
            raise ValueError("DSS_URL must be set in the environment variables.")

        print(f"DSS URL: {self._base_url}")

        self._client = httpx.AsyncClient(base_url=self._base_url)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    async def close(self):
        await self._client.aclose()

    async def _authenticated_request(self, method: str, scope: Scope, **kwargs) -> httpx.Response:
        auth = AuthService.get_instance()
        token = await auth.get_dss_token(scope=scope)
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"

        request_func = getattr(self._client, method.lower())
        response = await request_func(headers=headers, **kwargs)
        if response.status_code == 403:
            await auth.refresh_dss_token(scope=scope)
            token = await auth.get_dss_token(scope=scope)
            headers["Authorization"] = f"Bearer {token}"
            response = await request_func(headers=headers, **kwargs)
        return response

    # TODO: I am almost solving this (hang on)
    async def _authenticated_post(self, url: str, body: dict, scope: Scope) -> httpx.Response:
        auth = AuthService.get_instance()
        token = await auth.get_dss_token(scope=scope)
        headers = {"Authorization": f"Bearer {token}"}

        response = await self._client.post(url, headers=headers, json=body)
        if response.status_code == 403:
            await auth.refresh_dss_token(scope=scope)
            token = await auth.get_dss_token(scope=scope)
            headers["Authorization"] = f"Bearer {token}"
            response = await self._client.post(url, headers=headers, json=body)
        return response

    async def _authenticated_put(self, url: str, body: dict, scope: Scope) -> httpx.Response:
        auth = AuthService.get_instance()
        token = await auth.get_dss_token(scope=scope)
        headers = {"Authorization": f"Bearer {token}"}

        response = await self._client.put(url, headers=headers, json=body)
        if response.status_code == 403:
            await auth.refresh_dss_token(scope=scope)
            token = await auth.get_dss_token(scope=scope)
            headers["Authorization"] = f"Bearer {token}"
            response = await self._client.put(url, headers=headers, json=body)
        return response

    async def query_constraint_references(self, area_of_interest: BaseModel) -> ConstraintReferenceQuery:
        """
        Query all constraint references from the DSS.
        """
        body = {
            "area_of_interest": area_of_interest.model_dump(mode="json"),
        }

        response = await self._authenticated_request(
            method="post",
            scope=Scope.CONSTRAINT_PROCESSING,
            url="/constraint_references/query",
            json=body,
        )

        if response.status_code != 200: 
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error querying DSS: {response.text}",
            )

        constraint_reference = ConstraintReferenceQuery.model_validate(response.json())

        return constraint_reference

    async def query_operational_intents(self, area_of_interest: BaseModel) -> OperationalIntentReferenceQuery:
        """
        Query all operational intents from the DSS.
        """
        body = {
            "area_of_interest": area_of_interest.model_dump(mode="json"),
        }

        response = await self._authenticated_request(
            method="post",
            scope=Scope.STRATEGIC_COORDINATION,
            url="/operational_intent_references/query",
            json=body,
        )

        if response.status_code != 200: 
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error querying DSS: {response.text}",
            )

        operational_intents = OperationalIntentReferenceQuery.model_validate(response.json())

        return operational_intents

    async def create_operational_intent(self, entity_id: UUID, area_of_interest: BaseModel) -> Any:

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

        response = await self._authenticated_request(
            method="put",
            scope=Scope.STRATEGIC_COORDINATION,
            url=f"/operational_intent_references/{entity_id}",
            json=body,
        )

        print("Response")
        pprint(response.json())

        if response.status_code != 201: 
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error creating operational intent: {response.text}",
            )

        operational_intent = OperationalIntentReferenceCreate.model_validate(response.json())

        return operational_intent


