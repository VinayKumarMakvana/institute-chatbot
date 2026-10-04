from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    update_id: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

class UnreadCountResponse(BaseModel):
    count: int
