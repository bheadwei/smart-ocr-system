"""
Admin routes for user management.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
)
from app.services.user_service import UserService
from app.core.dependencies import get_user_service, get_current_admin_user

router = APIRouter()


@router.get("/users", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 20,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_admin_user),
):
    """
    取得使用者列表 (管理員專用)。
    """
    users = await user_service.list_users(skip=skip, limit=limit)
    total = await user_service.count_users()
    return UserListResponse(users=users, total=total)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_admin_user),
):
    """
    新增本地使用者 (管理員專用)。
    """
    existing = await user_service.get_by_username(user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="使用者名稱已存在",
        )

    user = await user_service.create_user(user_data)
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_admin_user),
):
    """
    更新使用者資料 (管理員專用)。
    """
    user = await user_service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="使用者不存在",
        )
    return user


@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_admin_user),
):
    """
    停用使用者 (管理員專用)。
    """
    success = await user_service.deactivate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="使用者不存在",
        )
    return {"message": "使用者已停用"}
