from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes.operational_intent import router as OperationalIntentsRouter
from routes.constraint import router as ConstraintRouter
from routes.flight_plan import router as FlightPlanRouter
from routes.constraint_management import router as ConstraintManagementRouter
from routes.subscription_management import router as SubscriptionManagementRouter
from routes.log_sets import router as LogSetsRouter
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

origins = [
    "http://localhost",
    "http://localhost:9000",
    "http://34.9.130.218/",
]

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Required routers
app.include_router(OperationalIntentsRouter, tags=["Operational Intents"], prefix="/uss/v1/operational_intents", dependencies=[Depends(AuthCheck())])
app.include_router(ConstraintRouter, tags=["Constraints"], prefix="/uss/v1/constraints", dependencies=[Depends(AuthCheck())])
app.include_router(LogSetsRouter, tags=["Log Sets"], prefix="/uss/v1/log_sets")

# Operator router
app.include_router(FlightPlanRouter, tags=["Flight Plan"], prefix="/uss/v1/flight_plan")
app.include_router(ConstraintManagementRouter, tags=["Constraint Management"], prefix="/uss/v1/constraint_management")
app.include_router(SubscriptionManagementRouter, tags=["Subscription Management"], prefix="/uss/v1/subscription_management")

