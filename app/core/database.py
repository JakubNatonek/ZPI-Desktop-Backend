import os
import time
import importlib
from urllib.parse import quote_plus

from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


load_dotenv()

def build_database_url() -> str:
    """Build database URL from environment variables with optional direct override."""
    direct_url = os.getenv("DATABASE_URL")
    if direct_url:
        return direct_url

    user = quote_plus(os.getenv("POSTGRES_USER", "postgres"))
    password = quote_plus(os.getenv("POSTGRES_PASSWORD", "postgres"))
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "zpi_db")

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


SQLALCHEMY_DATABASE_URL = build_database_url()
AUTO_CREATE_DATABASE = os.getenv("AUTO_CREATE_DATABASE", "true").lower() == "true"
DB_INIT_MAX_RETRIES = int(os.getenv("DB_INIT_MAX_RETRIES", "1"))
DB_INIT_RETRY_DELAY = float(os.getenv("DB_INIT_RETRY_DELAY", "2"))

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
)

Base = declarative_base()

#IF DB not exist creates db from dir ./models
def ensure_database_exists() -> None:
    """Create the PostgreSQL database if it does not exist yet."""
    if not AUTO_CREATE_DATABASE:
        return

    url = make_url(SQLALCHEMY_DATABASE_URL)

    if not url.drivername.startswith("postgresql"):
        return

    database_name = url.database
    if not database_name:
        return

    maintenance_db = os.getenv("POSTGRES_MAINTENANCE_DB", "postgres")

    connection = psycopg2.connect(
        dbname=maintenance_db,
        user=url.username,
        password=url.password,
        host=url.host or "localhost",
        port=url.port or 5432,
    )
    connection.autocommit = True

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
            exists = cursor.fetchone() is not None

            if not exists:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
    finally:
        connection.close()


def init_database() -> None:
    """Ensure the database exists and create all ORM tables."""
    last_error = None

    for attempt in range(1, DB_INIT_MAX_RETRIES + 1):
        try:
            ensure_database_exists()

            importlib.import_module("app.models")

            Base.metadata.create_all(bind=engine)
            return
        except psycopg2.OperationalError as exc:
            last_error = exc

            if attempt == DB_INIT_MAX_RETRIES:
                raise

            time.sleep(DB_INIT_RETRY_DELAY)
        except Exception:
            raise

    if last_error is not None:
        raise last_error


# Database session dependency for CRUD operations through API
def get_db():
    """Dependency for FastAPI routes to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
