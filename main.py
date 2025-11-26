from fastapi import FastAPI
from routers import stats, tasks

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами по матрице Эйзенхауэра",
    version="1.0.0",
    contact={"name": "Baskakov O.V."},
)

app.include_router(tasks.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")

@app.get("/")
async def welcome() -> dict:
    return {
        "message": "Hello, student!",
        "api_title": app.title,
        "api_description": app.description,
        "api_version": app.version,
        "api_author": app.contact["name"],
    }

@app.post("/tasks")
async def create_task(task: dict):
    return {"message": "Запись успешно создана", "task": task}