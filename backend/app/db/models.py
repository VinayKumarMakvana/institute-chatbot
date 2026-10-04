from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey
import uuid
from datetime import datetime, timezone
from app.db.sqlite import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.utcnow()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="USER")
    roll_number = Column(String, nullable=True)
    department = Column(String, nullable=True)
    course = Column(String, nullable=True)
    semester = Column(String, nullable=True)
    mobile_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    last_login_at = Column(DateTime, nullable=True)

class DocumentDB(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String)
    original_filename = Column(String)
    stored_filename = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    mime_type = Column(String)
    document_type = Column(String)
    category = Column(String, nullable=True)
    semester = Column(String, nullable=True)
    status = Column(String, default="UPLOADED")
    processing_stage = Column(String, nullable=True)
    processing_error = Column(String, nullable=True)
    version = Column(Integer, default=1)
    total_pages = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    uploaded_by = Column(String)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    processed_at = Column(DateTime, nullable=True)

class DocumentChunkDB(Base):
    __tablename__ = "document_chunks"
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    document_title = Column(String)
    page_number = Column(Integer, nullable=True)
    chunk_index = Column(Integer)
    text = Column(Text)
    created_at = Column(DateTime, default=utc_now)

class ChatDB(Base):
    __tablename__ = "chats"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title = Column(String)
    message_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    last_message_at = Column(DateTime, default=utc_now)

class ChatMessageDB(Base):
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True, default=generate_uuid)
    chat_id = Column(String, ForeignKey("chats.id", ondelete="CASCADE"), index=True)
    role = Column(String)
    content = Column(Text)
    sources = Column(String, nullable=True) # JSON encoded string
    created_at = Column(DateTime, default=utc_now)

class SavedAnswerDB(Base):
    __tablename__ = "saved_answers"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    message_id = Column(String)
    chat_id = Column(String)
    question = Column(Text)
    answer = Column(Text)
    sources = Column(String, nullable=True) # JSON encoded string
    created_at = Column(DateTime, default=utc_now)

class LiveUpdateDB(Base):
    __tablename__ = "live_updates"
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String)
    content = Column(Text)
    category = Column(String, nullable=True)
    target_audience = Column(String, nullable=True)
    priority = Column(String, default="NORMAL")
    status = Column(String, default="DRAFT")
    created_by = Column(String)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    published_at = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)

class NotificationDB(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type = Column(String)
    title = Column(String)
    message = Column(Text)
    update_id = Column(String, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)
    read_at = Column(DateTime, nullable=True)

class ChatbotSettingsDB(Base):
    __tablename__ = "chatbot_settings"
    id = Column(String, primary_key=True, default=generate_uuid)
    
    # AI Model & Core Settings
    provider = Column(String, default="Google Gemini")
    model_name = Column(String, default="Gemini 1.5 Flash (Recommended)")
    temperature = Column(String, default="0.3") # stored as string to match UI precision
    max_tokens = Column(Integer, default=2048)
    
    # Language Support
    default_language = Column(String, default="English")
    support_english = Column(Boolean, default=True)
    support_hindi = Column(Boolean, default=True)
    support_hinglish = Column(Boolean, default=True)
    
    # Content & Safety Filters
    filter_inappropriate = Column(Boolean, default=True)
    only_educational = Column(Boolean, default=True)
    blocked_keywords = Column(String, default="hack, cheats, adult, violence, illegal")
    
    # Response Behavior
    response_style = Column(String, default="Detailed Explanation")
    tone = Column(String, default="Helpful & Professional")
    include_source_links = Column(Boolean, default=True)
    show_related_info = Column(Boolean, default=True)
    use_tables = Column(Boolean, default=True)
    
    # Knowledge & Retrieval Settings
    search_pdfs = Column(Boolean, default=True)
    keyword_matching = Column(Boolean, default=True)
    use_rag = Column(Boolean, default=True)
    max_chunks = Column(Integer, default=5)
    rerank_results = Column(Boolean, default=True)
    
    # Advanced Settings
    session_memory = Column(Boolean, default=True)
    max_history = Column(Integer, default=20)
    fallback_response = Column(String, default="I'm sorry, I couldn't find the exact information in the available study materials. Please try rephrasing your question or contact support.")

    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
