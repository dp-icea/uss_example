import jwt

from http import HTTPStatus
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from config.config import Settings
from schemas.error import ResponseError

class AuthCheck(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials = await super().__call__(request)
        key_filename = Settings().DSS_PEM
        manager = Settings().MANAGER

        if not key_filename:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=ResponseError(
                    message="DSS_PEM must be an environment variable assigned",
                    data=None,
                ).model_dump(mode="json"),
            )

        if not manager:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=ResponseError(
                    message="MANAGER must be an environment variable assigned",
                    data=None,
                ).model_dump(mode="json"),
            )
        
        with open(key_filename, "rb") as key_file:
            pub_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )

        try:
            jwt.decode(credentials.credentials, pub_key, audience=manager, algorithms=['RS256', ])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=ResponseError(
                    message="Token expired",
                    data=None,
                ).model_dump(mode="json"),
            )
        except jwt.InvalidAudienceError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=ResponseError(
                    message="Invalid audience",
                    data=None,
                ).model_dump(mode="json"),
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=ResponseError(
                    message=f"Invalid token: {str(credentials.credentials)}",
                    data=None,
                ).model_dump(mode="json"),
            )
