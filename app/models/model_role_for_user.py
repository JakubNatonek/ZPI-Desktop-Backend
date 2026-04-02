##
# @file model_user_role.py
# @brief Association model mapping users to roles (many-to-many).

from sqlalchemy import Column, Integer, ForeignKey

from app.core.database import Base


class RolesForUser(Base):

    __tablename__ = "roles_for_user"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
