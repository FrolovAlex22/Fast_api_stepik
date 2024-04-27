from typing import Annotated
import sqlite3
from fastapi import FastAPI, Body, HTTPException, status


def connect_to_db():
    con = sqlite3.connect("my_app.db")
    cur = con.cursor()
    return con, cur


try:
    con, cur = connect_to_db()

    cur.execute("""CREATE TABLE if not exists todo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed INTEGER);
    """)
finally:
    con.close()


app = FastAPI()


@app.post("/add/")
def add_task(
    title: Annotated[str, Body()],
    description: Annotated[str, Body()]
):
    try:
        con, cur = connect_to_db()
        cur.execute("""INSERT INTO todo (title, description, completed)
                    values (?, ?, ?)
                    """, (title, description, 0))
        con.commit()
    finally:
        con.close()


@app.get("/{id}/")
def get_task_by_id(id: int):
    try:
        con, cur = connect_to_db()
        cur.execute("SELECT * FROM todo WHERE id = ?", (id,))
        task = cur.fetchone()
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This task doesn't exist"
            )
        return {
            "id": task[0],
            "title": task[1],
            "description": task[2],
            "completed": task[3]
        }
    finally:
        con.close()


@app.put("/{id}/")
def update_task(
    id: int,
    title: Annotated[str, Body()],
    description: Annotated[str, Body()],
    completed: Annotated[int, Body()]
):
    try:
        con, cur = connect_to_db()
        cur.execute("""UPDATE todo
                    SET title = ?,
                    description = ?,
                    completed = ?
                    WHERE id = ?
                    """, (title, description, completed, id))
        con.commit()
        cur.execute("SELECT * FROM todo WHERE id = ?", (id,))
        task = cur.fetchone()
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This task doesn't exist"
            )
        return {
            "id": task[0],
            "title": task[1],
            "description": task[2],
            "completed": task[3]
        }
    finally:
        con.close()


@app.delete("/{id}/")
def delete_todo(id: int):
    try:
        con, cur = connect_to_db()
        cur.execute("DELETE from todo where id = ?", (id,))
        con.commit()
    finally:
        con.close()