from fastapi import APIRouter, Body

from models.test import Test
from schemas.response import Response

router = APIRouter()

@router.post(
    "/",
    response_description="Adding a test data to the database",
    response_model=Response
)
async def add_test_data(test: Test = Body(...)):
    """
    Add test data to the database
    """
    test = await test.create()
    return {
        "status": 200,
        "message": "Test data added successfully",
        "data": test,
    }

@router.get(
    "/ping",
    response_description="Ping the server",
    response_model=Response
)
async def ping():
    """
    Ping the server
    """
    return {
        "status": 200,
        "message": "Pong",
        "data": None,
    }

