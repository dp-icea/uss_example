from typing import List

from schemas.area_of_interest import AreaOfInterestSchema
from schemas.operational_intent import OperationalIntentReferenceSchema
from services.uss_service import USSService

async def get_operational_intents_volume(operational_intents: List[OperationalIntentReferenceSchema]) -> List[AreaOfInterestSchema]:
    """
    Extracts the volumes from a list of operational intent references.
    """
    volumes: List[AreaOfInterestSchema] = []

    for operational_intent in operational_intents:
        uss = USSService(operational_intent.uss_base_url)
        res = await uss.get_operational_intent(operational_intent.id)
        volumes += res.operational_intent.details.volumes

    return volumes

