"""
User-related Pydantic models (DTOs).
"""
from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    """Local login request."""

    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class UserLoginLDAP(BaseModel):
    """LDAP login request."""

    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    """Base user fields."""

    username: str
    display_name: str
    email: Optional[EmailStr] = None
    role: Literal["admin", "user"] = "user"


class UserCreate(UserBase):
    """Create user request."""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Update user request."""

    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Literal["admin", "user"]] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase):
    """User response."""

    id: str
    auth_type: Literal["local", "ldap"]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """User list response."""

    users: List[UserResponse]
    total: int
