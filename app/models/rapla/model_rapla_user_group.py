from sqlalchemy import Column, Integer
from app.core.database import Base


class RaplaUserGroup(Base):
    __tablename__ = "rapla_user_group"

# Internal data
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

# Rapla data
    rapla_user_id = Column(Integer, nullable=False)
    category_id = Column(Integer, nullable=False)

    __mapper_args__ = {"primary_key": [user_id, category_id]}


#   <rapla:group key="category[key='modify-preferences']"/>
#   <rapla:group key="category[key='read-events-from-others']"/>
#   <rapla:group key="category[key='create-events']"/>
#   <rapla:group key="category[key='pl_phys']"/>
#   <rapla:group key="category[key='pl_math']"/>