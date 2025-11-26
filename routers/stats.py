from fastapi import APIRouter, HTTPException, Query
from database import tasks_db

router = APIRouter(
    prefix="/tasks",
    tags=["stats"],
)


@router.get("/stats")
async def get_tasks_stats():
    total = len(tasks_db)
    by_quadrant = {q: 0 for q in ["Q1", "Q2", "Q3", "Q4"]}
    by_status = {"completed": 0, "pending": 0}
    for task in tasks_db:
        by_quadrant[task["quadrant"]] += 1
        if task["completed"]:
            by_status["completed"] += 1
        else:
            by_status["pending"] += 1
    return {
        "total_tasks": total,
        "by_quadrant": by_quadrant,
        "by_status": by_status,
    }


@router.get("/status/{status}")
async def get_tasks_by_status(status: str):
    if status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=404, detail="Статус должен быть: completed или pending"
        )
    filtered = [
        task for task in tasks_db if task["completed"] == (status == "completed")
    ]
    return {"status": status, "count": len(filtered), "tasks": filtered}


@router.get("/search")
async def search_tasks(q: str):
    if len(q) < 2:
        raise HTTPException(
            status_code=400, detail="Ключевое слово должно содержать минимум 2 символа"
        )
    result = [
        task
        for task in tasks_db
        if q.lower() in task["title"].lower()
        or (task["description"] and q.lower() in task["description"].lower())
    ]
    if not result:
        raise HTTPException(status_code=404, detail="Задачи не найдены")
    return {"query": q, "count": len(result), "tasks": result}


@router.get("/{task_id}")
async def get_task_by_id(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Задача не найдена")
