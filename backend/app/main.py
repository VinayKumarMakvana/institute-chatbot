import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
origins = list(set([
    settings.FRONTEND_URL,
    settings.BACKEND_URL,
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "*"
]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if settings.APP_ENV == "production" and settings.FRONTEND_URL != "*" else ["*"],
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    csp_connect = f"'self' {settings.FRONTEND_URL} {settings.BACKEND_URL} http://localhost:8000 http://127.0.0.1:8000 http://localhost:5500 http://127.0.0.1:5500 https: http: ws: wss:"
    response.headers["Content-Security-Policy"] = (
        f"default-src 'self' data: https:; "
        f"img-src 'self' data: https:; "
        f"connect-src {csp_connect}; "
        f"script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
        f"style-src 'self' 'unsafe-inline' https:; "
        f"font-src 'self' data: https:;"
    )
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

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

# Mount Static Frontend (Serves UI directly if frontend folder is present)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    logger.info(f"Mounted static frontend from {frontend_dir}")

if __name__ == "__main__":
    import uvicorn
    # run with: uvicorn app.main:app
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
