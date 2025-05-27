from typing import Set
from http import HTTPStatus
from uuid import UUID
from datetime import timedelta
from fastapi import APIRouter

from utils.parse_dict import parse_dict
import controllers.operational_intent as operational_intent_controller
from services.dss_service import DSSService
from schemas.operational_intent import OperationalIntentNotificationRequest
from schema_types.operational_intent import OperationalIntentState

router = APIRouter()

@router.post(
    "/",
    response_description="Receive notification of changed operational details",
    status_code=HTTPStatus.NO_CONTENT.value,
)
async def handle_operational_intent_notification(
    notification: OperationalIntentNotificationRequest,
):
    """
    Receive notification of changed operational details
    """

    # Check if the entity ID existsds
    dss = DSSService()

    # Verify if the Operation should be deleted
    if notification.operational_intent is None:
        operational_intent = await operational_intent_controller.get_operational_intent(
            entity_id=notification.operational_intent_id,
        )

        # Delete the opreational intent from the DSS database
        # TODO: Notify the subscribers from the deleted operation area
        _ = await dss.delete_operational_intent_reference(
            entity_id=operational_intent.reference.id,
            ovn=operational_intent.reference.ovn,
        )

        await operational_intent_controller.delete_operational_intent(
            entity_id=operational_intent.reference.id,
        )

        return

    updated_operational_intent = notification.operational_intent

    operational_intent_reference_updated = await dss.update_operational_intent_reference(
        entity_id=notification.operational_intent_id,
        ovn=updated_operational_intent.reference.ovn,
        keys=[],
        operational_intent=updated_operational_intent,
    )

    updated_operational_intent.reference = operational_intent_reference_updated.operational_intent_reference

    await operational_intent_controller.update_operational_intent(
        entity_id=notification.operational_intent_id,
        operational_intent=updated_operational_intent,
    )


# TODO: Add a Depends function to validate the aud parameter in the JWT tokenm 
#   and validating the signature with the public key
# So far it is not validating the token
@router.get(
    "/{entity_id}",
    response_description="Retrieve the specified operational intent details",
    response_model=dict,
    status_code=HTTPStatus.OK.value,
)
async def get_operational_intent(
    entity_id: UUID,
):
    """
    Retrieve the specified operational intent details
    """

    operational_intent = await operational_intent_controller.get_operational_intent(
        entity_id=entity_id,
    )

    return {
        "operational_intent": operational_intent.model_dump(mode="json"),
    }

# TODO: Figure out correctly how to inform the USS about real-time telemetry
# Currently informing the position of the first geometry registered in the area object
@router.get(
    "/{entity_id}/telemetry",
    response_description="Query detailed information on the position of an off-nominal operational intent from a USS",
    response_model=dict,
    status_code=HTTPStatus.OK.value,
)
async def get_operational_intent_telemetry(
    entity_id: UUID,
):
    """
    Query detailed information on the position of an off-nominal operational intent from a USS
    """

    operational_intent = await operational_intent_controller.get_operational_intent(
        entity_id=entity_id,
    )

    details = operational_intent.details.model_dump(mode="json")
    lng = parse_dict(details, "lng")
    lat = parse_dict(details, "lat")
    altitude_lower = parse_dict(details, "altitude_lower")

    return {
        "operational_intent_id": operational_intent.reference.id,
        "telemetry": {
            "time_measured": operational_intent.reference.time_start,
            "position": {
                "longitude": lng,
                "latitude": lat,
                "accuracy_h": "HAUnknown",
                "accuracy_v": "VAUnknown",
                "extrapolate": False,
                "altitude": altitude_lower,
            },
            "velocity": {
                "speed": 0,
                "units_speed": "MetersPerSecond",
                "track": 120,
            }
        },
        "next_telemetry_opportunity": {
            "value": operational_intent.reference.time_start.value + timedelta(seconds = 10),
            "format": operational_intent.reference.time_start.format,
        },
    }

@router.get(
    "/{entity_id}/authorization",
    response_description="Query information of the flight authorization linked with this operational intent",
    response_model=dict,
    status_code=HTTPStatus.OK.value,
)
async def get_operational_intent_authorization(
    entity_id: UUID,
):
    """
    Query information of the flight authorization linked with this operational intent
    """

    operational_intent = await operational_intent_controller.get_operational_intent(
        entity_id=entity_id,
    )

    # TODO: Change this when I create my own auth system for the USS
    return {
        "issued_by": operational_intent.reference.manager,
        "issued_to": {
            "cnpj": "00394429010840",
            "razao_social": "COMANDO DA AERONAUTICA",
            "nome_fantasia": "INSTITUTO DE CONTROLE DO ESPACO AEREO - ICEA",
        },
        "operation_profile": "Padrão",
        "operators": [
            "HUKMBB",
        ],
        "aircraft": "PP-000000000",
        "contigency_strategy": "Return to Home (RTH)",
        "timestamp": 1,
        "observations": "",
    }
