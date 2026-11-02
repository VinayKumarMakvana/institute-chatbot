from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.sqlite import get_db
from app.db.models import ChatbotSettingsDB
from app.models.chatbot_settings import ChatbotSettingsUpdate, ChatbotSettingsResponse
from app.api.v1.deps import require_admin
from app.models.response import StandardResponse
from app.models.user import UserResponse

router = APIRouter()

@router.get("", response_model=StandardResponse[ChatbotSettingsResponse])
@router.get("/", response_model=StandardResponse[ChatbotSettingsResponse])
async def get_chatbot_settings(
    db: AsyncSession = Depends(get_db),
    current_admin: UserResponse = Depends(require_admin)
):
    result = await db.execute(select(ChatbotSettingsDB).limit(1))
    settings = result.scalars().first()
    
    if not settings:
        settings = ChatbotSettingsDB()
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
        
    return StandardResponse(success=True, data=ChatbotSettingsResponse.model_validate(settings))

@router.put("", response_model=StandardResponse[ChatbotSettingsResponse])
@router.put("/", response_model=StandardResponse[ChatbotSettingsResponse])
async def update_chatbot_settings(
    settings_in: ChatbotSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: UserResponse = Depends(require_admin)
):
    result = await db.execute(select(ChatbotSettingsDB).limit(1))
    settings = result.scalars().first()
    
    if not settings:
        settings = ChatbotSettingsDB(**settings_in.model_dump())
        db.add(settings)
    else:
        for key, value in settings_in.model_dump().items():
            setattr(settings, key, value)
            
    await db.commit()
    await db.refresh(settings)
    return StandardResponse(
        success=True,
        data=ChatbotSettingsResponse.model_validate(settings),
        message="Settings updated successfully"
    )
