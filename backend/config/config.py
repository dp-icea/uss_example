from typing import Optional
from beanie import init_beanie
from pydantic_settings import BaseSettings
from motor.motor_asyncio import AsyncIOMotorClient
import models as models

class Settings(BaseSettings):

    DATABASE_URL: Optional[str] = None

    class Config:
        env_file = ".env.dev"
        from_attributes = True

async def init_database():
    client = AsyncIOMotorClient(Settings().DATABASE_URL)
    await init_beanie(
            database=client.get_default_database(),
            document_models=models.__all__
    )
