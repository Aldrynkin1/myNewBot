from dotenv import load_dotenv
load_dotenv()

import asyncio
from aiogram import Bot, Dispatcher

from app.core.config import settings
from app.core.database import init_db
from app.midllewares.db import DbSessionMiddleware
from app.handlers.router import router


async def main():
    await init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    dp.update.middleware(DbSessionMiddleware())

    dp.include_router(router)

    print("Bot started!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())