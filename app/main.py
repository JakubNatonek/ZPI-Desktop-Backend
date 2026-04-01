from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_database

from app.apis.api_login import router as login_router
from app.apis.api_users import router as users_router
from app.apis.api_chat import router as chat_router
from app.services.socket_events import create_socket_events
from app.apis.api_rooms import router as rooms_router
from app.apis.rapla.api_rapla_file import router as rapla_file_router
from app.seed_data.seed_all import seed_all


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_database()
    # run_migrations() # this should not be done evry time the server is run

    # seed_all()
    yield


app = FastAPI(title="ZPI Desktop Backend", lifespan=lifespan)

# Initialize Socket.IO
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_timeout=60,
    ping_interval=25,
)

# Create socket event handlers
create_socket_events(sio)


# Create database tables 
# models.Base.metadata.create_all(bind=engine)

# Enable CORS for frontend development
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:8100,http://127.0.0.1:8100,http://localhost:4200,http://127.0.0.1:4200",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers

app.include_router(login_router)
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(rooms_router)
app.include_router(rapla_file_router)



@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}


# Export ASGI app with Socket.IO support.
app = socketio.ASGIApp(sio, other_asgi_app=app)
