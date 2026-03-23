from sqlalchemy import Column, ForeignKey, Integer, String

from app.core.database import Base


class RaplaLanguageName(Base):
    __tablename__ = "rapla_language_name"

# Internal data
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

# Rapla data
    id_abbreviations = Column(Integer, ForeignKey("rapla_language_abbreviations.id"), nullable=False)
    name = Column(String(255))