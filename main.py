# Главный файл приложения
from fastapi import FastAPI
from typing import List, Dict, Any
from datetime import datetime

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact={
        "name": "Baskakov O.V.",
    },
)

# Временное хранилище (позже будет заменено на PostgreSQL)
tasks_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Сдать проект по FastAPI",
        "description": "Завершить разработку API и написать документацию",
        "is_important": True,
        "is_urgent": True,
        "quadrant": "Q1",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": 2,
        "title": "Изучить SQLAlchemy",
        "description": "Прочитать документацию и попробовать примеры",
        "is_important": True,
        "is_urgent": False,
        "quadrant": "Q2",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": 3,
        "title": "Сходить на лекцию",
        "description": None,
        "is_important": False,
        "is_urgent": True,
        "quadrant": "Q3",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": 4,
        "title": "Посмотреть сериал",
        "description": "Новый сезон любимого сериала",
        "is_important": False,
        "is_urgent": False,
        "quadrant": "Q4",
        "completed": True,
        "created_at": datetime.now(),
    },
]


@app.get("/")
async def welcome() -> dict:
    return {
        "message": "Hello, student!",
        "api_title": app.title,
        "api_description": app.description,
        "api_version": app.version,
        "api_author": app.contact["name"],
    }


@app.get("/tasks")
async def get_all_tasks() -> dict:
    return {
        "count": len(tasks_db),
        "tasks": tasks_db,
    }


@app.get("/tasks/stats") #Статистика по задачам
async def get_tasks_stats() -> dict:
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


@app.get("/tasks/status/{status}") #Фильтрация задач по статусу выполнения
async def get_tasks_by_status(status: str) -> dict:
    if status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=404, detail="Статус должен быть: completed или pending")
    filtered = [
        task for task in tasks_db if task["completed"] == (status == "completed")
    ]
    return {"status": status, "count": len(filtered), "tasks": filtered}


@app.get("/tasks/search") #Поиск по ключевому слову в названии или описании
async def search_tasks(q: str) -> dict:
    if len(q) < 2:
        raise HTTPException(
            status_code=400, detail="Ключевое слово должно содержать минимум 2 символа")
    result = [
        task
        for task in tasks_db
        if q.lower() in task["title"].lower()
        or (task["description"] and q.lower() in task["description"].lower())]
    if not result:
        raise HTTPException(status_code=404, detail="Задачи не найдены")
    return {"query": q, "count": len(result), "tasks": result}


@app.get("/tasks/{task_id}") #Поиск по ID (В конец, т.к. динамическая)
async def get_task_by_id(task_id: int) -> dict:
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Задача не найдена")


@app.get("/tasks/quadrant/{quadrant}") #Отправлено в конец, т.к. тоже динамическое
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    from fastapi import HTTPException
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(
            status_code=400, detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4")
    filtered = [task for task in tasks_db if task["quadrant"] == quadrant]
    return {"quadrant": quadrant, "count": len(filtered), "tasks": filtered}
