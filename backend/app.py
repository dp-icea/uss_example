from fastapi import FastAPI
from routes.test import router as TestRouter
from config.config import init_database

app = FastAPI()

@app.on_event("startup")
async def start_database():
    await init_database()

app.include_router(TestRouter, tags=["Test"], prefix="/test")
