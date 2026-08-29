from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class RegistrationByEvent(BaseModel):
    event_id: int
    title: str
    category: str
    capacity: int
    registrations: int

class EventsByCategory(BaseModel):
    category: str
    count: int

class AdminDashboardStats(BaseModel):
    total_students: int
    total_events: int
    upcoming_events: int
    total_registrations: int
    active_registrations: int
    registrations_by_event: List[RegistrationByEvent]
    events_by_category: List[EventsByCategory]

class ParticipantResponse(BaseModel):
    registration_id: int
    user_id: int
    student_name: str
    student_id: Optional[str] = None
    email: str
    department: Optional[str] = None
    registration_date: datetime
    status: str

    model_config = {"from_attributes": True}

class EventParticipantsSummary(BaseModel):
    event_id: int
    title: str
    capacity: int
    total_participants: int
    participants: List[ParticipantResponse]
