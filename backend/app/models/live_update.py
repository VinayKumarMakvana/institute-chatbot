from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class LiveUpdateStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    UNPUBLISHED = "UNPUBLISHED"

class LiveUpdatePriority(str, Enum):
    NORMAL = "NORMAL"
    IMPORTANT = "IMPORTANT"
    URGENT = "URGENT"

class LiveUpdateCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    category: Optional[str] = None
    target_audience: Optional[str] = None
    priority: LiveUpdatePriority = LiveUpdatePriority.NORMAL
    expiry_date: Optional[datetime] = None

class LiveUpdateUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    target_audience: Optional[str] = None
    priority: Optional[LiveUpdatePriority] = None
    expiry_date: Optional[datetime] = None

class LiveUpdateResponse(BaseModel):
    id: str
    title: str
    content: str
    category: Optional[str] = None
    target_audience: Optional[str] = None
    priority: LiveUpdatePriority
    status: LiveUpdateStatus
    created_by: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
