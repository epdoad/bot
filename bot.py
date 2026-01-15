import os
import asyncio
import logging
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.deep_linking import create_start_link


TOKEN = os.getenv("BOT_TOKEN")  
ADMIN_ID = 7526136310          

PHOTO_URL = "https://raw.githubusercontent.com/epdoad/troll/2e19fc2cea41a00f994b6278a879cdf0bfb5bb36/troll.png"
PHOTO_URL_HI = "https://github.com/epdoad/troll/blob/main/pictures/jpg(9).png?raw=true"
DB_PATH = "users.db"
# ====================

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
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

def upsert_user(user_id: int, username: str, full_name: str) -> bool:
    """
    True  -> новый пользователь
    False -> уже был
    username/full_name обновляются всегда
    """
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT 1 FROM starters WHERE user_id = ?", (user_id,))
    existed = cur.fetchone() is not None

    cur.execute("""
        INSERT INTO starters(user_id, username, full_name, first_seen_at)
        VALUES(?, ?, ?, datetime('now'))
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            full_name=excluded.full_name
    """, (user_id, username, full_name))

    con.commit()
    con.close()
    return not existed

def get_sender_display(sender_id: int) -> str | None:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT username, full_name FROM starters WHERE user_id = ?", (sender_id,))
    row = cur.fetchone()
    con.close()

    if not row:
        return None
    username, full_name = row
    if username:
        return username  # уже с @
    return full_name or None



def get_user_fields(message: Message):
    u = message.from_user
    username = f"@{u.username}" if u.username else ""
    full_name = " ".join(x for x in [u.first_name, u.last_name] if x).strip()
    return u.id, username, full_name

def get_nick(message: Message) -> str:
    u = message.from_user
    if u.username:
        return f"@{u.username}"
    full = " ".join(x for x in [u.first_name, u.last_name] if x).strip()
    return full or "пользователь"

def reply_kb() -> ReplyKeyboardMarkup:

    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="ПОСЛАТЬ НАХУЙ ДРУГА")]],
        resize_keyboard=True
    )

async def send_photo_with_caption(message: Message, caption: str, photo_url: str):
    try:
        await message.answer_photo(
            photo=photo_url,
            caption=caption,
            reply_markup=reply_kb()
        )
    except Exception:
        logger.exception("Не смог отправить фото по ссылке, отправляю текст")
        await message.answer(caption, reply_markup=reply_kb())




async def start(message: Message, bot: Bot):
    if not TOKEN:
        return

    user_id, username, full_name = get_user_fields(message)
    chat_id = message.chat.id
    is_new = upsert_user(user_id, username, full_name)

    logger.info(f"/start | user_id={user_id} | username={username or '—'} | name={full_name or '—'} | chat_id={chat_id}")


    if is_new:
        try:
            await bot.send_message(
                ADMIN_ID,
                "🆕 NEW /start\n"
                f"id: {user_id}\n"
                f"username: {username or '—'}\n"
                f"name: {full_name or '—'}\n"
                f"chat_id: {chat_id}"
            )
        except Exception:
            logger.exception("Не смог отправить лог админу")

    hi_text = None
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) == 2:
        payload = parts[1].strip()
        if payload.startswith("hi_"):
            try:
                sender_id = int(payload.replace("hi_", "", 1))
                sender_name = get_sender_display(sender_id) or f"id:{sender_id}"
                receiver_name = get_nick(message)
                hi_text = f"{receiver_name}, ТЕБЯ ПОСЛАЛ НАХУЙ {sender_name}"
                logger.info(f"hi_received | receiver_id={user_id} | sender_id={sender_id}")
            except ValueError:
                pass

    if hi_text:
        await send_photo_with_caption(message, hi_text)

    await send_photo_with_caption(message, f'ЧЕ В ХУЙ@Trolocrack? {get_nick(message)}')


async def send_hi_button(message: Message, bot: Bot):
    """Нажатие кнопки в поле ввода приходит как обычный текст."""
    sender_id, username, full_name = get_user_fields(message)
    logger.info(f"send_hi_click | user_id={sender_id} | username={username or '—'} | name={full_name or '—'}")

    link = await create_start_link(bot, payload=f"hi_{sender_id}", encode=True)

    await message.answer(
        "PRUNK LINK FOR YOU STUPID FRIEND\n"
        f"{link}\n\n"
        
    )


async def main():
    if not TOKEN:
        raise RuntimeError("Не найден BOT_TOKEN. Добавь переменную окружения BOT_TOKEN (Railway -> Variables).")

    init_db()
    bot = Bot(TOKEN)
    dp = Dispatcher()

    dp.message.register(start, CommandStart())
    dp.message.register(send_hi_button, F.text == "ПОСЛАТЬ НАХУЙ ДРУГАт")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


