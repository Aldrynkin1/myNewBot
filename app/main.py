from dotenv import load_dotenv

from app.repositories.user_repo import UserRepository
load_dotenv()

import asyncio
from aiogram import Bot, Dispatcher

from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.midllewares.db import DbSessionMiddleware
from app.handlers.router import router
async def on_startup_notify(bot: Bot):
    
    async with SessionLocal() as session:
        repo = UserRepository(session)
        users = await repo.get_all_users()
        
    for tg_id in users:
        try:
            await bot.send_message(
                chat_id=tg_id, 
                text="Бот запущен."
            )
            await asyncio.sleep(0.05) 
        except Exception as e:
            print(f"Не удалось отправить пользователю {tg_id}: {e}")

    print("Рассылка завершена успешно!")



async def main():
    await init_db()
    
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    a = input("Введите 'да', чтобы начать рассылку или нажмите Enter, чтобы пропустить: ").strip().lower()
    if a == 'да':
        dp.startup.register(on_startup_notify)

    dp.update.middleware(DbSessionMiddleware())

    dp.include_router(router)

    print("Bot started!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())