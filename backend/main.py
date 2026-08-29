from contextlib import asynccontextmanager
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base, SessionLocal
from backend.models import user, event, registration  # Ensure models are imported for metadata
from backend.routers import auth_router, users_router, events_router, registrations_router, admin_router
from backend.services.seed_service import seed_database_if_empty

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

# Configure CORS for local frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for seamless local dev server communication
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
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
