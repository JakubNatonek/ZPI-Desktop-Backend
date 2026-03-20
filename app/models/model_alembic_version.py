from sqlalchemy import Column, String

from app.core.database import Base


class AlembicVersion(Base):
    __tablename__ = "alembic_version"

    version_num = Column(String(32), primary_key=True, nullable=False)
