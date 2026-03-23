


from sqlalchemy import Column, Integer, String
from app.core.database import Base


class RaplaUserGroup(Base):
    __tablename__ = "rapla_group"

# Internal data
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

# Rapla data
    group = Column(String(255))
    

#   <rapla:category 
#  created-at="2026-02-25T18:08:45.266Z" 
#  last-changed="2026-02-25T18:08:45.266Z" 
#  id="ccce30fd-9853-442b-85dc-3af998a48db2" 
#  key="user-groups">
#  <doc:name 
#     lang="en">
#     user-groups
#  </doc:name>
#  <rapla:category
#     created-at="2026-02-25T18:08:45.266Z" 
#     last-changed="2026-02-25T18:08:45.266Z" 
#     id="c81c6b0b-1330-4d3a-9dc9-f3686965db68" 
#     key="read-events-from-others">
#     <doc:name 
#        lang="en">
#           See events of other users
#     </doc:name>
#  </rapla:category>