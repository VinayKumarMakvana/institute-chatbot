from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str = "USER" # USER or ADMIN
    roll_number: Optional[str] = None
    department: Optional[str] = None
    course: Optional[str] = None
    semester: Optional[str] = None
    mobile_number: Optional[str] = None

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    roll_number: str
    department: str
    course: str
    semester: str
    mobile_number: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: str
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str
    role: str
