import httpx
from threading import Lock
from config.config import Settings

DSS_AUD = "dss"

class AuthService:
    _instance = None
    _lock = Lock()

    def __init__(self):
        settings = Settings()

        self._tokens = {
            DSS_AUD: None,
        }

        self._base_url = settings.AUTH_URL
        self._auth_key = settings.AUTH_KEY
        
        if not self._base_url or not self._auth_key:
            raise ValueError("AUTH_URL and AUTH_KEY must be set in the environment variables.")

        self._client = httpx.AsyncClient(base_url=self._base_url)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    async def get_dss_token(self):
        if not self._tokens[DSS_AUD]:
            await self.refresh_dss_token()
        return self._tokens[DSS_AUD]

    async def refresh_dss_token(self):
        params = {
            # TODO: Ask for the reason of this intended_audience
            "intended_audience": "localhost",
            # TODO: Manage those two scopes
            "scope": "utm.constraint_processing",
            # "scope": "utm.strategic_coordination",
            "apikey": self._auth_key,
            "grant_type": "client_credentials"
        }

        response = await self._client.get(
            "/token",
            params=params,
        )

        if response.status_code == 200:
            self._tokens[DSS_AUD] = response.json().get("access_token")

    async def close(self):
        await self._client.aclose()
