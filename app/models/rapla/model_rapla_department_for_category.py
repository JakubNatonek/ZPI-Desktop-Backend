from sqlalchemy import Column, Integer, ForeignKey

from app.core.database import Base


class RaplaDepartmentForCategory(Base):
    __tablename__ = "rapla_department_for_category"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_category = Column(Integer, ForeignKey("rapla_category.id"), nullable=False)
    id_department = Column(Integer, ForeignKey("departments.id"), nullable=False)
