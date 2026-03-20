from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import os

from .core.database import engine
from . import models
from app.core.database import SessionLocal
from app.models.model_user import User, RolaEnum, DzialEnum
from app.apis.api_login import router as login_router
from app.apis.api_users import router as users_router
from app.apis.api_chat import router as chat_router
from app.services.socket_events import create_socket_events
from scripts.migration_runner import run_migrations
from scripts.create_admin import create_admin


# Initialize FastAPI app
fastapi_app = FastAPI(title="ZPI Desktop Backend")

# Initialize Socket.IO
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_timeout=60,
    ping_interval=25,
)

# Create socket event handlers
create_socket_events(sio)


@fastapi_app.on_event("startup")
async def startup() -> None:
    run_migrations()
    create_admin()


# Create database tables 
# models.Base.metadata.create_all(bind=engine)

# Enable CORS for frontend development
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:4200",
)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
fastapi_app.include_router(login_router)
fastapi_app.include_router(users_router)
fastapi_app.include_router(chat_router)



@fastapi_app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}


# Export ASGI app with Socket.IO support.
app = socketio.ASGIApp(sio, fastapi_app)
