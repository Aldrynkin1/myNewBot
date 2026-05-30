import asyncio
from dotenv import load_dotenv

load_dotenv()

from aiogram import Bot, Dispatcher
from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.midllewares.db import DbSessionMiddleware
from app.handlers.router import router
from app.repositories.user_repo import UserRepository

async def on_startup_notify(bot: Bot):
    async with SessionLocal() as session:
        repo = UserRepository(session)
        users = await repo.get_all_users()
        
    for tg_id in users:
        try:
            await bot.send_message(chat_id=tg_id, text="Бот запущен.")
            await asyncio.sleep(0.05) 
        except Exception as e:
            print(f"Не удалось отправить пользователю {tg_id}: {e}")
    print("Рассылка завершена успешно!")

async def main(should_notify: bool):
    await init_db()
    
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    
    if should_notify:
        dp.startup.register(on_startup_notify)

    dp.update.middleware(DbSessionMiddleware())
    dp.include_router(router)

    print("Bot started via Polling (Locally)!")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    user_input = input("Введите 'да', чтобы начать рассылку, или нажмите Enter, чтобы пропустить: ").strip().lower()
    run_notification = (user_input == 'да')
    
    # Запускаем бота и передаем сохраненный флаг
    asyncio.run(main(should_notify=run_notification))
