from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.matchmaking_service import MatchMakingService
from app.services.chat_service import ChatService

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("/search, чтобы найти собеседника")
    await message.answer('/next - новый собеседник')
    await message.answer('/stop - остановить диалог')


@router.message(Command("search"))
async def search_handler(message: Message, bot: Bot, db: AsyncSession):
    if not message.from_user:
        return

    serv = MatchMakingService(db)
    res = await serv.search(message.from_user.id)

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
    await chat_service.stop_chat(message.from_user.id)

    matchmaking = MatchMakingService(db)
    res = await matchmaking.search(message.from_user.id)

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

    if not message.text:
        return

    if message.text.startswith("/"):
        return

    service = ChatService(db)
    partner_tg_id = await service.get_partner_id(message.from_user.id)

    if not partner_tg_id:
        await message.answer("Ты сейчас ни с кем не общаешься. Напиши /search")
        return

    await bot.send_message(partner_tg_id, message.text)
    await message.answer("/search, чтобы найти собеседника")
    await message.answer('/next - новый собеседник')
    await message.answer('/stop - остановить диалог')
    
    
@router.message(Command("stop"))
async def stop_handler(message: Message, bot: Bot, db: AsyncSession):
    if not message.from_user:
        return
    
    chat_service = ChatService(db)
    partner_tg_id = await chat_service.get_partner_id(message.from_user.id)

    if not partner_tg_id:
        await message.answer("Ты сейчас ни с кем не общаешься. Напиши /search, чтобы найти собеседника")
        return

    await chat_service.stop_chat(message.from_user.id)
    await message.answer("Диалог остановлен. Чтобы найти нового собеседника, введи /search")
    try:
        await bot.send_message(
            partner_tg_id, 
            "Собеседник завершил диалог. Чтобы найти нового, введи /search"
        )
    except Exception:
        pass

    await message.answer("/search - найти собеседника")
    await message.answer('/next - новый собеседник')
    await message.answer('/stop - остановить диалог')