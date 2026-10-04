from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.response import StandardResponse
from app.models.user import UserResponse
from app.api.v1 import deps
from app.db.sqlite import get_db
from app.db.models import UserDB

router = APIRouter()

@router.get("", response_model=StandardResponse[List[UserResponse]])
async def list_users(current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserDB).order_by(UserDB.created_at.desc()))
    users = result.scalars().all()
    
    return StandardResponse(
        success=True,
        message="Users retrieved successfully",
        data=[
            UserResponse(
                id=u.id,
                email=u.email,
                name=u.name,
                role=u.role,
                is_active=u.is_active,
                created_at=u.created_at,
                last_login_at=u.last_login_at
            ) for u in users
        ]
    )
