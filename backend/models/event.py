from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), index=True, nullable=False)  # Technical, Cultural, Sports, Workshop, Seminar, Hackathon, Competition, Other
    venue = Column(String(150), nullable=False)
    event_date = Column(String(20), index=True, nullable=False)  # YYYY-MM-DD format for straightforward queries and displays
    start_time = Column(String(10), nullable=False)  # HH:MM
    end_time = Column(String(10), nullable=False)    # HH:MM
    capacity = Column(Integer, nullable=False, default=50)
    image_url = Column(String(500), nullable=True)
    organizer = Column(String(150), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event(id={self.id}, title='{self.title}', category='{self.category}')>"
