from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AuditLogResponse(BaseModel):
    id: int
    entity_name: str
    entity_id: int
    action: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    modified_by: Optional[int] = None
    modified_by_name: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class AcknowledgeRequest(BaseModel):
    pass
