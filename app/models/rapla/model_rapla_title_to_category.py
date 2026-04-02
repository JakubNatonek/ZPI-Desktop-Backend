from sqlalchemy import Column, Integer, ForeignKey

from app.core.database import Base


class RaplaTitleToCategory(Base):
    __tablename__ = "rapla_title_to_category"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_category = Column(Integer, ForeignKey("rapla_category.id"), nullable=False)
    id_title = Column(Integer, ForeignKey("title.id"), nullable=False)
