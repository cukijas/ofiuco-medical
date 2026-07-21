"""Authentication service."""

from typing import Optional

from fastapi import HTTPException, status

from backend.app.application.dtos.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    RefreshRequest,
)
from backend.app.domain.models.user import User
from backend.app.domain.ports.user_repo import IUserRepo
from backend.app.infrastructure.auth.password import hash_password, verify_password
from backend.app.infrastructure.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_user_id_from_token,
)
from backend.app.domain.enums import RoleEnum


class AuthService:
    """Authentication service handling user registration, login, and token management."""

    def __init__(self, user_repo: IUserRepo) -> None:
        self.user_repo = user_repo

    async def register(self, request: RegisterRequest, current_user: User) -> UserResponse:
        """Register a new user (admin-only).

        Args:
            request: Registration request data.
            current_user: The admin user performing registration.

        Returns:
            Created user response.

        Raises:
            HTTPException: If email already exists or user is not admin.
        """
        if current_user.role != RoleEnum.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can register new users",
            )
        
        # Check for duplicate email
        existing_user = await self.user_repo.get_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        
        # Create new user
        user = User(
            email=request.email,
            password_hash=hash_password(request.password),
            full_name=request.full_name,
            role=request.role,
        )
        created_user = await self.user_repo.create(user)
        
        return UserResponse.model_validate(created_user)

    async def login(self, request: LoginRequest) -> TokenResponse:
        """Authenticate user and issue JWT tokens.

        Args:
            request: Login request with email and password.

        Returns:
            Token response with access and refresh tokens.

        Raises:
            HTTPException: If credentials are invalid.
        """
        user = await self.user_repo.get_by_email(request.email)
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account",
            )
        
        role_value = user.role.value if hasattr(user.role, "value") else user.role
        access_token = create_access_token(user.id, role_value)
        refresh_token = create_refresh_token(user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh(self, request: RefreshRequest) -> TokenResponse:
        """Refresh access token using refresh token.

        Args:
            request: Refresh request with refresh token.

        Returns:
            New token response with rotated refresh token.

        Raises:
            HTTPException: If refresh token is invalid or user not found.
        """
        payload = decode_token(request.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = get_user_id_from_token(request.refresh_token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Issue new token pair (rotation)
        role_value = user.role.value if hasattr(user.role, "value") else user.role
        access_token = create_access_token(user.id, role_value)
        refresh_token = create_refresh_token(user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def me(self, current_user: User) -> UserResponse:
        """Get current user profile.

        Args:
            current_user: The authenticated user.

        Returns:
            User response with current user data.
        """
        return UserResponse.model_validate(current_user)
