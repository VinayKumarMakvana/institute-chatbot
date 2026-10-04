from pydantic import BaseModel
from typing import Optional

class ChatbotSettingsBase(BaseModel):
    provider: str
    model_name: str
    temperature: str
    max_tokens: int
    
    default_language: str
    support_english: bool
    support_hindi: bool
    support_hinglish: bool
    
    filter_inappropriate: bool
    only_educational: bool
    blocked_keywords: str
    
    response_style: str
    tone: str
    include_source_links: bool
    show_related_info: bool
    use_tables: bool
    
    search_pdfs: bool
    keyword_matching: bool
    use_rag: bool
    max_chunks: int
    rerank_results: bool
    
    session_memory: bool
    max_history: int
    fallback_response: str

class ChatbotSettingsCreate(ChatbotSettingsBase):
    pass

class ChatbotSettingsUpdate(ChatbotSettingsBase):
    pass

class ChatbotSettingsResponse(ChatbotSettingsBase):
    id: str
    
    class Config:
        orm_mode = True
