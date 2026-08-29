from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    registration_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(20), default="CONFIRMED", nullable=False)  # "CONFIRMED", "CANCELLED"

    # Unique constraint per user and event
    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event_registration"),
    )

    # Relationships
    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")

    def __repr__(self):
        return f"<Registration(id={self.id}, user_id={self.user_id}, event_id={self.event_id}, status='{self.status}')>"
