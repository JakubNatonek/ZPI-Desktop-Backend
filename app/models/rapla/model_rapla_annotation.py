from sqlalchemy import Column, Integer, String, Text

from app.core.database import Base


class RaplaAnnotation(Base):
    __tablename__ = "rapla_annotation"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=True)

