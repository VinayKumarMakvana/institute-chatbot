from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    EXTRACTING = "EXTRACTING"
    CLEANING = "CLEANING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    INDEXING = "INDEXING"
    READY = "READY"
    FAILED = "FAILED"

class DocumentBase(BaseModel):
    title: str
    document_type: str = "general"
    category: Optional[str] = None
    semester: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    document_type: Optional[str] = None
    category: Optional[str] = None
    semester: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: str
    original_filename: str
    stored_filename: str
    file_size: int
    mime_type: str
    version: int
    status: DocumentStatus
    processing_stage: str
    processing_error: Optional[str] = None
    total_pages: int
    total_chunks: int
    uploaded_by: str
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None

class DocumentChunk(BaseModel):
    id: str
    document_id: str
    document_version: int
    chunk_index: int
    text: str
    page_start: int
    page_end: int
    vector_id: Optional[int] = None
    created_at: datetime
