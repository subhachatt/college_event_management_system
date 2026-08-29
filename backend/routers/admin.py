from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from database import get_db
from models.user import User
from models.event import Event
from models.registration import Registration
from schemas.admin import AdminDashboardStats, RegistrationByEvent, EventsByCategory, EventParticipantsSummary, ParticipantResponse
from schemas.user import UserResponse
from dependencies import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/dashboard", response_model=AdminDashboardStats)
def get_admin_dashboard_stats(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin only: Get aggregated statistics and analytics for the admin dashboard.
    """
    total_students = db.query(User).filter(User.role == "STUDENT").count()
    total_events = db.query(Event).count()

    today_str = date.today().isoformat()
    upcoming_events = db.query(Event).filter(Event.event_date >= today_str).count()

    total_registrations = db.query(Registration).count()
    active_registrations = db.query(Registration).filter(Registration.status == "CONFIRMED").count()

    # Registrations by event
    events = db.query(Event).all()
    registrations_by_event: List[RegistrationByEvent] = []
    for ev in events:
        reg_count = db.query(Registration).filter(
            Registration.event_id == ev.id,
            Registration.status == "CONFIRMED"
        ).count()
        registrations_by_event.append(
            RegistrationByEvent(
                event_id=ev.id,
                title=ev.title,
                category=ev.category,
                capacity=ev.capacity,
                registrations=reg_count
            )
        )

    # Events by category
    categories_counts = db.query(
        Event.category, func.count(Event.id)
    ).group_by(Event.category).all()

    events_by_category = [
        EventsByCategory(category=cat, count=cnt)
        for cat, cnt in categories_counts
    ]

    return AdminDashboardStats(
        total_students=total_students,
        total_events=total_events,
        upcoming_events=upcoming_events,
        total_registrations=total_registrations,
        active_registrations=active_registrations,
        registrations_by_event=registrations_by_event,
        events_by_category=events_by_category
    )

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin only: Get list of registered users.
    """
    return db.query(User).order_by(User.created_at.desc()).all()

@router.get("/events/{event_id}/participants", response_model=EventParticipantsSummary)
def get_event_participants(
    event_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin only: Get attendee participant roster for a specific event.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    registrations = db.query(Registration).options(
        joinedload(Registration.user)
    ).filter(
        Registration.event_id == event_id
    ).order_by(Registration.registration_date.desc()).all()

    participants_list = []
    for reg in registrations:
        if reg.user:
            participants_list.append(
                ParticipantResponse(
                    registration_id=reg.id,
                    user_id=reg.user.id,
                    student_name=reg.user.name,
                    student_id=reg.user.student_id,
                    email=reg.user.email,
                    department=reg.user.department,
                    registration_date=reg.registration_date,
                    status=reg.status
                )
            )

    return EventParticipantsSummary(
        event_id=event.id,
        title=event.title,
        capacity=event.capacity,
        total_participants=len(participants_list),
        participants=participants_list
    )
