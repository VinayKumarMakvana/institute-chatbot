from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timezone
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.chat import ChatRequest, ChatResponse, ChatMetadataResponse, ChatDetailResponse, ChatMessageResponse
from app.models.response import StandardResponse
from app.models.user import UserResponse
from app.api.v1 import deps
from app.services.rag.rag_service import rag_service
from app.db.sqlite import get_db
from app.db.models import ChatDB, ChatMessageDB
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def utc_now():
    return datetime.utcnow()

@router.post("", response_model=StandardResponse[ChatResponse])
async def chat_endpoint(
    request: ChatRequest,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    chat_id = request.chat_id
    now = utc_now()
    
    chat = None
    if chat_id:
        result = await db.execute(select(ChatDB).where(ChatDB.id == chat_id, ChatDB.is_deleted == False))
        chat = result.scalar_one_or_none()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        if chat.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this chat")
    else:
        title = " ".join(request.message.strip().split()[:5])
        if len(request.message.strip().split()) > 5:
            title += "..."
            
        chat = ChatDB(
            user_id=current_user.id,
            title=title,
            created_at=now,
            updated_at=now,
            last_message_at=now,
            message_count=0,
            is_deleted=False
        )
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        chat_id = chat.id

    user_msg = ChatMessageDB(
        chat_id=chat_id,
        role="USER",
        content=request.message.strip(),
        sources=json.dumps([]),
        created_at=now
    )
    db.add(user_msg)
    await db.commit()
        
    try:
        rag_res = await rag_service.ask(request.message.strip(), db)
        
        ast_now = utc_now()
        ast_msg = ChatMessageDB(
            chat_id=chat_id,
            role="ASSISTANT",
            content=rag_res.answer,
            sources=json.dumps([s.model_dump() for s in rag_res.sources]),
            created_at=ast_now
        )
        db.add(ast_msg)
        
        chat.updated_at = ast_now
        chat.last_message_at = ast_now
        chat.message_count += 2
        
        await db.commit()
        await db.refresh(ast_msg)
        
        rag_res.chat_id = chat_id
        rag_res.message_id = ast_msg.id
        
        return StandardResponse(
            success=True,
            message="Answer generated successfully.",
            data=rag_res
        )
    except Exception as e:
        logger.error(f"Chat generation error: {e}")
        chat.updated_at = utc_now()
        chat.last_message_at = utc_now()
        chat.message_count += 1
        await db.commit()
        raise HTTPException(status_code=500, detail="The AI service is temporarily unavailable. Please try again.")

def _map_chat(doc: ChatDB) -> ChatMetadataResponse:
    return ChatMetadataResponse(
        id=doc.id,
        user_id=doc.user_id,
        title=doc.title,
        message_count=doc.message_count,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        last_message_at=doc.last_message_at
    )

def _map_msg(doc: ChatMessageDB) -> ChatMessageResponse:
    sources = []
    if doc.sources:
        try:
            sources = json.loads(doc.sources)
        except:
            pass
    return ChatMessageResponse(
        id=doc.id,
        chat_id=doc.chat_id,
        role=doc.role,
        content=doc.content,
        language=None,
        sources=sources,
        created_at=doc.created_at
    )

@router.get("s", response_model=StandardResponse[List[ChatMetadataResponse]])
async def list_chats(current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatDB).where(ChatDB.user_id == current_user.id, ChatDB.is_deleted == False).order_by(ChatDB.updated_at.desc()).limit(100)
    )
    docs = result.scalars().all()
    return StandardResponse(success=True, message="Chats retrieved.", data=[_map_chat(d) for d in docs])

@router.get("s/{chat_id}", response_model=StandardResponse[ChatDetailResponse])
async def get_chat(chat_id: str, current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatDB).where(ChatDB.id == chat_id, ChatDB.is_deleted == False))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    msg_result = await db.execute(select(ChatMessageDB).where(ChatMessageDB.chat_id == chat_id).order_by(ChatMessageDB.created_at.asc()).limit(1000))
    msgs = msg_result.scalars().all()
    
    return StandardResponse(
        success=True, 
        message="Chat details retrieved.", 
        data=ChatDetailResponse(
            chat=_map_chat(chat),
            messages=[_map_msg(m) for m in msgs]
        )
    )

