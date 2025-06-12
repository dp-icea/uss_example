from http import HTTPStatus
from uuid import UUID
from fastapi import APIRouter, HTTPException

from config.logger import MessageLogger, OperatorInputLogger, PlanningAttemptLogger
from controllers import constraint as constraint_controller
from schemas.constraint import ConstraintNotificationRequest
from services.dss_service import DSSService
from schema_types.constraint import ConstraintState

router = APIRouter()


# TODO: In the future. Implement a webhook for the client to receive constant updates
@router.get(
    "/",
    response_description="Export operational logs from the USS",
    status_code=HTTPStatus.OK.value,
)
async def export_logs():
    log_types = [MessageLogger, OperatorInputLogger, PlanningAttemptLogger]

    logs = {}

    for log_type in log_types:
        logger = log_type.get_instance()
        logs[logger.NAME] = logger.export()

    return logs
    
