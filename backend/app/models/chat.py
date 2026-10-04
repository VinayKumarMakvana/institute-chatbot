from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None

class SourceReference(BaseModel):
    document_id: str
    document_title: str
    page_start: int
    page_end: int

class ChatResponse(BaseModel):
    answer: str
    language: str
    sources: List[SourceReference]
    chat_id: Optional[str] = None
    message_id: Optional[str] = None

class ChatMessageResponse(BaseModel):
    id: str
    chat_id: str
    role: str
    content: str
    language: Optional[str] = None
    sources: Optional[List[SourceReference]] = None
    created_at: datetime

class ChatMetadataResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    message_count: int

class ChatDetailResponse(BaseModel):
    chat: ChatMetadataResponse
    messages: List[ChatMessageResponse]

