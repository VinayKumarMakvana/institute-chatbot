from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.db.sqlite import get_db
from app.db.models import UserDB, DocumentDB, ChatDB, SavedAnswerDB, ChatMessageDB
from app.api.v1.deps import get_current_user, require_admin

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_admin)  # Protect with admin auth
):
    # Total counts
    total_users = await db.scalar(select(func.count(UserDB.id)))
    total_queries = await db.scalar(select(func.count(ChatMessageDB.id)).where(ChatMessageDB.role == 'user'))
    total_pdfs = await db.scalar(select(func.count(DocumentDB.id)))
    saved_answers = await db.scalar(select(func.count(SavedAnswerDB.id)))

    # Recent Users
    recent_users_result = await db.execute(
        select(UserDB).order_by(desc(UserDB.created_at)).limit(5)
    )
    recent_users = recent_users_result.scalars().all()
    recent_users_list = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at.isoformat() if u.created_at else None
        } for u in recent_users
    ]

    # Recent Queries
    recent_queries_result = await db.execute(
        select(ChatMessageDB).where(ChatMessageDB.role == 'user').order_by(desc(ChatMessageDB.created_at)).limit(5)
    )
    recent_queries = recent_queries_result.scalars().all()
    recent_queries_list = [
        {
            "id": q.id,
            "content": q.content,
            "created_at": q.created_at.isoformat() if q.created_at else None
        } for q in recent_queries
    ]

    # Recent PDFs
    recent_pdfs_result = await db.execute(
        select(DocumentDB).order_by(desc(DocumentDB.created_at)).limit(5)
    )
    recent_pdfs = recent_pdfs_result.scalars().all()
    recent_pdfs_list = [
        {
            "id": d.id,
            "title": d.title,
            "original_filename": d.original_filename,
            "file_size": d.file_size,
            "created_at": d.created_at.isoformat() if d.created_at else None
        } for d in recent_pdfs
    ]

    return {
        "success": True,
        "data": {
            "stats": {
                "total_users": total_users,
                "total_queries": total_queries,
                "total_pdfs": total_pdfs,
                "saved_answers": saved_answers,
                "support_requests": 48, # Static for now
                "system_uptime": 99.9  # Static for now
            },
            "recent_activity": {
                "users": recent_users_list,
                "queries": recent_queries_list,
                "pdfs": recent_pdfs_list
            }
        }
    }
