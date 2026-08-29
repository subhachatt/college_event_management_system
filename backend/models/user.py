from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    student_id = Column(String(50), nullable=True)  # Nullable for admins
    department = Column(String(100), nullable=True)
    role = Column(String(20), default="STUDENT", nullable=False)  # "STUDENT" or "ADMIN"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    registrations = relationship("Registration", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', role='{self.role}')>"
