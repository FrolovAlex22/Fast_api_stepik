from fastapi import FastAPI, HTTPException
from databases import Database
from pydantic import BaseModel
from typing import Optional


app = FastAPI()

DATABASE_URL = "postgresql://postgres:1q2w3e4r@localhost/mydatabase"

database = Database(DATABASE_URL)


class Todo(BaseModel):
    title: str
    description: str
    completed: bool = False


class TodoReturn(BaseModel):
    title: str
    description: str
    completed: bool
    id: Optional[int] = None


@app.on_event("startup")
async def startup_database():
    await database.connect()

@app.on_event("shutdown")
async def shutdown_database():
    await database.disconnect()


@app.post("/task/", response_model=TodoReturn)
async def create_user(task: Todo):
    query = "INSERT INTO todo (title, description, completed) VALUES (:title, :description, :completed) RETURNING id"
    values = {"title": task.title, "description": task.description, "completed": task.completed}
    try:
        task_id = await database.execute(query=query, values=values)
        return {**task.dict(), "id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create user")


@app.get("/task/{task_id}", response_model=TodoReturn)
async def get_user(task_id: int):
    query = "SELECT * FROM todo WHERE id = :task_id"
    values = {"task_id": task_id}
    try:
        result = await database.fetch_one(query=query, values=values)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch user from database")
    if result:
        return TodoReturn(title=result["title"], description=result["description"], completed=result["completed"], id=result["id"])
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.put("/task/{task_id}", response_model=TodoReturn)
async def update_user(task_id: int, task: Todo):
    query = "UPDATE todo SET title = :title, description = :description, completed = :completed WHERE id = :task_id"
    values = {"task_id": task_id, "title": task.title, "description": task.description, "completed": task.completed}
    try:
        await database.execute(query=query, values=values)
        return {**task.dict(), "id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update user in database")


@app.delete("/task/{task_id}", response_model=dict)
async def delete_user(task_id: int):
    query = "DELETE FROM todo WHERE id = :task_id RETURNING id"
    values = {"task_id": task_id}
    try:
        deleted_rows = await database.execute(query=query, values=values)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete task from database")
    if deleted_rows:
        return {"message": "Task deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Task not found")
