from aiogram import Router

from app.handlers.chat_handlers import router as user_router
from app.handlers.admin_handlers import router as admin_router

router = Router()

router.include_router(admin_router)
router.include_router(user_router)