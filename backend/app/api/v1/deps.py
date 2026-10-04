from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError
from app.core.config import settings
from app.models.user import TokenPayload, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.sqlite import get_db
from app.db.models import UserDB

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)

async def get_current_user(token: str = Depends(reusable_oauth2), db: AsyncSession = Depends(get_db)) -> UserResponse:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    # If admin, construct a generic admin user object to avoid db hit for config-based admin
    if token_data.role == "ADMIN" and token_data.sub == settings.ADMIN_EMAIL:
        return UserResponse(
            id="admin_id",
            email=settings.ADMIN_EMAIL,
            name="Administrator",
            role="ADMIN",
            is_active=True,
            created_at=None,
            last_login_at=None
        )

    # Fetch user from db
    result = await db.execute(select(UserDB).where(UserDB.id == token_data.sub))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at
    )
    
    if not user_resp.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
        
    return user_resp

async def require_admin(current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges"
        )
    return current_user
