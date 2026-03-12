from fastapi import FastAPI
from .database import engine
from . import models
from fastapi.middleware.cors import CORSMiddleware
import subprocess

from app.apis.api_login import router as login_router
from app.migration_runner import run_migrations


app = FastAPI(title="ZPI Desktop Backend")

# Create database tables 
models.Base.metadata.create_all(bind=engine)

# Run Alembic migrations automatically at startup
run_migrations()

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(login_router)



@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}
