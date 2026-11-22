from app.api.availability import router as availability_router
from app.api.auth import router as auth_router
from app.api.contacts import router as contacts_router
from app.api.exotel_stream import router as exotel_router
from app.api.profile import router as profile_router
from app.api.simulated_calls import router as simulated_calls_router

__all__ = [
    "availability_router",
    "auth_router",
    "contacts_router",
    "exotel_router",
    "profile_router",
    "simulated_calls_router",
]
