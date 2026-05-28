import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

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

async def on_startup_polling(bot: Bot):
    await init_db()
    asyncio.create_task(on_startup_notify(bot))
    print("Бот запущен через Polling (Локально)!")

async def on_startup_webhook(bot: Bot):
    await init_db()
    webhook_url = os.getenv("RENDER_EXTERNAL_URL")
    await bot.set_webhook(url=f"{webhook_url}/webhook")
    asyncio.create_task(on_startup_notify(bot))
    print(f"Бот запущен через Webhook на сервере: {webhook_url}/webhook")

def main():
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware())
    dp.include_router(router)

    # Проверяем: если мы на сервере Render (переменная создана хостингом автоматически)
    if os.getenv("RENDER_EXTERNAL_URL"):
        dp.startup.register(on_startup_webhook)
        
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
        setup_application(app, dp, bot=bot)
        
        port = int(os.getenv("PORT", 8080))
        print("Запуск веб-сервера для Render...")
        web.run_app(app, host="0.0.0.0", port=port)
    
    else:
        dp.startup.register(on_startup_polling)
        print("Запуск обычного Polling...")
        asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    main()
