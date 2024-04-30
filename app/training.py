from typing import Annotated
import sqlite3
from fastapi import FastAPI, Body, HTTPException, status


def connect_to_db():
    con = sqlite3.connect("training.db")
    cur = con.cursor()
    return con, cur


try:
    con, cur = connect_to_db()

    cur.execute("""CREATE TABLE if not exists diplom (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER,
            completed INTEGER);
    """)
finally:
    con.close()


app = FastAPI()

@app.post('/add/')
async def add_direction(
        name: Annotated[str, Body()],
        description: Annotated[str, Body()],
        price: Annotated[int, Body()]
        ):
    try:
        con, cur = connect_to_db()

        cur.execute("""INSERT INTO diplom (name, description, price, completed)
                    values (?, ?, ?, ?)
                    """, (name, description, price, 0))
        con.commit()
    finally:
        con.close()

@app.get('/{id}/')
async def get_direction(id: int):
    try:
        con, cur = connect_to_db()

        cur.execute("SELECT * FROM diplom WHERE id = ?", (id,))
        diplom = cur.fetchone()
        if diplom is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This diplom doesn't exist"
            )
        return {
            'id': diplom[0],
            'name': diplom[1],
            'description': diplom[2],
            'price': diplom[3],
            'completed': diplom[4],
            }
    finally:
        con.close()

@app.put('/{id}/')
async def put_direction(
    id: int,
    name: Annotated[str, Body()],
    description: Annotated[str, Body()],
    price: Annotated[int, Body()]
    ):
    try:
        con, cur = connect_to_db()

        cur.execute("""UPDATE diplom
                    SET name = ?,
                    description = ?,
                    price = ?
                    WHERE id = ?""", (name, description, price , id))
        con.commit()
        cur.execute("SELECT * FROM diplom WHERE id = ?", (id,))
        diplom = cur.fetchone()
        if diplom is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This diplom doesn't exist"
            )
        return {
            'id': diplom[0],
            'name': diplom[1],
            'description': diplom[2],
            'price': diplom[3],
            'completed': diplom[4],
            }
    finally:
        con.close()

@app.delete('/{id}/')
async def delete_direction(
    id: int
    ):
    try:
        con, cur = connect_to_db()
        cur.execute("DELETE FROM diplom WHERE id = ?", (id,))
        con.commit()
    finally:
        con.close()


