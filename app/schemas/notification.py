from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    """Schema do tworzenia powiadomienia (wewnętrzny use)."""
    user_id: int = Field(description="ID użytkownika, któremu przeznaczono powiadomienie")
    message: str = Field(min_length=1, max_length=2000, description="Treść powiadomienia")


class NotificationMarkAsRead(BaseModel):
    """Schema do oznaczenia powiadomienia jako przeczytanego."""
    is_read: bool = Field(default=True)


class NotificationResponse(BaseModel):
    """Response schema dla powiadomienia."""
    id: int
    user_id: int
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Response dla listy powiadomień użytkownika."""
    items: list[NotificationResponse] = Field(description="Lista powiadomień")
    unread_count: int = Field(description="Liczba nieprzeczytanych powiadomień")

    class Config:
        from_attributes = True
