from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.response import StandardResponse
from app.models.user import UserResponse
from app.api.v1 import deps
from app.db.sqlite import get_db
from app.db.models import UserDB

router = APIRouter()

class UserStatusToggle(BaseModel):
    is_active: bool

@router.get("", response_model=StandardResponse[List[UserResponse]])
async def list_users(current_user: UserResponse = Depends(deps.require_admin), db: AsyncSession = Depends(get_db)):
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
                roll_number=u.roll_number,
                department=u.department,
                course=u.course,
                semester=u.semester,
                mobile_number=u.mobile_number,
                is_active=u.is_active,
                created_at=u.created_at,
                last_login_at=u.last_login_at
            ) for u in users
        ]
    )

@router.put("/{user_id}/status", response_model=StandardResponse[UserResponse])
async def update_user_status(
    user_id: str,
    status_in: UserStatusToggle,
    current_admin: UserResponse = Depends(deps.require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(UserDB).where(UserDB.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = status_in.is_active
    await db.commit()
    await db.refresh(user)

    return StandardResponse(
        success=True,
        message=f"User {'activated' if user.is_active else 'deactivated'} successfully",
        data=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            roll_number=user.roll_number,
            department=user.department,
            course=user.course,
            semester=user.semester,
            mobile_number=user.mobile_number,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
    )

@router.delete("/{user_id}", response_model=StandardResponse[None])
async def delete_user(
    user_id: str,
    current_admin: UserResponse = Depends(deps.require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(UserDB).where(UserDB.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()

    return StandardResponse(success=True, message="User deleted successfully", data=None)
