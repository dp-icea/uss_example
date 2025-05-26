from pydantic import BaseModel, HttpUrl

class NewSubscription(BaseModel):
    uss_base_url: HttpUrl
    notify_for_constraints: bool
