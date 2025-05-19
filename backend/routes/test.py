from fastapi import APIRouter, Body

from models.test import Test

router = APIRouter()

@router.post(
    "/",
    response_description="Adding a test data to the database",
)
async def add_test_data(test: Test = Body(...)):
    """
    Add test data to the database
    """
    test = await test.create()
    return {
        "message": "Test data added successfully",
        "data": test,
    }
