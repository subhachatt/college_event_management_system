from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from schemas.event import EventResponse
from schemas.user import UserResponse

class RegistrationCreate(BaseModel):
    event_id: int

class RegistrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    registration_date: datetime
    status: str

    model_config = {"from_attributes": True}

class RegistrationDetailResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    registration_date: datetime
    status: str
    event: EventResponse
    user: Optional[UserResponse] = None

    model_config = {"from_attributes": True}
