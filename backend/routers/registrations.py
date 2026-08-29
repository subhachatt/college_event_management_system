from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.registration import RegistrationResponse, RegistrationDetailResponse
from dependencies import get_current_active_student, get_current_user
from services.registration_service import (
    register_user_for_event, cancel_user_registration, get_user_registrations
)

router = APIRouter(tags=["Registrations"])

@router.post("/api/events/{event_id}/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_for_event(
    event_id: int,
    current_student: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    """
    Student only: Register for an event. Enforces JWT auth, capacity limits, and duplicate registration prevention.
    """
    registration = register_user_for_event(db=db, user_id=current_student.id, event_id=event_id)
    return registration

@router.delete("/api/events/{event_id}/register", status_code=status.HTTP_200_OK)
def cancel_registration(
    event_id: int,
    current_student: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    """
    Student only: Cancel own registration for an event.
    """
    cancel_user_registration(db=db, user_id=current_student.id, event_id=event_id)
    return {"message": "Registration cancelled successfully", "event_id": event_id}

@router.get("/api/my-registrations", response_model=List[RegistrationDetailResponse])
def list_my_registrations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all registered events for the currently authenticated user.
    """
    return get_user_registrations(db=db, user_id=current_user.id)
