##
# @file model_department.py
# @brief Department model for users.
#
# Defines the `Department` SQLAlchemy model used by the user model and other
# code that needs department information.

from sqlalchemy import Column, Integer, String

from app.core.database import Base


class Department(Base):

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
