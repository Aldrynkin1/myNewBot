from email.mime import message

from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository
from app.services.matchmaking_service import MatchMakingService
from app.services.chat_service import ChatService
from app.utils.icebreaker import get_random_icebreaker
from app.services.chat_service import ChatService

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message, db: AsyncSession):
    if not message.from_user:
        return
    
    user_repo = UserRepository(db)
    user = await user_repo.get_or_create(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await db.commit()
    await message.answer("""
                         Правила общения:
1. Уважайте друг друга. Не допускаются оскорбления, унижения, дискриминация по любому признаку.

2. Не публикуйте личную информацию. Не делитесь своими контактами, адресом, местом работы и т.д.

3. Не используйте бота для спама, рекламы или мошенничества.

4. Соблюдайте законы. Не обсуждайте и не планируйте незаконные действия.

5. Если ваш собеседник нарушает правила, используйте команду /report для жалобы.

6. Помните, что за нарушение правил можно получить жалобы от других пользователей, а при 5 и более жалобах - блокировку доступа к боту.

Приятного общения!

/search, чтобы найти собеседника

/next - новый собеседник

/stop - остановить диалог
                         """)


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
    partner_tg_id = await service.get_partner_id(
        message.from_user.id, message.from_user.username, message.from_user.full_name
    )

    if not partner_tg_id:
        await message.answer("Ты сейчас ни с кем не общаешься. Напиши /search")
        return

    action = "upload_document" if message.document else "typing"
    if message.photo or message.video:
        action = "upload_photo" if message.photo else "upload_video"

    try:
        await bot.send_chat_action(chat_id=partner_tg_id, action=action)
    except Exception as e:
        print('Ошибка на стороне сервера при отправке действия - ', e)
        pass 

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
    
@router.message(Command("help"))
async def help_handler(message: Message, db: AsyncSession):
    if not message.from_user:
        return
    
    help_text = (
        "Вот что я могу сделать:\n\n"
        "/search — найти собеседника\n"
        "/next — найти нового собеседника\n"
        "/stop — остановить диалог\n"
        "/report — пожаловаться на собеседника\n"
        "/icebreaker — случайный вопрос для диалога\n"
        "/help — показать это сообщение"
    )
    
    await message.answer(help_text, parse_mode="Markdown")

    
@router.message(Command("icebreaker"))
async def icebreaker_handler(message: Message, db: AsyncSession, bot: Bot):
    if not message.from_user:
        return
    
    chat_service = ChatService(db)
    partner_tg_id = await chat_service.get_partner_id(message.from_user.id, message.from_user.username, message.from_user.full_name)

    if not partner_tg_id:
        await message.answer("Ты сейчас ни с кем не общаешься. Напиши /search, чтобы найти собеседника")
        return
    
    icebreaker = get_random_icebreaker()
    await message.answer(f"Вот вопрос для поддержания разговора:\n\n{icebreaker}")
    try:
        await bot.send_message(partner_tg_id, f"🎲 Собеседник запустил игру! Вопрос для вас обоих:\n\n{icebreaker}")
    except Exception as e:
        print('Ошибка на стороне сервера при отправке вопроса - ', e)
        pass
    
@router.message(Command("report"))
async def report_handler(message: Message, db: AsyncSession, bot: Bot):
    if not message.from_user:
        return

    chat_service = ChatService(db)
    partner_tg_id = await chat_service.get_partner_id(message.from_user.id, message.from_user.username, message.from_user.full_name)

    if not partner_tg_id:
        await message.answer("Ты сейчас ни с кем не общаешься. Напиши /search, чтобы найти собеседника")
        return

    await chat_service.report_partner(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer("Собеседник был отмечен за нарушение правил.")
    
    if partner_tg_id:
        try:
            await bot.send_message(partner_tg_id, "⚠️ Твой собеседник пожаловался на тебя. Пожалуйста, соблюдай правила общения. Если ты получишь 5 жалоб, то будешь заблокирован.")
        except Exception as e:
            print('Ошибка на стороне сервера при отправке предупреждения - ', e)
            pass