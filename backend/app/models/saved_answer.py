from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.models.chat import SourceReference

class SavedAnswerRequest(BaseModel):
    message_id: str

class SavedAnswerResponse(BaseModel):
    id: str
    user_id: str
    chat_id: str
    message_id: str
    question: str
    answer: str
    language: str
    sources: List[SourceReference]
    created_at: datetime
