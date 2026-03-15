from fastapi import FastAPI
from .database import engine
from . import models
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.model_user import User, RolaEnum, DzialEnum
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess

from app.apis.api_login import router as login_router
from app.migration_runner import run_migrations


app = FastAPI(title="ZPI Desktop Backend")

# Create database tables 
models.Base.metadata.create_all(bind=engine)

# Run Alembic migrations automatically at startup
run_migrations()

# Create admin user if not present
def ensure_admin():
    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@admin.com").first()
        if not admin:
            db.add(User(
                imie="admin",
                nazwisko="admin",
                login="admin",
                email="admin@admin.com",
                password_hash="$2b$12$zi7AdboGsbPpUp4j3qFpv.WTir3I5odeMnqzyUW4DTaN956Jq3.p.",
                plain_password=None,
                must_change_password=False,
                rola=RolaEnum.ADMIN,
                dzial=DzialEnum.ADMIN
            ))
            db.commit()
    finally:
        db.close()

ensure_admin()

# Enable CORS for frontend development
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:8100,http://127.0.0.1:8100,http://localhost:4200,http://127.0.0.1:4200",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(login_router)



@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}
