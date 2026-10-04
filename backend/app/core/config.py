from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "development"
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5500"
    
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "chatbot_db"
    
    JWT_SECRET: str = "supersecretkey_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 1440 # minutes

    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD_HASH: str = "$2b$12$0DBi.NtEflRKEMqujyaVyekgsoDa57/49g2X/HRmKvmPoujclAaXK"

    AI_PROVIDER: str = "mock"
    AI_API_KEY: str = ""
    
    DOCUMENT_STORAGE_PATH: str = "uploads"
    MAX_PDF_SIZE_MB: int = 10
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    VECTOR_INDEX_PATH: str = "vectorstore"

    RAG_TOP_K: int = 5
    RAG_MAX_CONTEXT_CHUNKS: int = 10
    RAG_MAX_CONTEXT_CHARS: int = 15000
    RAG_MIN_RELEVANCE_SCORE: float = 0.5
    SEMANTIC_WEIGHT: float = 0.7
    KEYWORD_WEIGHT: float = 0.3
    RAG_DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
