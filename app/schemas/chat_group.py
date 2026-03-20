from pydantic import BaseModel, Field
from typing import List

class CreateGroupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    user_ids: List[int] = Field(default_factory=list)

class CreateGroupResponse(BaseModel):
    conversation_id: int
    name: str
    members: List[int]
