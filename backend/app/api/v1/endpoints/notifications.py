from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.notification import NotificationResponse, UnreadCountResponse
from app.models.response import StandardResponse
from app.models.user import UserResponse
from app.api.v1 import deps
from app.db.sqlite import get_db
from app.db.models import NotificationDB

router = APIRouter()

def utc_now():
    return datetime.utcnow()

def _map_notification(doc: NotificationDB) -> NotificationResponse:
    return NotificationResponse(
        id=doc.id,
        user_id=doc.user_id,
        type=doc.type,
        title=doc.title,
        message=doc.message,
        update_id=doc.update_id,
        is_read=doc.is_read,
        created_at=doc.created_at,
        read_at=doc.read_at
    )

@router.get("", response_model=StandardResponse[List[NotificationResponse]])
async def list_notifications(current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(NotificationDB)
        .where(NotificationDB.user_id == current_user.id)
        .order_by(NotificationDB.created_at.desc())
        .limit(100)
    )
    docs = result.scalars().all()
    return StandardResponse(success=True, message="Notifications retrieved", data=[_map_notification(d) for d in docs])

@router.get("/unread-count", response_model=StandardResponse[UnreadCountResponse])
async def get_unread_count(current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(NotificationDB)
        .where(NotificationDB.user_id == current_user.id, NotificationDB.is_read == False)
    )
    count = len(result.scalars().all())
    return StandardResponse(success=True, message="Unread count retrieved", data=UnreadCountResponse(unread_count=count))

@router.post("/{notification_id}/read", response_model=StandardResponse[None])
async def mark_read(notification_id: str, current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NotificationDB).where(NotificationDB.id == notification_id))
    noti = result.scalar_one_or_none()
    if not noti:
        raise HTTPException(status_code=404, detail="Notification not found")
    if noti.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    noti.is_read = True
    noti.read_at = utc_now()
    await db.commit()
    
    return StandardResponse(success=True, message="Notification marked read", data=None)

@router.post("/read-all", response_model=StandardResponse[None])
async def mark_all_read(current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(NotificationDB)
        .where(NotificationDB.user_id == current_user.id, NotificationDB.is_read == False)
    )
    unreads = result.scalars().all()
    now = utc_now()
    for noti in unreads:
        noti.is_read = True
        noti.read_at = now
        
    await db.commit()
    return StandardResponse(success=True, message="All notifications marked read", data=None)
