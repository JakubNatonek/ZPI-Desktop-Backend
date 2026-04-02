from sqlalchemy import Column, Integer, String

from app.core.database import Base


class RaplaConstraint(Base):
    __tablename__ = "rapla_constraint"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Constraint data
    name = Column(String(255), nullable=False)
    value = Column(String, nullable=True)