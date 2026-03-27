from sqlalchemy import Column, Integer, String

from app.core.database import Base


class RaplaLanguageAbbreviations(Base):
    __tablename__ = "rapla_language_abbreviations"

# Internal data
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

# Rapla data
    language = Column(String(10))