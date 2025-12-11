from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dependencies import get_current_user
from models import Task
from database import get_async_session
from models.user import User

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/", response_model=dict)
async def get_tasks_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    if current_user.role == "admin":
        result = await db.execute(select(Task))
    else:
        result = await db.execute(select(Task).where(Task.user_id == current_user.id))
    tasks = result.scalars().all()
    total_tasks = len(tasks)
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    by_status = {"completed": 0, "pending": 0}
    for task in tasks:
        if task.quadrant in by_quadrant:
            by_quadrant[task.quadrant] += 1
    if task.completed:
        by_status["completed"] += 1
    else:
        by_status["pending"] += 1
    return {
        "total_tasks": total_tasks,
        "by_quadrant": by_quadrant,
        "by_status": by_status,
    }


@router.get("/deadlines", response_model=list)
async def get_deadline_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "admin":
        result = await db.execute(select(Task).where(Task.completed == False))
    else:
        result = await db.execute(
            select(Task).where(Task.completed == False, Task.user_id == current_user.id)
        )
    tasks = result.scalars().all()

    today = datetime.now().date()
    stats = []

    for t in tasks:
        stats.append(
            {
                "title": t.title,
                "description": t.description,
                "created_at": t.created_at,
                "days_left": (
                    (t.deadline_at.date() - today).days if t.deadline_at else None
                ),  # None, потому что иначе ошибка из-за старых задач с пустым полем
            }
        )

    return stats
