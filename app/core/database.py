import os
import time
import importlib
from urllib.parse import quote_plus

from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, inspect, text
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
def ensure_database_exists() -> bool:
    """Create the PostgreSQL database if it does not exist yet.

    Returns True when the database was created by this call, False otherwise.
    """
    if not AUTO_CREATE_DATABASE:
        return False

    url = make_url(SQLALCHEMY_DATABASE_URL)

    if not url.drivername.startswith("postgresql"):
        return False

    database_name = url.database
    if not database_name:
        return False

    maintenance_db = os.getenv("POSTGRES_MAINTENANCE_DB", "postgres")

    connection = psycopg2.connect(
        dbname=maintenance_db,
        user=url.username,
        password=url.password,
        host=url.host or "localhost",
        port=url.port or 5432,
    )
    connection.autocommit = True

    created = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
            exists = cursor.fetchone() is not None

            if not exists:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
                created = True
    finally:
        connection.close()

    return created


def ensure_teaching_load_assignment_schema() -> None:
    """Keep the teaching-load table aligned with the current ORM model.

    This is a narrow compatibility fallback for environments where the Alembic
    revision has not been applied yet but the app is already running against the
    target database.
    """
    inspector = inspect(engine)

    if "teaching_load_assignments" not in inspector.get_table_names():
        return

    columns = {
        column["name"]
        for column in inspector.get_columns("teaching_load_assignments")
    }

    if "subject_for_field_of_study_id" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE teaching_load_assignments ADD COLUMN subject_for_field_of_study_id INTEGER NULL"
                )
            )

    if "room_id" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE teaching_load_assignments ADD COLUMN room_id INTEGER NULL")
            )

    if "group_id" in columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE teaching_load_assignments DROP COLUMN group_id")
            )

    inspector = inspect(engine)

    if not any(
        index["name"] == "ix_teaching_load_assignments_subject_for_field_of_study_id"
        for index in inspector.get_indexes("teaching_load_assignments")
    ):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE INDEX ix_teaching_load_assignments_subject_for_field_of_study_id ON teaching_load_assignments (subject_for_field_of_study_id)"
                )
            )

    if not any(
        index["name"] == "ix_teaching_load_assignments_room_id"
        for index in inspector.get_indexes("teaching_load_assignments")
    ):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE INDEX ix_teaching_load_assignments_room_id ON teaching_load_assignments (room_id)"
                )
            )

    if not any(
        foreign_key["constrained_columns"] == ["subject_for_field_of_study_id"]
        and foreign_key["referred_table"] == "subject_for_field_of_study"
        for foreign_key in inspector.get_foreign_keys("teaching_load_assignments")
    ):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE teaching_load_assignments ADD CONSTRAINT fk_teaching_load_assignments_subject_for_field_of_study_id_subject_for_field_of_study FOREIGN KEY (subject_for_field_of_study_id) REFERENCES subject_for_field_of_study (id) ON DELETE SET NULL"
                )
            )

    if not any(
        foreign_key["constrained_columns"] == ["room_id"]
        and foreign_key["referred_table"] == "room"
        for foreign_key in inspector.get_foreign_keys("teaching_load_assignments")
    ):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE teaching_load_assignments ADD CONSTRAINT fk_teaching_load_assignments_room_id_room FOREIGN KEY (room_id) REFERENCES room (id) ON DELETE SET NULL"
                )
            )


def init_database() -> None:
    """Ensure the database exists and create all ORM tables."""
    last_error = None
    for attempt in range(1, DB_INIT_MAX_RETRIES + 1):
        try:
            # ensure database exists; capture whether it was created now
            db_created = ensure_database_exists()

            # import models and create tables
            importlib.import_module("app.models")

            Base.metadata.create_all(bind=engine)
            ensure_teaching_load_assignment_schema()

            # # Run seeding only when the database was created by this process
            # if db_created:
            #     from app.seed_data.seed_all import seed_all

            #     seed_all()

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
