from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import UserCreate, UserLogin, UserResponse, Token
from app.models.response import StandardResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.db.sqlite import get_db
from app.db.models import UserDB
from app.api.v1 import deps

router = APIRouter()

def utc_now():
    return datetime.utcnow()

@router.post("/register", response_model=StandardResponse[UserResponse])
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    email = user_in.email.lower()
    
    result = await db.execute(select(UserDB).where(UserDB.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered.")
        
    now = utc_now()
    new_user = UserDB(
        email=email,
        name=user_in.name,
        hashed_password=get_password_hash(user_in.password),
        role="USER",
        roll_number=user_in.roll_number,
        department=user_in.department,
        course=user_in.course,
        semester=user_in.semester,
        mobile_number=user_in.mobile_number,
        is_active=True,
        created_at=now,
        last_login_at=None
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    user_resp = UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        role=new_user.role,
        roll_number=new_user.roll_number,
        department=new_user.department,
        course=new_user.course,
        semester=new_user.semester,
        mobile_number=new_user.mobile_number,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )
    
    return StandardResponse(
        success=True,
        message="User registered successfully.",
        data=user_resp
    )

import time
from fastapi import Request

login_attempts = {}

def get_login_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Cleanup stale entries to prevent memory leak
    stale_ips = [ip for ip, times in login_attempts.items() if not any(t for t in times if now - t < 60)]
    for ip in stale_ips:
        del login_attempts[ip]
        
    attempts = [t for t in login_attempts.get(client_ip, []) if now - t < 60]
    limit = 60 if settings.APP_ENV == "development" else 10
    if len(attempts) >= limit:
        raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")
    attempts.append(now)
    login_attempts[client_ip] = attempts

@router.post("/login", response_model=StandardResponse[dict])
async def login(request: Request, user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    get_login_rate_limit(request)

    email = user_in.email.lower()
    
    if email == settings.ADMIN_EMAIL.lower() and verify_password(user_in.password, settings.ADMIN_PASSWORD_HASH):
        now = utc_now()
        access_token = create_access_token(data={"sub": settings.ADMIN_EMAIL, "role": "ADMIN"})
        admin_resp = UserResponse(
            id="admin_id",
            email=settings.ADMIN_EMAIL,
            name="Administrator",
            role="ADMIN",
            is_active=True,
            created_at=now,
            last_login_at=now
        )
        return StandardResponse(
            success=True,
            message="Login successful",
            data={"user": admin_resp.model_dump(), "token": access_token}
        )
    
    result = await db.execute(select(UserDB).where(UserDB.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user account")
        
    now = utc_now()
    user.last_login_at = now
    await db.commit()
    
    access_token = create_access_token(data={"sub": user.id, "role": user.role})
    
    user_resp = UserResponse(
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
        last_login_at=now
    )
    
    return StandardResponse(
        success=True,
        message="Login successful",
        data={"user": user_resp.model_dump(), "token": access_token}
    )

@router.post("/admin/login", response_model=StandardResponse[dict])
async def admin_login(request: Request, user_in: UserLogin):
    get_login_rate_limit(request)
    email = user_in.email.lower()
    
    if email != settings.ADMIN_EMAIL.lower() or not verify_password(user_in.password, settings.ADMIN_PASSWORD_HASH):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    access_token = create_access_token(data={"sub": settings.ADMIN_EMAIL, "role": "ADMIN"})
    
    admin_resp = {
        "id": "admin_id",
        "email": settings.ADMIN_EMAIL,
        "name": "Administrator",
        "role": "ADMIN",
        "is_active": True,
        "created_at": None,
        "last_login_at": utc_now()
    }
    
    return StandardResponse(
        success=True,
        message="Admin login successful",
        data={"user": admin_resp, "token": access_token}
    )

from pydantic import BaseModel
from typing import Optional

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    mobile_number: Optional[str] = None
    department: Optional[str] = None
    course: Optional[str] = None
    semester: Optional[str] = None
    roll_number: Optional[str] = None

@router.put("/profile", response_model=StandardResponse[UserResponse])
async def update_profile(
    profile_in: UpdateProfileRequest,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role == "ADMIN":
        return StandardResponse(success=True, message="Admin profile active.", data=current_user)

    result = await db.execute(select(UserDB).where(UserDB.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if profile_in.name is not None and profile_in.name.strip():
        user.name = profile_in.name.strip()
    if profile_in.mobile_number is not None:
        user.mobile_number = profile_in.mobile_number.strip()
    if profile_in.department is not None:
        user.department = profile_in.department.strip()
    if profile_in.course is not None:
        user.course = profile_in.course.strip()
    if profile_in.semester is not None:
        user.semester = profile_in.semester.strip()
    if profile_in.roll_number is not None:
        user.roll_number = profile_in.roll_number.strip()

    await db.commit()
    await db.refresh(user)

    updated_resp = UserResponse(
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
    return StandardResponse(success=True, message="Profile updated successfully.", data=updated_resp)

@router.post("/change-password", response_model=StandardResponse[None])
async def change_password(
    pwd_in: ChangePasswordRequest,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role == "ADMIN":
        raise HTTPException(status_code=400, detail="Admin password is managed via environment configuration.")

    if len(pwd_in.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters.")

    result = await db.execute(select(UserDB).where(UserDB.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(pwd_in.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")

    user.hashed_password = get_password_hash(pwd_in.new_password)
    await db.commit()

    return StandardResponse(success=True, message="Password updated successfully.", data=None)

@router.get("/me", response_model=StandardResponse[UserResponse])
async def read_users_me(current_user: UserResponse = Depends(deps.get_current_user)):
    return StandardResponse(
        success=True,
        message="Current user info retrieved.",
        data=current_user
    )
