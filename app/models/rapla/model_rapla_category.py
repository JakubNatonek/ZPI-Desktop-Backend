from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer)
    category_key = Column(String(100), nullable=False)
    label = Column(String(255))
    definition = Column(Text)
    parent_order = Column(Integer)