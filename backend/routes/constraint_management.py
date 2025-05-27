from http import HTTPStatus
from uuid import uuid4, UUID
from typing import List
from fastapi import APIRouter, HTTPException

from models.constraint import ConstraintModel
from schemas.response import Response
from schemas.constraint import ConstraintDetailSchema
from schemas.area_of_interest import AreaOfInterestSchema
from controllers import constraint as constraint_controller
from services.dss_service import DSSService

router = APIRouter()

DEFAULT_CONSTRAINT_TYPE = "uss.icea.non_utm_aircraft_operations"

@router.put(
    "/",
    response_description="Add a new constraint",
    status_code=HTTPStatus.CREATED.value,
)
async def add_constraint(
    areas_of_interest: List[AreaOfInterestSchema]
):

    entity_id = uuid4()

    dss = DSSService()
    constraint_created = await dss.create_constraint_reference(
        entity_id=entity_id,
        areas_of_interest=areas_of_interest,
    )

    constraint_model = ConstraintModel(
        reference=constraint_created.constraint_reference,
        details= ConstraintDetailSchema(
            volumes=areas_of_interest,
            # TODO: Verify the usage those two fields
            type=DEFAULT_CONSTRAINT_TYPE,
            geozone=None,
        ),
    )

    # TODO: Implement
    await constraint_controller.create_constraint(
        constraint=constraint_model
    )

    return Response(
        status=HTTPStatus.CREATED.value,
        message="Constraint created successfully.",
        data=constraint_created.model_dump(mode="json"),
    )

