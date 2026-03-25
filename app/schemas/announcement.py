from datetime import datetime

from pydantic import BaseModel, Field


class AnnouncementCreateRequest(BaseModel):
    subject: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class AnnouncementResponse(BaseModel):
    id: int
    subject: str
    content: str
    seen: bool
    created_at: datetime
    author_id: int | None = None


class AnnouncementSeenResponse(BaseModel):
    announcement_id: int
    seen: bool
