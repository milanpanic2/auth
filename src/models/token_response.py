from pydantic import BaseModel


class BearerTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    