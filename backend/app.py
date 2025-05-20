from fastapi import FastAPI
from routes.test import router as TestRouter
from routes.operational_intent import router as OperationalIntentsRouter
from config.config import init_database
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event for the FastAPI application.
    """
    await init_database()
    yield
    # Close the database connection if needed
    # await close_database_connection()


app = FastAPI(
    title="USS API",
    description="USS example API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(TestRouter, tags=["Test"], prefix="/test")
app.include_router(OperationalIntentsRouter, tags=["Operational Intents"], prefix="/uss/v1/operational_intents")

