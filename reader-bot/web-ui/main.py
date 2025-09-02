from datetime import datetime
from enum import Enum
from typing import Optional, List
import os

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
import asyncpg
import os

DB_USER=os.getenv("POSTGRES_USER")
DB_PASS=os.getenv("POSTGRES_PASSWORD")
DB_HOST=os.getenv("POSTGRES_HOST")
DB_NAME=os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

app = FastAPI(title="Book Library API")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class StatusEnum(str, Enum):
    read = "прочитано"
    reading = "читаю"
    planned = "в планах"

class BookCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=200)
    genre: Optional[str] = Field(None, max_length=100)
    status: StatusEnum

class BookResponse(BookCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    conn = await get_db_connection()
    try:
        query = "SELECT * FROM books ORDER BY created_at DESC LIMIT 20"
        books = await conn.fetch(query)
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "books": books}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

@app.get("/add", response_class=HTMLResponse)
async def add_book_page(request: Request):
    return templates.TemplateResponse("add.html", {"request": request})

@app.post("/add", response_class=RedirectResponse)
async def add_book(
    user_id: int = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    genre: str = Form(None),
    status: StatusEnum = Form(...)
):
    conn = await get_db_connection()
    try:
        query = """
            INSERT INTO books (user_id, title, author, genre, status)
            VALUES ($1, $2, $3, $4, $5)
        """
        await conn.execute(
            query,
            user_id,
            title,
            author,
            genre,
            status.value
        )
        return RedirectResponse("/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

@app.post("/api/books/", response_model=BookResponse, status_code=201)
async def create_book(book: BookCreate):
    conn = await get_db_connection()
    try:
        query = """
            INSERT INTO books (user_id, title, author, genre, status)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, user_id, title, author, genre, status, created_at
        """
        result = await conn.fetchrow(
            query,
            book.user_id,
            book.title,
            book.author,
            book.genre,
            book.status.value
        )
        return dict(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

@app.get("/api/books/", response_model=List[BookResponse])
async def get_books(
    user_id: Optional[int] = None,
    status: Optional[StatusEnum] = None,
    limit: int = 10,
    offset: int = 0
):
    conn = await get_db_connection()
    try:
        base_query = "SELECT * FROM books WHERE 1=1"
        params = []
        param_count = 0

        if user_id:
            param_count += 1
            base_query += f" AND user_id = ${param_count}"
            params.append(user_id)

        if status:
            param_count += 1
            base_query += f" AND status = ${param_count}"
            params.append(status.value)

        base_query += f" ORDER BY created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([limit, offset])

        results = await conn.fetch(base_query, *params)
        return [dict(record) for record in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

@app.get("/api/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int):
    conn = await get_db_connection()
    try:
        query = "SELECT * FROM books WHERE id = $1"
        result = await conn.fetchrow(query, book_id)
        if not result:
            raise HTTPException(status_code=404, detail="Book not found")
        return dict(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

@app.put("/api/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, book: BookCreate):
    conn = await get_db_connection()
    try:
        query = """
            UPDATE books
            SET user_id = $1, title = $2, author = $3, genre = $4, status = $5
            WHERE id = $6
            RETURNING *
        """
        result = await conn.fetchrow(
            query,
            book.user_id,
            book.title,
            book.author,
            book.genre,
            book.status.value,
            book_id
        )
        if not result:
            raise HTTPException(status_code=404, detail="Book not found")
        return dict(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

@app.delete("/{book_id}", status_code=204)
async def delete_book(book_id: int):
    conn = await get_db_connection()
    try:
        query = "DELETE FROM books WHERE id = $1"
        result = await conn.execute(query, book_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Book not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()