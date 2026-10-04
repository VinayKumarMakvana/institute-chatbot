from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, documents, chat, saved_answers, live_updates, notifications, users, chatbot_settings, dashboard

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(saved_answers.router, prefix="/saved-answers", tags=["saved-answers"])
api_router.include_router(live_updates.router, prefix="/live-updates", tags=["live-updates"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(chatbot_settings.router, prefix="/chatbot/settings", tags=["chatbot-settings"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
