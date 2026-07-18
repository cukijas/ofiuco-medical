"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    RefreshRequest,
)
from backend.app.application.services.auth_service import AuthService
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import get_current_user, require_role
from backend.app.domain.models.user import User
from backend.app.infrastructure.database.user_repo_impl import UserRepo

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Register a new user (admin-only).

    Args:
        request: Registration request data.
        current_user: Admin user performing registration.
        db: Database session.

    Returns:
        Created user data.
    """
    user_repo = UserRepo(db)
    auth_service = AuthService(user_repo)
    return await auth_service.register(request, current_user)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate user and receive JWT tokens.

    Args:
        request: Login request with email and password.
        db: Database session.

    Returns:
        JWT access and refresh tokens.
    """
    user_repo = UserRepo(db)
    auth_service = AuthService(user_repo)
    return await auth_service.login(request)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh access token using refresh token.

    Args:
        request: Refresh request with refresh token.
        db: Database session.

    Returns:
        New JWT token pair.
    """
    user_repo = UserRepo(db)
    auth_service = AuthService(user_repo)
    return await auth_service.refresh(request)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: User = Depends(get_current_user),
) -> None:
    """Logout current user (client-side token discard).

    Note: For true server-side logout, implement token blacklist.
    """
    # In a stateless JWT system, logout is typically handled client-side
    # by discarding the tokens. For enhanced security, implement token
    # blacklisting in a production system.
    return None


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current authenticated user profile.

    Args:
        current_user: Authenticated user from JWT.

    Returns:
        Current user data.
    """
    user_repo = UserRepo(None)  # Not needed for this operation
    auth_service = AuthService(user_repo)
    return await auth_service.me(current_user)
