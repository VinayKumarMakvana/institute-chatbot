from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from app.db.sqlite import get_db
from app.db.models import ChatbotSettingsDB
from app.models.chatbot_settings import ChatbotSettingsUpdate, ChatbotSettingsResponse
from app.api.v1.deps import get_current_user
from app.models.response import StandardResponse

router = APIRouter()

@router.get("/", response_model=StandardResponse)
async def get_chatbot_settings(
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_user) # Remove for testing UI temporarily
):
    result = await db.execute(select(ChatbotSettingsDB).limit(1))
    settings = result.scalars().first()
    
    if not settings:
        settings = ChatbotSettingsDB()
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
        
    return StandardResponse(success=True, data=settings)

@router.put("/", response_model=StandardResponse)
async def update_chatbot_settings(
    settings_in: ChatbotSettingsUpdate,
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_user)
):
    result = await db.execute(select(ChatbotSettingsDB).limit(1))
    settings = result.scalars().first()
    
    if not settings:
        settings = ChatbotSettingsDB(**settings_in.dict())
        db.add(settings)
    else:
        for key, value in settings_in.dict().items():
            setattr(settings, key, value)
            
    await db.commit()
    await db.refresh(settings)
    return StandardResponse(success=True, data=settings, message="Settings updated successfully")
