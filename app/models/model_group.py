from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Group(Base):
    __tablename__ = "group"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # Map English ORM attributes to legacy DB column names from initial migration.
    specialization = Column("spec", String, nullable=False)
    code = Column("kod", String, nullable=False)
    year = Column("rok", Integer, nullable=True)
    studies_type = Column("studia", String, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)

    department = relationship("Department", backref="groups")
    students = relationship("Student", back_populates="group")