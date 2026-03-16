from pydantic import BaseModel
from typing import List

class CreateGroupRequest(BaseModel):
    name: str
    user_ids: List[int]

class CreateGroupResponse(BaseModel):
    conversation_id: int
    name: str
    members: List[int]
