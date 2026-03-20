import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Prefer the repository root .env so backend and frontend share one source of truth.
# override=True protects against stale shell variables (e.g. old DATABASE_URL).
project_root_env = Path(__file__).resolve().parents[3] / ".env"
if project_root_env.exists():
    load_dotenv(dotenv_path=project_root_env, override=True)
else:
    load_dotenv(override=True)
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


# Database session dependency for CRUD operations through API
def get_db():
    """Dependency for FastAPI routes to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
