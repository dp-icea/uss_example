from typing import List

from schemas.area_of_interest import AreaOfInterestSchema
from services.uss_service import USSService
from schemas.constraint import ConstraintReferenceSchema

async def get_constraints_volume(constraints: List[ConstraintReferenceSchema]) -> List[AreaOfInterestSchema]:
    """
    Extracts the volumes from a list of constraint references.
    """
    volumes: List[AreaOfInterestSchema] = []

    for constraint in constraints:
        uss = USSService(constraint.uss_base_url)
        res =  await uss.get_constraint(constraint.id)
        volumes += res.constraint.details.volumes

    return volumes

