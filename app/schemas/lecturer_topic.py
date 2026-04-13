from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.thesis_datetime import format_datetime_minute


class LecturerTopicCreateRequest(BaseModel):
    topic: str = Field(min_length=10, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class LecturerTopicResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda value: format_datetime_minute(value)})

    id: int
    lecturer_id: int
    lecturer_name: str
    topic: str
    description: str | None
    is_taken: bool
    created_at: datetime
