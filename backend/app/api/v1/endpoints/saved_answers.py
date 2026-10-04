from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json

from app.models.saved_answer import SavedAnswerRequest, SavedAnswerResponse
from app.models.response import StandardResponse
from app.models.user import UserResponse
from app.api.v1 import deps
from app.db.sqlite import get_db
from app.db.models import SavedAnswerDB, ChatMessageDB, ChatDB
from datetime import datetime, timezone

router = APIRouter()

def utc_now():
    return datetime.utcnow()

def _map_saved_answer(doc: SavedAnswerDB) -> SavedAnswerResponse:
    sources = []
    if doc.sources:
        try:
            sources = json.loads(doc.sources)
        except:
            pass
    return SavedAnswerResponse(
        id=doc.id,
        user_id=doc.user_id,
        message_id=doc.message_id,
        chat_id=doc.chat_id,
        question=doc.question,
        answer=doc.answer,
        language="en",
        sources=sources,
        created_at=doc.created_at
    )

@router.post("", response_model=StandardResponse[SavedAnswerResponse])
async def save_answer(
    request: SavedAnswerRequest,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ChatMessageDB).where(ChatMessageDB.id == request.message_id))
    msg = result.scalar_one_or_none()
    if not msg or msg.role != "ASSISTANT":
        raise HTTPException(status_code=404, detail="Assistant message not found")
        
    chat_result = await db.execute(select(ChatDB).where(ChatDB.id == msg.chat_id))
    chat = chat_result.scalar_one_or_none()
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    user_msg_result = await db.execute(select(ChatMessageDB).where(
        ChatMessageDB.chat_id == msg.chat_id, 
        ChatMessageDB.role == "USER", 
        ChatMessageDB.created_at < msg.created_at
    ).order_by(ChatMessageDB.created_at.desc()).limit(1))
    
    user_msg = user_msg_result.scalar_one_or_none()
    question = user_msg.content if user_msg else "Unknown question"
    
    saved = SavedAnswerDB(
        user_id=current_user.id,
        message_id=request.message_id,
        chat_id=msg.chat_id,
        question=question,
        answer=msg.content,
        sources=msg.sources,
        created_at=utc_now()
    )
    db.add(saved)
    await db.commit()
    await db.refresh(saved)
    
    return StandardResponse(
        success=True,
        message="Answer saved successfully.",
        data=_map_saved_answer(saved)
    )

@router.get("", response_model=StandardResponse[List[SavedAnswerResponse]])
async def list_saved_answers(
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(SavedAnswerDB)
        .where(SavedAnswerDB.user_id == current_user.id)
        .order_by(SavedAnswerDB.created_at.desc())
        .limit(100)
    )
    docs = result.scalars().all()
    return StandardResponse(
        success=True,
        message="Saved answers retrieved.",
        data=[_map_saved_answer(d) for d in docs]
    )

@router.delete("/{answer_id}", response_model=StandardResponse[None])
async def delete_saved_answer(
    answer_id: str,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(SavedAnswerDB).where(SavedAnswerDB.id == answer_id))
    answer = result.scalar_one_or_none()
    if not answer:
        raise HTTPException(status_code=404, detail="Saved answer not found")
        
    if answer.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    await db.delete(answer)
    await db.commit()
    
    return StandardResponse(
        success=True,
        message="Saved answer deleted.",
        data=None
    )
