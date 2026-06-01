from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_database
from scripts.migration_runner import run_migrations

from app.apis.api_login import router as login_router
from app.apis.api_users import router as users_router
from app.apis.api_departments import router as departments_router
from app.apis.api_roles import router as roles_router
from app.apis.api_chat import router as chat_router
from app.apis.api_messages import router as messages_router
from app.apis.api_announcements import router as announcements_router
from app.apis.thesis.api_thesis import router as thesis_router
from app.apis.thesis.api_admin_thesis import router as admin_thesis_router
from app.apis.api_grades import router as grades_router
from app.services.socket_events import create_socket_events
from app.services.socket_broker import set_sio
from app.apis.api_rooms import router as rooms_router
from app.apis.api_room_types import router as room_types_router
from app.apis.api_activities import router as activities_router
from app.apis.api_subjects import router as subjects_router
from app.apis.api_field_of_study import router as field_of_study_router
from app.apis.api_special_equipment import router as special_equipment_router
from app.apis.api_teaching_loads import router as teaching_loads_router
from app.apis.api_subject_preferences import router as subject_preferences_router
from app.apis.rapla.api_rapla_file import router as rapla_file_router

from app.apis.api_dezyderata import router as dezyderata_router
from app.apis.api_unavailability_notes import router as unavailability_notes_router
from app.apis.api_notifications import router as notifications_router
from app.apis.api_audit_logs import router as audit_logs_router
from app.apis.api_teaching_loads import router as teaching_loads_router

# NOTE: Semi example data to use and maybe import to proper app.
from app.seed_data.seed_all import seed_all
from app.core.database import SessionLocal
from app.models.model_teaching_load_assignment import TeachingLoadAssignment

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_database()
    # run_migrations() 

    # seed_all() # NOTE: Works only for empty DB with correct tables
    yield


app = FastAPI(title="ZPI Desktop Backend", lifespan=lifespan)

# Initialize Socket.IO
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_timeout=60,
    ping_interval=25,
)

# Expose sio via broker for other modules to emit events
set_sio(sio)

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
app.include_router(departments_router)
app.include_router(roles_router)
app.include_router(chat_router)
app.include_router(announcements_router)
app.include_router(rooms_router)
app.include_router(room_types_router)
app.include_router(activities_router)
app.include_router(subjects_router)
app.include_router(field_of_study_router)
app.include_router(teaching_loads_router)
app.include_router(subject_preferences_router)
app.include_router(special_equipment_router)
# app.include_router(audit_router)

# NOTE: Not fully implemented
app.include_router(rapla_file_router)

app.include_router(messages_router)
app.include_router(dezyderata_router)
app.include_router(thesis_router)
app.include_router(admin_thesis_router)
app.include_router(grades_router)
app.include_router(unavailability_notes_router)
app.include_router(notifications_router)
app.include_router(audit_logs_router)
app.include_router(teaching_loads_router)



@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}


# FastAPI app for HTTP tests (pytest TestClient). Production ASGI adds Socket.IO below.
fastapi_app = app

# Export ASGI app with Socket.IO support.
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)
