"""
Authentication routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.models.user import (
    UserLogin,
    UserLoginLDAP,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.core.dependencies import get_auth_service, get_current_user

router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    本地帳號登入。
    """
    user = await auth_service.authenticate_local(
        credentials.username, credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤",
        )

    token = auth_service.create_access_token(user)
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/login/ldap", response_model=TokenResponse)
async def login_ldap(
    credentials: UserLoginLDAP,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    LDAP/AD 企業帳號登入。
    """
    user = await auth_service.authenticate_ldap(
        credentials.username, credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LDAP 認證失敗",
        )

    token = auth_service.create_access_token(user)
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/logout")
async def logout():
    """
    登出 (客戶端需清除 token)。
    """
    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
):
    """
    取得當前登入使用者資訊。
    """
    return current_user
