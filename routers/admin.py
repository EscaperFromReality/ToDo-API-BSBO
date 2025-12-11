from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_async_session
from models import User, UserRole
from models.task import Task
from schemas_auth import UserCreate, UserResponse, Token
from auth_utils import verify_password, get_password_hash, create_access_token
from dependencies import get_current_user
from pydantic import BaseModel, Field

router = APIRouter(prefix="/admin", tags=["users"])


@router.get("/admin/users", tags=["admin"])
async def get_all_users_with_tasks(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="Доступ запрещён. Нужны права администратора"
        )

    result = await db.execute(select(User))
    users = result.scalars().all()
    response = []

    for user in users:
        result_tasks = await db.execute(select(Task).where(Task.user_id == user.id))
        tasks_count = len(result_tasks.scalars().all())

        response.append(
            {
                "id": user.id,
                "nickname": user.nickname,
                "email": user.email,
                "role": user.role.value,
                "tasks_count": tasks_count,
            }
        )

    return response
