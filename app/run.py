import os
from dotenv import load_dotenv
import asyncio
import logging

from aiogram import Bot, Dispatcher

from middlewares.logger import GroupLoggerMiddleware
from handlers import router
from database.models import async_main

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()


async def main():
    await async_main()
    dp.include_router(router)
    dp.message.middleware(GroupLoggerMiddleware())
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutdown")