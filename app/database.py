# import os # for later use in using .env
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# TODO: Configure PostgreSQL connection
# Database URL format: postgresql://user:password@host:port/database
# Example: postgresql://postgres:password@localhost:5432/zpi_db
# For production, use environment variables from .env file

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"
# TODO: Replace placeholder values:
# - user: your PostgreSQL username
# - password: your PostgreSQL password
# - localhost: database host (use 'localhost' for local, or server IP/hostname)
# - 5432: PostgreSQL port (default is 5432)
# - dbname: your database name

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Database session dependency for CRUD operations through API
def get_db():
    """Dependency for FastAPI routes to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()