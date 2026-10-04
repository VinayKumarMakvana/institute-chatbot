from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.live_update import LiveUpdateCreate, LiveUpdateUpdate, LiveUpdateResponse, LiveUpdateStatus
from app.models.notification import NotificationResponse

from app.models.response import StandardResponse
from app.models.user import UserResponse
from app.api.v1 import deps
from app.db.sqlite import get_db
from app.db.models import LiveUpdateDB, UserDB, NotificationDB

router = APIRouter()

def utc_now():
    return datetime.utcnow()

def _map_update(doc: LiveUpdateDB) -> LiveUpdateResponse:
    return LiveUpdateResponse(
        id=doc.id,
        title=doc.title,
        content=doc.content,
        category=doc.category,
        target_audience=doc.target_audience,
        priority=doc.priority,
        status=doc.status,
        created_by=doc.created_by,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        published_at=doc.published_at,
        expiry_date=doc.expiry_date
    )

@router.post("", response_model=StandardResponse[LiveUpdateResponse])
async def create_live_update(
    update_in: LiveUpdateCreate,
    current_user: UserResponse = Depends(deps.require_admin),
    db: AsyncSession = Depends(get_db)
):
    now = utc_now()
    doc = LiveUpdateDB(
        title=update_in.title,
        content=update_in.content,
        category=update_in.category,
        target_audience=update_in.target_audience,
        priority=update_in.priority.value,
        status=LiveUpdateStatus.DRAFT.value,
        created_by=current_user.email,
        is_deleted=False,
        created_at=now,
        updated_at=now,
        published_at=None,
        expiry_date=update_in.expiry_date
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    
    return StandardResponse(success=True, message="Draft update created", data=_map_update(doc))

@router.put("/{update_id}", response_model=StandardResponse[LiveUpdateResponse])
async def edit_live_update(
    update_id: str,
    update_in: LiveUpdateUpdate,
    current_user: UserResponse = Depends(deps.require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(LiveUpdateDB).where(LiveUpdateDB.id == update_id, LiveUpdateDB.is_deleted == False))
    update = result.scalar_one_or_none()
    if not update:
        raise HTTPException(status_code=404, detail="Live update not found")
        
    update.updated_at = utc_now()
    if update_in.title: update.title = update_in.title
    if update_in.content: update.content = update_in.content
    if update_in.category: update.category = update_in.category
    if update_in.target_audience: update.target_audience = update_in.target_audience
    if update_in.priority: update.priority = update_in.priority.value
    if update_in.expiry_date: update.expiry_date = update_in.expiry_date
        
    await db.commit()
    await db.refresh(update)
    return StandardResponse(success=True, message="Update edited", data=_map_update(update))

async def _create_notifications(update_id: str, title: str):
    # This should be called in background task. Needs own session.
    from app.db.sqlite import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(UserDB).where(UserDB.is_active == True, UserDB.role == "USER"))
        users = result.scalars().all()
        now = utc_now()
        notifications = []
        for u in users:
            notifications.append(NotificationDB(
                user_id=u.id,
                type="SYSTEM_UPDATE",
                title="New Platform Update",
                message=title,
                update_id=update_id,
                is_read=False,
                created_at=now
            ))
        if notifications:
            db.add_all(notifications)
            await db.commit()

@router.post("/{update_id}/publish", response_model=StandardResponse[LiveUpdateResponse])
async def publish_live_update(
    update_id: str,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(deps.require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(LiveUpdateDB).where(LiveUpdateDB.id == update_id, LiveUpdateDB.is_deleted == False))
    update = result.scalar_one_or_none()
    if not update:
        raise HTTPException(status_code=404, detail="Live update not found")
        
    if update.status == LiveUpdateStatus.PUBLISHED.value:
        raise HTTPException(status_code=400, detail="Update is already published")
        
    update.status = LiveUpdateStatus.PUBLISHED.value
    update.published_at = utc_now()
    update.updated_at = utc_now()
    
    await db.commit()
    await db.refresh(update)
    
    background_tasks.add_task(_create_notifications, update_id, update.title)
    
    return StandardResponse(success=True, message="Update published and notifications dispatched", data=_map_update(update))

@router.post("/{update_id}/unpublish", response_model=StandardResponse[LiveUpdateResponse])
async def unpublish_live_update(
    update_id: str,
    current_user: UserResponse = Depends(deps.require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(LiveUpdateDB).where(LiveUpdateDB.id == update_id, LiveUpdateDB.is_deleted == False))
    update = result.scalar_one_or_none()
    if not update:
        raise HTTPException(status_code=404, detail="Live update not found")
        
    update.status = LiveUpdateStatus.UNPUBLISHED.value
    update.updated_at = utc_now()
    
    await db.commit()
    await db.refresh(update)
    return StandardResponse(success=True, message="Update unpublished", data=_map_update(update))

@router.delete("/{update_id}", response_model=StandardResponse[None])
async def delete_live_update(
    update_id: str,
    current_user: UserResponse = Depends(deps.require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(LiveUpdateDB).where(LiveUpdateDB.id == update_id))
    update = result.scalar_one_or_none()
    if not update:
        raise HTTPException(status_code=404, detail="Live update not found")
        
    update.is_deleted = True
    await db.commit()
    return StandardResponse(success=True, message="Update deleted", data=None)

@router.get("/admin", response_model=StandardResponse[List[LiveUpdateResponse]])
async def admin_list_updates(current_user: UserResponse = Depends(deps.require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LiveUpdateDB).where(LiveUpdateDB.is_deleted == False).order_by(LiveUpdateDB.created_at.desc()).limit(1000))
    docs = result.scalars().all()
    return StandardResponse(success=True, message="Admin updates retrieved", data=[_map_update(d) for d in docs])

@router.get("", response_model=StandardResponse[List[LiveUpdateResponse]])
async def list_published_updates(current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LiveUpdateDB)
        .where(LiveUpdateDB.is_deleted == False, LiveUpdateDB.status == LiveUpdateStatus.PUBLISHED.value)
        .order_by(LiveUpdateDB.published_at.desc())
        .limit(100)
    )
    docs = result.scalars().all()
    return StandardResponse(success=True, message="Published updates retrieved", data=[_map_update(d) for d in docs])

@router.get("/{update_id}", response_model=StandardResponse[LiveUpdateResponse])
async def get_published_update(update_id: str, current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LiveUpdateDB).where(LiveUpdateDB.id == update_id, LiveUpdateDB.is_deleted == False, LiveUpdateDB.status == LiveUpdateStatus.PUBLISHED.value))
    update = result.scalar_one_or_none()
    if not update:
        raise HTTPException(status_code=404, detail="Update not found or unavailable")
    return StandardResponse(success=True, message="Update retrieved", data=_map_update(update))
