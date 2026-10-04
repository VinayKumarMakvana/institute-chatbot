import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.sqlite import init_db
from app.api.v1.api import api_router
from app.models.response import StandardResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI application...")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down FastAPI application...")

app = FastAPI(
    title="Language Agnostic Chatbot API",
    openapi_url=f"/api/v1/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=StandardResponse(
            success=False,
            message="An unexpected error occurred.",
            error_code="INTERNAL_SERVER_ERROR"
        ).model_dump()
    )

# Routers
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    # run with: uvicorn app.main:app --reload
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
