from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from app.core.database import Base


class RaplaGroupForUser(Base):
    __tablename__ = "rapla_group_for_user"

# Internal data
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

# Rapla data
    rapla_user_id = Column(Integer, ForeignKey("rapla_user.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("rapla_category.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("rapla_user_id", "category_id", name="uq_rapla_group_for_user"),
    )