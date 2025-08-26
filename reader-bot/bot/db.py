import psycopg2
import os
import logging
from datetime import datetime

def get_conn():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT")
        )
        return conn
    except Exception as e:
        logging.error(f"Ошибка подключения к БД: {e}")
        raise

def add_book(user_id, title, author, genre, status):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO books (user_id, title, author, genre, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, title, author, genre, status, datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
        logging.info("Книга успешно добавлена")
    except Exception as e:
        logging.error(f"Ошибка при добавлении книги: {e}")

def get_books(user_id, page):
    with get_conn() as conn:
        with conn.cursor() as cur:
            offset = (page-1)*10
            cur.execute("""
                SELECT id, title, author, genre, status FROM books
                WHERE user_id=%s ORDER BY id LIMIT 10 OFFSET %s
            """, (user_id, offset))
            return [dict(zip(['id', 'title', 'author', 'genre', 'status'], r)) for r in cur.fetchall()]

def search_books(user_id, query):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, author, genre, status FROM books
                WHERE user_id=%s AND (title ILIKE %s OR author ILIKE %s)
                ORDER BY id
            """, (user_id, f"%{query}%", f"%{query}%"))
            return [dict(zip(['id', 'title', 'author', 'genre', 'status'], r)) for r in cur.fetchall()]

def edit_book(book_id, updates):
    fields = ', '.join([f"{k}=%s" for k in updates.keys()])
    vals = list(updates.values())
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE books SET {fields} WHERE id=%s", vals+[book_id])
            conn.commit()

def delete_book(book_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM books WHERE id=%s", (book_id,))
            conn.commit()

def get_stats(user_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM books
                WHERE user_id=%s AND status='прочитано'
                AND DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)
            """, (user_id,))
            return cur.fetchone()[0]