@router.delete("s/{chat_id}", response_model=StandardResponse[None])
async def delete_chat(chat_id: str, current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatDB).where(ChatDB.id == chat_id, ChatDB.is_deleted == False))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    chat.is_deleted = True
    await db.commit()
    return StandardResponse(success=True, message="Chat deleted.", data=None)

# --- Saved Answers Endpoints ---

from app.db.models import SavedAnswerDB
from pydantic import BaseModel
from typing import Optional, Any

class SavedAnswerResponse(BaseModel):
    id: str
    user_id: str
    message_id: str
    chat_id: str
    question: str
    answer: str
    sources: Optional[List[Any]] = None
    created_at: datetime

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
        sources=sources,
        created_at=doc.created_at
    )

class SaveAnswerRequest(BaseModel):
    message_id: str
    chat_id: str
    question: str
    answer: str
    sources: Optional[List[Any]] = None

@router.post("/saved-answers", response_model=StandardResponse[SavedAnswerResponse])
async def save_answer(
    request: SaveAnswerRequest,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(SavedAnswerDB).where(SavedAnswerDB.user_id == current_user.id, SavedAnswerDB.message_id == request.message_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return StandardResponse(success=True, message="Answer already saved.", data=_map_saved_answer(existing))

    doc = SavedAnswerDB(
        user_id=current_user.id,
        message_id=request.message_id,
        chat_id=request.chat_id,
        question=request.question,
        answer=request.answer,
        sources=json.dumps(request.sources) if request.sources else None
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return StandardResponse(success=True, message="Answer saved successfully.", data=_map_saved_answer(doc))

@router.get("/saved-answers", response_model=StandardResponse[List[SavedAnswerResponse]])
async def get_saved_answers(current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SavedAnswerDB).where(SavedAnswerDB.user_id == current_user.id).order_by(SavedAnswerDB.created_at.desc())
    )
    docs = result.scalars().all()
    return StandardResponse(success=True, message="Saved answers retrieved.", data=[_map_saved_answer(d) for d in docs])

@router.delete("/saved-answers/{answer_id}", response_model=StandardResponse[None])
async def delete_saved_answer(answer_id: str, current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SavedAnswerDB).where(SavedAnswerDB.id == answer_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Saved answer not found")
    if doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    await db.delete(doc)
    await db.commit()
    return StandardResponse(success=True, message="Saved answer deleted.", data=None)


# --- Saved Answers Endpoints ---

from app.db.models import SavedAnswerDB
from pydantic import BaseModel
from typing import Optional, Any

class SavedAnswerResponse(BaseModel):
    id: str
    user_id: str
    message_id: str
    chat_id: str
    question: str
    answer: str
    sources: Optional[List[Any]] = None
    created_at: datetime

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
        sources=sources,
        created_at=doc.created_at
    )

class SaveAnswerRequest(BaseModel):
    message_id: str
    chat_id: str
    question: str
    answer: str
    sources: Optional[List[Any]] = None

@router.post("/saved-answers", response_model=StandardResponse[SavedAnswerResponse])
async def save_answer(
    request: SaveAnswerRequest,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(SavedAnswerDB).where(SavedAnswerDB.user_id == current_user.id, SavedAnswerDB.message_id == request.message_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return StandardResponse(success=True, message="Answer already saved.", data=_map_saved_answer(existing))

    doc = SavedAnswerDB(
        user_id=current_user.id,
        message_id=request.message_id,
        chat_id=request.chat_id,
        question=request.question,
        answer=request.answer,
        sources=json.dumps(request.sources) if request.sources else None
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return StandardResponse(success=True, message="Answer saved successfully.", data=_map_saved_answer(doc))

@router.get("/saved-answers", response_model=StandardResponse[List[SavedAnswerResponse]])
async def get_saved_answers(current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SavedAnswerDB).where(SavedAnswerDB.user_id == current_user.id).order_by(SavedAnswerDB.created_at.desc())
    )
    docs = result.scalars().all()
    return StandardResponse(success=True, message="Saved answers retrieved.", data=[_map_saved_answer(d) for d in docs])

@router.delete("/saved-answers/{answer_id}", response_model=StandardResponse[None])
async def delete_saved_answer(answer_id: str, current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SavedAnswerDB).where(SavedAnswerDB.id == answer_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Saved answer not found")
    if doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    await db.delete(doc)
    await db.commit()
    return StandardResponse(success=True, message="Saved answer deleted.", data=None)