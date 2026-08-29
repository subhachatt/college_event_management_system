from contextlib import asynccontextmanager
import os
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from models import user, event, registration  # Ensure models are imported for metadata
from routers import auth_router, users_router, events_router, registrations_router, admin_router
from services.seed_service import seed_database_if_empty

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Automatically create all SQLite tables on startup
    Base.metadata.create_all(bind=engine)
    print("[*] Database tables verified / created.")

    # 2. Seed demo data if database is brand new/empty
    db = SessionLocal()
    try:
        seed_database_if_empty(db)
    finally:
        db.close()

    yield

    print("[*] Application shutdown.")

app = FastAPI(
    title="College Event Management System API",
    description="RESTful API for discovering, registering, and managing college events.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Allow origins: comma-separated list in ALLOWED_ORIGINS env var (defaults to all for dev)
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(events_router)
app.include_router(registrations_router)
app.include_router(admin_router)

@app.get("/", tags=["System"])
def root():
    return {
        "status": "online",
        "system": "College Event Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    # pyrefly: ignore [missing-import]
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
