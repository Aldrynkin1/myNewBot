from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository
from app.services.matchmaking_service import MatchMakingService
from app.services.chat_service import ChatService

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message, db: AsyncSession):
    if not message.from_user:
        return
    
    user_repo = UserRepository(db)
    user = await user_repo.get_or_create(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await db.commit()
    await message.answer("/search, чтобы найти собеседника")
    await message.answer('/next - новый собеседник')
    await message.answer('/stop - остановить диалог')


@router.message(Command("search"))
async def search_handler(message: Message, bot: Bot, db: AsyncSession):
    if not message.from_user:
        return

    serv = MatchMakingService(db)
    res = await serv.search(message.from_user.id, message.from_user.username, message.from_user.full_name)

    if not res:
        await message.answer("Ищем собеседника...")
        return

    user, partner = res

    await message.answer("Мы нашли тебе пару! Общайся :)")
    await bot.send_message(partner.tg_id, "Мы нашли тебе пару! Общайся :)")
    await message.answer("/search, чтобы найти собеседника")
    await message.answer('/next - новый собеседник')
    await message.answer('/stop - остановить диалог')


@router.message(Command("next"))
async def next_handler(message: Message, bot: Bot, db: AsyncSession):
    if not message.from_user:
        return

    chat_service = ChatService(db)
    await chat_service.stop_chat(message.from_user.id, message.from_user.username, message.from_user.full_name)

    matchmaking = MatchMakingService(db)
    res = await matchmaking.search(message.from_user.id, message.from_user.username, message.from_user.full_name)

    if not res:
        await message.answer("Ищу нового собеседника...")
        return

    user, partner = res

    await message.answer("Новая пара найдена! Общайся :)")
    await bot.send_message(partner.tg_id, "Новая пара найдена! Общайся :)")
    await message.answer("/search, чтобы найти собеседника")
    await message.answer('/next - новый собеседник')
    await message.answer('/stop - остановить диалог')


@router.message()
async def forward_handler(message: Message, bot: Bot, db: AsyncSession):
    if not message.from_user:
        return

    if message.text and message.text.startswith("/"):
        return

    service = ChatService(db)
    partner_tg_id = await service.get_partner_id(message.from_user.id, message.from_user.username, message.from_user.full_name)

    if not partner_tg_id:
        await message.answer("Ты сейчас ни с кем не общаешься. Напиши /search")
        return

    await message.send_copy(chat_id=partner_tg_id)
    
    
@router.message(Command("stop"))
async def stop_handler(message: Message, bot: Bot, db: AsyncSession):
    if not message.from_user:
        return
    
    chat_service = ChatService(db)
    partner_tg_id = await chat_service.get_partner_id(message.from_user.id, message.from_user.username, message.from_user.full_name)

    if not partner_tg_id:
        await message.answer("Ты сейчас ни с кем не общаешься. Напиши /search, чтобы найти собеседника")
        return

    await chat_service.stop_chat(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer("Диалог остановлен. Чтобы найти нового собеседника, введи /search")
    try:
        await bot.send_message(
            partner_tg_id, 
            "Собеседник завершил диалог. Чтобы найти нового, введи /search"
        )
    except Exception as e:
        print('Ошибка на стороне сервера - ', e)
        pass