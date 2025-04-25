import os
from dotenv import load_dotenv

from aiogram.types import User
from aiogram import Bot

load_dotenv()

async def log_to_group(bot: Bot, user: User, text: str) -> None:
    username = f"@{user.username}" if user.username else "[без username]"
    full_name = f"{user.full_name}"
    msg = f'Пользователь {username} "{full_name}" {text}'
    await bot.send_message(chat_id=os.getenv("LOG_CHAT_ID"), text=msg)
