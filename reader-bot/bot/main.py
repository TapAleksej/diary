import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import db

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Это бот-дневник читателя. /help для инструкций."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "/add <название>, <автор>, <жанр>, <статус:прочитано|читаю|в планах>\n"
        "/list <страница>\n"
        "/search <автор/название>\n"
        "/edit <id>, поле=значение,...\n"
        "/delete <id>\n"
        "/stats\n"
    )
    await update.message.reply_text(msg)

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text[len("/add "):].split(',')
    if len(args) != 4:
        await update.message.reply_text("Формат: /add Название, Автор, Жанр, Статус")
        return
    title, author, genre, status = [arg.strip() for arg in args]
    user_id = update.message.from_user.id
    db.add_book(user_id, title, author, genre, status)
    await update.message.reply_text("Книга добавлена!")

async def list_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    page = 1
    args = update.message.text.split()
    if len(args) == 2 and args[1].isdigit():
        page = int(args[1])
    user_id = update.message.from_user.id
    books = db.get_books(user_id, page)
    msg = "\n".join([
        f"{book['id']}. {book['title']} - {book['author']} [{book['genre']}] ({book['status']})"
        for book in books
    ])
    await update.message.reply_text(msg if msg else "Нет книг на этой странице.")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text[len("/search "):].strip()
    user_id = update.message.from_user.id
    results = db.search_books(user_id, query)
    msg = "\n".join([
        f"{book['id']}. {book['title']} - {book['author']} [{book['genre']}] ({book['status']})"
        for book in results
    ])
    await update.message.reply_text(msg if msg else "Не найдено.")

async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text[len("/edit "):].split(',')
    if len(args) < 2:
        await update.message.reply_text("Формат: /edit id, поле=значение,...")
        return
    book_id = int(args[0].strip())
    updates = {}
    for item in args[1:]:
        if "=" in item:
            field, value = item.strip().split("=", 1)
            updates[field] = value
    db.edit_book(book_id, updates)
    await update.message.reply_text("Запись обновлена.")

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    book_id = int(update.message.text[len("/delete "):].strip())
    db.delete_book(book_id)
    await update.message.reply_text("Книга удалена.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    stat = db.get_stats(user_id)
    await update.message.reply_text(f"Прочитано книг за месяц: {stat}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_books))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("edit", edit))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(CommandHandler("stats", stats))

    app.run_polling()

if __name__ == "__main__":
    main()
