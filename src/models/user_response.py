from pydantic import BaseModel

class UserResponse(BaseModel):
    email: str
    full_name: str
    displayed_name: str
