"""
FastAPI dependencies for dependency injection.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_access_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Get current authenticated user from JWT token.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效或過期的 Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": payload.get("sub"),
        "username": payload.get("username"),
        "role": payload.get("role"),
        "auth_type": payload.get("auth_type"),
    }


async def get_current_admin_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Get current user and verify admin role.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理員權限",
        )
    return current_user


# Service dependencies (to be implemented with actual database connections)
async def get_auth_service():
    """Get AuthService instance."""
    from app.services.auth_service import AuthService
    return AuthService()


async def get_user_service():
    """Get UserService instance."""
    from app.services.user_service import UserService
    return UserService()


async def get_ocr_service():
    """Get OCRService instance."""
    from app.services.ocr_service import OCRService
    return OCRService()


async def get_file_service():
    """Get FileService instance."""
    from app.services.file_service import FileService
    return FileService()


async def get_export_service():
    """Get ExportService instance."""
    from app.services.export_service import ExportService
    return ExportService()
