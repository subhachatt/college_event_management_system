from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.schemas.event import EventCreate, EventUpdate, EventResponse, EventDetailResponse
from backend.dependencies import get_current_admin, get_optional_current_user
from backend.services.event_service import (
    get_all_events, get_event_by_id, create_event, update_event, delete_event
)

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.get("", response_model=List[EventResponse])
def list_events(
    search: Optional[str] = Query(None, description="Search keyword for title, venue, organizer, description"),
    category: Optional[str] = Query(None, description="Category filter (Technical, Cultural, Sports, etc.)"),
    date_filter: Optional[str] = Query(None, description="Filter: 'upcoming', 'past', or specific 'YYYY-MM-DD'"),
    sort_by: str = Query("date_asc", description="Sort order: 'date_asc' or 'date_desc'"),
    db: Session = Depends(get_db)
):
    """
    Public endpoint: Get all events matching optional search, category, and date filters.
    """
    return get_all_events(db, search=search, category=category, date_filter=date_filter, sort_by=sort_by)

@router.get("/{event_id}", response_model=EventDetailResponse)
def get_event(
    event_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Public/Authenticated endpoint: Get detailed event information including real-time registration stats
    and whether the requesting student is currently registered.
    """
    user_id = current_user.id if current_user else None
    event_detail = get_event_by_id(db, event_id=event_id, user_id=user_id)
    if not event_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event_detail

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def add_event(
    event_in: EventCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin only: Create a new college event.
    """
    return create_event(db, event_in)

@router.put("/{event_id}", response_model=EventResponse)
def modify_event(
    event_id: int,
    event_in: EventUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin only: Update an existing event.
    """
    updated = update_event(db, event_id=event_id, event_in=event_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return updated

@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
def remove_event(
    event_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin only: Delete an event and all associated registrations.
    """
    success = delete_event(db, event_id=event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return {"message": "Event deleted successfully", "event_id": event_id}
