from backend.routers.auth import router as auth_router
from backend.routers.users import router as users_router
from backend.routers.events import router as events_router
from backend.routers.registrations import router as registrations_router
from backend.routers.admin import router as admin_router

__all__ = [
    "auth_router",
    "users_router",
    "events_router",
    "registrations_router",
    "admin_router"
]
