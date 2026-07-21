"""Authentication DTOs (Pydantic models)."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from backend.app.domain.enums import RoleEnum


class RegisterRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 chars)")
    full_name: Optional[str] = Field(None, description="User full name")
    role: RoleEnum = Field(RoleEnum.technician, description="User role")


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Response model for JWT tokens."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")


class UserResponse(BaseModel):
    """Response model for user data."""
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="User full name")
    role: RoleEnum = Field(..., description="User role")
    is_active: bool = Field(..., description="User active status")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="User last update timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


class RefreshRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str = Field(..., description="JWT refresh token")
