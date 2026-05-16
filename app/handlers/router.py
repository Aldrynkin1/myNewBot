from aiogram import Router
from app.handlers.chat_handlers import router as chat_router

router = Router()
router.include_router(chat_router)