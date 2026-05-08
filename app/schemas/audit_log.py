from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class AuditLogDto(BaseModel):
    id: int
    entity_name: str
    entity_id: int
    action: str
    old_values: Optional[Any] = None
    new_values: Optional[Any] = None
    modified_by: Optional[int] = None
    modified_by_name: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class AuditLogResponseDto(BaseModel):
    last_changes_viewed_at: Optional[datetime] = None
    logs: list[AuditLogDto]
