from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class FieldOfStudy(Base):
    __tablename__ = "field_of_study"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    name = Column(String(240), nullable=False)
    abbrevation = Column(String(40), nullable=False)
    year = Column(Integer, nullable=False)

    subject_links = relationship(
        "SubjectForFieldOfStudy",
        back_populates="field_of_study",
        cascade="all, delete-orphan",
    )
    