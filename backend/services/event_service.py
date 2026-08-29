from datetime import datetime, date
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from backend.models.event import Event
from backend.models.registration import Registration
from backend.schemas.event import EventCreate, EventUpdate, EventResponse, EventDetailResponse

def calculate_event_stats(event: Event, db: Session, user_id: Optional[int] = None) -> Tuple[int, int, bool, bool, bool, Optional[str]]:
    """
    Calculate registered count, available seats, full status, past status,
    and user's registration status.
    """
    registered_count = db.query(func.count(Registration.id)).filter(
        Registration.event_id == event.id,
        Registration.status == "CONFIRMED"
    ).scalar() or 0

    available_seats = max(0, event.capacity - registered_count)
    is_full = registered_count >= event.capacity

    # Check if event is in the past
    today_str = date.today().isoformat()
    is_past = event.event_date < today_str

    is_registered = False
    reg_status = None
    if user_id:
        user_reg = db.query(Registration).filter(
            Registration.event_id == event.id,
            Registration.user_id == user_id
        ).first()
        if user_reg:
            is_registered = (user_reg.status == "CONFIRMED")
            reg_status = user_reg.status

    return registered_count, available_seats, is_full, is_past, is_registered, reg_status

def format_event_response(event: Event, db: Session) -> EventResponse:
    registered_count, available_seats, is_full, is_past, _, _ = calculate_event_stats(event, db)
    return EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        category=event.category,
        venue=event.venue,
        event_date=event.event_date,
        start_time=event.start_time,
        end_time=event.end_time,
        capacity=event.capacity,
        image_url=event.image_url,
        organizer=event.organizer,
        created_at=event.created_at,
        updated_at=event.updated_at,
        registered_count=registered_count,
        available_seats=available_seats,
        is_full=is_full,
        is_past=is_past
    )

def format_event_detail_response(event: Event, db: Session, user_id: Optional[int] = None) -> EventDetailResponse:
    registered_count, available_seats, is_full, is_past, is_registered, reg_status = calculate_event_stats(event, db, user_id)
    return EventDetailResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        category=event.category,
        venue=event.venue,
        event_date=event.event_date,
        start_time=event.start_time,
        end_time=event.end_time,
        capacity=event.capacity,
        image_url=event.image_url,
        organizer=event.organizer,
        created_at=event.created_at,
        updated_at=event.updated_at,
        registered_count=registered_count,
        available_seats=available_seats,
        is_full=is_full,
        is_past=is_past,
        is_registered=is_registered,
        registration_status=reg_status
    )

def get_all_events(
    db: Session,
    search: Optional[str] = None,
    category: Optional[str] = None,
    date_filter: Optional[str] = None,  # "upcoming", "past", or YYYY-MM-DD
    sort_by: str = "date_asc"
) -> List[EventResponse]:
    query = db.query(Event)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Event.title.ilike(search_term),
                Event.description.ilike(search_term),
                Event.venue.ilike(search_term),
                Event.organizer.ilike(search_term)
            )
        )

    if category and category != "All":
        query = query.filter(Event.category == category)

    today_str = date.today().isoformat()
    if date_filter == "upcoming":
        query = query.filter(Event.event_date >= today_str)
    elif date_filter == "past":
        query = query.filter(Event.event_date < today_str)
    elif date_filter and date_filter != "all":
        query = query.filter(Event.event_date == date_filter)

    if sort_by == "date_desc":
        query = query.order_by(Event.event_date.desc(), Event.start_time.desc())
    else:  # default date_asc
        query = query.order_by(Event.event_date.asc(), Event.start_time.asc())

    events = query.all()
    return [format_event_response(ev, db) for ev in events]

def get_event_by_id(db: Session, event_id: int, user_id: Optional[int] = None) -> Optional[EventDetailResponse]:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None
    return format_event_detail_response(event, db, user_id)

def create_event(db: Session, event_in: EventCreate) -> EventResponse:
    event = Event(
        title=event_in.title.strip(),
        description=event_in.description.strip(),
        category=event_in.category,
        venue=event_in.venue.strip(),
        event_date=event_in.event_date,
        start_time=event_in.start_time,
        end_time=event_in.end_time,
        capacity=event_in.capacity,
        image_url=event_in.image_url,
        organizer=event_in.organizer.strip()
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return format_event_response(event, db)

def update_event(db: Session, event_id: int, event_in: EventUpdate) -> Optional[EventResponse]:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None

    update_data = event_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if isinstance(value, str):
                setattr(event, field, value.strip())
            else:
                setattr(event, field, value)

    event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    return format_event_response(event, db)

def delete_event(db: Session, event_id: int) -> bool:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return False
    db.delete(event)
    db.commit()
    return True
