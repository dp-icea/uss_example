from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from routes.operational_intent import router as OperationalIntentsRouter
from routes.flight_plan import router as FlightPlanRouter
from auth.auth_check import AuthCheck
from config.config import init_database
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event for the FastAPI application.
    """
    await init_database()
    yield

app = FastAPI(
    title="USS API",
    description="USS example API",
    version="1.0.0",
    lifespan=lifespan,
)

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal Server Error",
                "data": str(e)},
        )

# app.include_router(OperationalIntentsRouter, tags=["Operational Intents"], prefix="/uss/v1/operational_intents", dependencies=[Depends(AuthCheck())])
app.include_router(OperationalIntentsRouter, tags=["Operational Intents"], prefix="/uss/v1/operational_intents", dependencies=[Depends(AuthCheck())])
app.include_router(FlightPlanRouter, tags=["Flight Plan"], prefix="/uss/v1/flight_plan")

