import os
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.declarative import declarative_base
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker

# Use DATABASE_URL env var (set on Render as a PostgreSQL URL).
# Falls back to a local SQLite file for development.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_SQLITE_FALLBACK = f"sqlite:///{os.path.join(BASE_DIR, 'college_events.db')}"
DATABASE_URL = os.getenv("DATABASE_URL", _SQLITE_FALLBACK)

# Render's Postgres URLs start with "postgres://" but SQLAlchemy requires "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

_is_sqlite = DATABASE_URL.startswith("sqlite")
_connect_args = {"check_same_thread": False} if _is_sqlite else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
