import os
import models

from typing import Optional
from beanie import init_beanie
from pydantic_settings import BaseSettings
from motor.motor_asyncio import AsyncIOMotorClient

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    AUTH_URL: Optional[str] = None
    AUTH_KEY: Optional[str] = None
    DSS_URL: Optional[str] = None
    DOMAIN: Optional[str] = None
    DSS_PEM: Optional[str] = None
    MANAGER: Optional[str] = None

    class Config:
        env_file = f".env.{os.getenv('ENV', 'dev')}"
        from_attributes = True

async def init_database():
    client = AsyncIOMotorClient(Settings().DATABASE_URL)
    await init_beanie(
            database=client.get_default_database(),
            document_models=models.__all__
    )

async def init_auth():
    pass
