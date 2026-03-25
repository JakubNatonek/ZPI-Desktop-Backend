##
# @file model_role.py
# @brief Role model for users.
#
# Defines the `Role` SQLAlchemy model used by the user model and other
# code that needs role information.

from sqlalchemy import Column, Integer, String

from app.core.database import Base


class Role(Base):

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
