import httpx
from pprint import pprint
from typing import Any
from threading import Lock
from pydantic import BaseModel
from config.config import Settings
from services.auth_service import AuthService, DSS_AUD

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

    async def query_all_constraint_references(self, area_of_interest: BaseModel):
        """
        Query all constraint references from the DSS.
        """
        token = await AuthService.get_instance().get_dss_token()

        headers = {
            "Authorization": f"Bearer {token}",
        }

        print(headers)

        body = {
            "area_of_interest": area_of_interest.model_dump(mode="json"),
        }

        pprint(body)

        response = await self._client.post(
            "/constraint_references/query",
            headers=headers,
            json=body,
        )

        return response


