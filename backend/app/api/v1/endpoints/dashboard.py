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

    from datetime import datetime, timedelta
    
    # Analytics - Graph Data (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_all_queries = await db.execute(
        select(ChatMessageDB).where(ChatMessageDB.role == 'user', ChatMessageDB.created_at >= seven_days_ago)
    )
    all_qs = recent_all_queries.scalars().all()
    
    date_counts = {}
    for i in range(7):
        d = (datetime.utcnow() - timedelta(days=6-i)).strftime('%Y-%m-%d')
        date_counts[d] = 0
        
    category_counts = {
        "Syllabus & Academics": 0,
        "Examination": 0,
        "Admission & Registration": 0,
        "Fee & Scholarship": 0,
        "Other": 0
    }
    
    for q in all_qs:
        d_str = q.created_at.strftime('%Y-%m-%d')
        if d_str in date_counts:
            date_counts[d_str] += 1
            
        c = q.content.lower()
        if 'syllabus' in c or 'subject' in c or 'course' in c:
            category_counts["Syllabus & Academics"] += 1
        elif 'exam' in c or 'result' in c or 'date' in c:
            category_counts["Examination"] += 1
        elif 'admission' in c or 'register' in c:
            category_counts["Admission & Registration"] += 1
        elif 'fee' in c or 'scholarship' in c or 'money' in c:
            category_counts["Fee & Scholarship"] += 1
        else:
            category_counts["Other"] += 1
            
    # Format graph data
    graph_data = [{"date": k, "count": v} for k, v in date_counts.items()]
    
    # Format categories
    total_cat = sum(category_counts.values()) or 1
    cat_data = [
        {
            "name": k, 
            "count": v, 
            "percentage": int((v/total_cat)*100)
        } for k, v in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    return {
        "success": True,
        "data": {
            "stats": {
                "total_users": total_users,
                "total_queries": total_queries,
                "total_pdfs": total_pdfs,
                "saved_answers": saved_answers,
                "support_requests": 0,
                "system_uptime": 99.9
            },
            "recent_activity": {
                "users": recent_users_list,
                "queries": recent_queries_list,
                "pdfs": recent_pdfs_list
            },
            "analytics": {
                "graph": graph_data,
                "categories": cat_data
            }
        }
    }
