from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from databases import Database
from pydantic import BaseModel
from typing import Optional
from fastapi.exceptions import RequestValidationError
import datetime


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

class ErrorResponseModel(BaseModel):
    status_code: int
    detail: str
    error_code: int


class UserNotFoundException(HTTPException):
    def __init__(self, status_code: int = 404, detail: str = 'UserNotFoundEpt'):
        super().__init__(status_code=status_code, detail=detail)


class InvalidUserDataException(HTTPException):
    def __init__(self, detail: str, status_code: int, message: str):
        super().__init__(status_code=status_code, detail=detail)
        self.message = message


@app.exception_handler(UserNotFoundException)
async def custom_exception_handler_a(request: Request, exc: ErrorResponseModel):
        start = datetime.datetime.now()
        return JSONResponse(status_code=exc.status_code,
            content=exc.detail,
            headers={"X-Error": str(datetime.datetime.now()-start)},
        )


@app.exception_handler(InvalidUserDataException)
async def custom_exception_handler_b(request: Request, exc: ErrorResponseModel) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code,content=exc.detail)


custom_messages = {
    "title": "Длина пароля должна быть от 8 до 16 символов",
    "description": "Описание должно быть строкой",
    "completed": "Должно быть булево число"
}


@app.exception_handler(RequestValidationError)
def custom_request_validation_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = error["loc"][-1]
        msg = custom_messages.get(field)
        errors.append({"field": field, "msg": msg, "value": error["input"]})
    print(errors)
    return JSONResponse(status_code=400, content=errors)

app.add_exception_handler(RequestValidationError, custom_request_validation_handler)


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
        raise UserNotFoundException(status_code=404, detail="fdsfdsfds not found")


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
