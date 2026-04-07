##
# @file model_user_department.py
# @brief Association model mapping users to departments (many-to-many).

from sqlalchemy import Column, Integer, ForeignKey

from app.core.database import Base


class DepartmentsForUser(Base):
    
    __tablename__ = "departments_for_user"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)