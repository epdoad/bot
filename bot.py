import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

TOKEN = "8495326477:AAFiThkRtm2fHiUPpLOOcY6ZDuEHu1KIJGg"
ADMIN_ID = 7526136310

PHOTO_URL = "https://github.com/epdoad/troll/blob/2e19fc2cea41a00f994b6278a879cdf0bfb5bb36/troll.png?raw=true"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("starts.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_nick(message: Message) -> str:
    u = message.from_user
    if u.username:
        return f"@{u.username}"
    return u.first_name or "пользователь"

async def start(message: Message):
    user = message.from_user
    
    username = f"@{user.username}" if user.username else "без username"
    full_name = " ".join(x for x in [user.first_name, user.last_name] if x)
    user_id = user.id
    chat_id = message.chat.id

    # 🔎 ОТЛАДКА
    logger.info(
        f"/start | user_id={user_id} | username={username} | name={full_name} | chat_id={chat_id}"
    )
    await message.bot.send_message(
    ADMIN_ID,
    f"🆕 NEW /start\nid={u.id}\nusername=@{u.username}"
)

    await message.answer_photo(
        photo=PHOTO_URL,
        caption=f' @Trolocrack? {get_nick(message)}'
    )

async def main():
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.message.register(start, CommandStart())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

