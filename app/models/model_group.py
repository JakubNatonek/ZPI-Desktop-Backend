from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Group(Base):
    __tablename__ = "group"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # Map English ORM attributes to legacy DB column names from initial migration.
    specialization = Column("spec", String, nullable=False)
    code = Column("kod", String, nullable=False)
    year = Column("rok", Integer, nullable=False)
    studies_type = Column("studia", String, nullable=False)

    students = relationship("Student", back_populates="group") # <- NOTE: Why do this??