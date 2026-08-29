from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

ALLOWED_CATEGORIES = [
    "Technical",
    "Cultural",
    "Sports",
    "Workshop",
    "Seminar",
    "Hackathon",
    "Competition",
    "Other"
]

class EventBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=10)
    category: str = Field(..., min_length=2, max_length=50)
    venue: str = Field(..., min_length=2, max_length=150)
    event_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")        # HH:MM
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")          # HH:MM
    capacity: int = Field(..., gt=0, le=10000)
    image_url: Optional[str] = Field(None, max_length=500)
    organizer: str = Field(..., min_length=2, max_length=150)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in ALLOWED_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(ALLOWED_CATEGORIES)}")
        return v

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    venue: Optional[str] = Field(None, min_length=2, max_length=150)
    event_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    start_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    end_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    capacity: Optional[int] = Field(None, gt=0, le=10000)
    image_url: Optional[str] = Field(None, max_length=500)
    organizer: Optional[str] = Field(None, min_length=2, max_length=150)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(ALLOWED_CATEGORIES)}")
        return v

class EventResponse(EventBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    registered_count: int = 0
    available_seats: int = 0
    is_full: bool = False
    is_past: bool = False

    model_config = {"from_attributes": True}

class EventDetailResponse(EventResponse):
    is_registered: bool = False
    registration_status: Optional[str] = None
