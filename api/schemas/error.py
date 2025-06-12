from pydantic import BaseModel
from typing import Optional, Any

class ResponseError(BaseModel):
    """
    Response class to handle the response from the API.
    """
    message: Optional[str] = None
    data: Optional[Any] = None
