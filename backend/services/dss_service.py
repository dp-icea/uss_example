import httpx
from pprint import pprint
from typing import Any
from threading import Lock
from fastapi import HTTPException
from pydantic import BaseModel
from config.config import Settings
from services.auth_service import AuthService, Scope
from schemas.constraints import ConstraintReferenceQuery

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

    # I dont like making this method
    # I would like to make this 403 check as something like a middleware
    # TODO: Find a solution later
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

    async def query_constraint_references(self, area_of_interest: BaseModel) -> ConstraintReferenceQuery:
        """
        Query all constraint references from the DSS.
        """
        body = {
            "area_of_interest": area_of_interest.model_dump(mode="json"),
        }

        response = await self._authenticated_post(
            "/constraint_references/query",
            body=body,
            scope=Scope.CONSTRAINT_PROCESSING,
        )

        if response.status_code != 200: 
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error querying DSS: {response.text}",
            )

        constraint_reference = ConstraintReferenceQuery.model_validate(response.json())

        return constraint_reference


