import os
import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

TOKEN = os.getenv("BOT_TOKEN")  
ADMIN_ID = 7526136310

PHOTO_URL = "https://raw.githubusercontent.com/epdoad/troll/2e19fc2cea41a00f994b6278a879cdf0bfb5bb36/troll.png"

DB_PATH = "users.db"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS starters (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            first_seen_at TEXT
        )
    """)
    con.commit()
    con.close()

def save_if_first_time(user_id: int, username: str, full_name: str) -> bool:
    """
    True  -> первый /start (добавили в базу)
    False -> пользователь уже был
    """
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO starters(user_id, username, full_name, first_seen_at) "
        "VALUES(?, ?, ?, datetime('now'))",
        (user_id, username, full_name)
    )
    con.commit()
    inserted = (cur.rowcount == 1)
    con.close()
    return inserted

def get_nick(message: Message) -> str:
    u = message.from_user
    if u.username:
        return f"@{u.username}"
    full = " ".join(x for x in [u.first_name, u.last_name] if x)
    return full or "пользователь"

async def start(message: Message):
    user = message.from_user
    username = f"@{user.username}" if user.username else "без username"
    full_name = " ".join(x for x in [user.first_name, user.last_name] if x).strip()
    user_id = user.id
    chat_id = message.chat.id

    logger.info(f"/start | user_id={user_id} | username={username} | name={full_name or '—'} | chat_id={chat_id}")

    first_time = save_if_first_time(user_id, username, full_name)

    if first_time:
        try:
            await message.bot.send_message(
                ADMIN_ID,
                "🆕 NEW /start\n"
                f"id: {user_id}\n"
                f"username: {username}\n"
                f"name: {full_name or '—'}\n"
                f"chat_id: {chat_id}"
            )
        except Exception:
            logger.exception("Не смог отправить лог админу (возможно, админ не писал боту в личку)")

    # Ответ пользователю
    try:
        await message.answer_photo(
            photo=PHOTO_URL,
            caption=f'@Trolocrack? {get_nick(message)}'
        )
    except Exception:
        logger.exception("Не смог отправить фото по ссылке")
        await message.answer(f'Че в хуй? @Trolocrack? {get_nick(message)}')

async def main():
    if not TOKEN:
        raise RuntimeError("Не найден BOT_TOKEN. Добавь переменную окружения BOT_TOKEN (Railway -> Variables).")

    init_db()
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.message.register(start, CommandStart())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
