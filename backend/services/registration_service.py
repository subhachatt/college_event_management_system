from datetime import datetime, date, timezone
from typing import List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from models.event import Event
from models.registration import Registration
from models.user import User
from schemas.registration import RegistrationDetailResponse
from services.event_service import format_event_response

def register_user_for_event(db: Session, user_id: int, event_id: int) -> Registration:
    # 1. Check user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 2. Check event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    # 3. Check if event is in the past
    today_str = date.today().isoformat()
    if event.event_date < today_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot register for past events"
        )

    # 4. Check if already registered
    existing_reg = db.query(Registration).filter(
        Registration.user_id == user_id,
        Registration.event_id == event_id
    ).first()

    if existing_reg and existing_reg.status == "CONFIRMED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already registered for this event"
        )

    # 5. Check capacity
    active_count = db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.status == "CONFIRMED"
    ).count()

    if active_count >= event.capacity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This event has reached maximum capacity"
        )

    # 6. Save or update registration
    if existing_reg:
        existing_reg.status = "CONFIRMED"
        existing_reg.registration_date = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing_reg)
        return existing_reg
    else:
        new_reg = Registration(
            user_id=user_id,
            event_id=event_id,
            status="CONFIRMED"
        )
        db.add(new_reg)
        db.commit()
        db.refresh(new_reg)
        return new_reg

def cancel_user_registration(db: Session, user_id: int, event_id: int) -> bool:
    reg = db.query(Registration).filter(
        Registration.user_id == user_id,
        Registration.event_id == event_id,
        Registration.status == "CONFIRMED"
    ).first()

    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active registration not found for this event"
        )

    reg.status = "CANCELLED"
    db.commit()
    return True

def get_user_registrations(db: Session, user_id: int) -> List[RegistrationDetailResponse]:
    registrations = db.query(Registration).options(
        joinedload(Registration.event),
        joinedload(Registration.user)
    ).filter(
        Registration.user_id == user_id
    ).order_by(Registration.registration_date.desc()).all()

    result = []
    for reg in registrations:
        if reg.event:
            event_resp = format_event_response(reg.event, db)
            result.append(
                RegistrationDetailResponse(
                    id=reg.id,
                    user_id=reg.user_id,
                    event_id=reg.event_id,
                    registration_date=reg.registration_date,
                    status=reg.status,
                    event=event_resp
                )
            )
    return result
