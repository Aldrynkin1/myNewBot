from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository
from app.services.matchmaking_service import MatchMakingService
from app.services.chat_service import ChatService
from app.utils.icebreaker import get_random_icebreaker
from ..utils.count.count import count_game 

router = Router()



@router.message(Command("start"))
async def start_handler(message: Message, db: AsyncSession):
    if not message.from_user:
        return

    user_repo = UserRepository(db)

    await user_repo.get_or_create(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )

    await db.commit()

    await message.answer(
        """
Правила общения:

1. Уважайте друг друга. Не допускаются оскорбления, унижения, дискриминация по любому признаку.

2. Не публикуйте личную информацию. Не делитесь своими контактами, адресом, местом работы и т.д.

3. Не используйте бота для спама, рекламы или мошенничества.

4. Соблюдайте законы. Не обсуждайте и не планируйте незаконные действия.

5. Если ваш собеседник нарушает правила, используйте команду /report для жалобы.

6. Помните, что за нарушение правил можно получить жалобы от других пользователей, а при 5 и более жалобах — блокировку доступа к боту.

Приятного общения!

/search — найти собеседника
/next — новый собеседник
/stop — остановить диалог
/help — помощь
"""
    )


@router.message(Command("search"))
async def search_handler(message: Message, bot: Bot, db: AsyncSession):
    if not message.from_user:
        return

    matchmaking = MatchMakingService(db)

    res = await matchmaking.search(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )

    await db.commit()

    if not res:
        await message.answer("Ищем собеседника...")
        return

    user, partner = res

    await message.answer("Мы нашли тебе пару! Общайся :)")

    try:
        await bot.send_message(
            partner.tg_id,
            "🎉 Мы нашли тебе пару! Общайся :)"
        )
    except Exception as e:
        print("Ошибка при отправке сообщения партнеру:", e)

    await message.answer(
        "/next — новый собеседник\n"
        "/stop — остановить диалог"
    )


@router.message(Command("next"))
async def next_handler(message: Message, bot: Bot, db: AsyncSession):
    if not message.from_user:
        return

    chat_service = ChatService(db)

    partner_tg_id = await chat_service.get_partner_id(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )

    if partner_tg_id:
        try:
            await bot.send_message(
                partner_tg_id,
                "Собеседник переключился на нового пользователя."
            )
        except Exception as e:
            print("Ошибка при уведомлении собеседника:", e)

    await chat_service.stop_chat(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )

    matchmaking = MatchMakingService(db)

    res = await matchmaking.search(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )

    await db.commit()

    if not res:
        await message.answer("Ищу нового собеседника...")
        return

    user, partner = res

    await message.answer("Новая пара найдена! Общайся :)")

    try:
        await bot.send_message(
            partner.tg_id,
            "Новая пара найдена! Общайся :)"
        )
    except Exception as e:
        print("Ошибка при отправке сообщения партнеру:", e)

    await message.answer(
        "/next — новый собеседник\n"
        "/stop — остановить диалог"
    )


@router.message(Command("stop"))
async def stop_handler(message: Message, bot: Bot, db: AsyncSession):
    if not message.from_user:
        return

    chat_service = ChatService(db)

    partner_tg_id = await chat_service.get_partner_id(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )

    if not partner_tg_id:
        await message.answer(
            "Ты сейчас ни с кем не общаешься.\n"
            "Напиши /search, чтобы найти собеседника"
        )
        return

    await chat_service.stop_chat(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )

    await db.commit()

    await message.answer(
        "Диалог остановлен.\n"
        "Чтобы найти нового собеседника, введи /search"
    )

    try:
        await bot.send_message(
            partner_tg_id,
            "Собеседник завершил диалог.\n"
            "Чтобы найти нового, введи /search"
        )
    except Exception as e:
        print("Ошибка на стороне сервера:", e)


@router.message(Command("help"))
async def help_handler(message: Message):
    help_text = (
        "Вот что я могу сделать:\n\n"
        "/search — найти собеседника\n"
        "/next — найти нового собеседника\n"
        "/stop — остановить диалог\n"
        "/report — пожаловаться на собеседника\n"
        "/icebreaker — случайный вопрос для диалога\n"
        "/help — показать это сообщение"
    )

    await message.answer(help_text)


@router.message(Command("icebreaker"))
async def icebreaker_handler(message: Message, db: AsyncSession, bot: Bot):
    if not message.from_user:
        return

    chat_service = ChatService(db)

    partner_tg_id = await chat_service.get_partner_id(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )

    if not partner_tg_id:
        await message.answer(
            "Ты сейчас ни с кем не общаешься.\n"
            "Напиши /search"
        )
        return

    icebreaker = get_random_icebreaker()

    await message.answer(
        f"Вопрос для поддержания разговора:\n\n{icebreaker}"
    )

    try:
        await bot.send_message(
            partner_tg_id,
            f"🎲 Собеседник запустил игру!\n\n{icebreaker}"
        )
    except Exception as e:
        print("Ошибка при отправке вопроса:", e)


@router.message(Command("report"))
async def report_handler(message: Message, db: AsyncSession, bot: Bot):
    if not message.from_user:
        return

    chat_service = ChatService(db)

    partner_tg_id = await chat_service.get_partner_id(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )

    if not partner_tg_id:
        await message.answer(
            "Ты сейчас ни с кем не общаешься.\n"
            "Напиши /search"
        )
        return

    await chat_service.report_partner(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )

    await db.commit()

    await message.answer(
        "Собеседник был отмечен за нарушение правил."
    )

    try:
        await bot.send_message(
            partner_tg_id,
            "На тебя поступила жалоба.\n"
            "Пожалуйста, соблюдай правила общения."
        )
    except Exception as e:
        print("Ошибка при отправке предупреждения:", e)

@router.message(Command("count"))
async def count_handler(message: Message, db: AsyncSession, bot: Bot):
    if not message.from_user:
        return

    chat_service = ChatService(db)

    partner_tg_id = await chat_service.get_partner_id(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name,
    )

    if not partner_tg_id:
        await message.answer(
            "Ты сейчас ни с кем не общаешься.\n" "Напиши /search"
        )
        return

    if not message.text:
        return

    args = message.text.split()
    if len(args) < 3:
        await message.answer(
            "Неверный формат команды.\n"
            "Используй: `/count [твой_ответ] [ответ_партнёра]`\n"
            "Пример: `/count 45 50` (если неправильно вписан ответ собеседника с твоей стороны - карается репортом от партнёра, так что будь внимателен!)"
        )
        return

    try:
        user1_ans = int(args[1])
        user2_ans = int(args[2])
    except ValueError:
        await message.answer(
            "Ответы должны быть целыми числами.\n" "Пример: `/count 45 50`"
        )
        return

    result = count_game(
        user1_id=message.from_user.id,
        user1_ans=user1_ans,
        user2_id=partner_tg_id,
        user2_ans=user2_ans,
    )

    response_text = (
        f"Игра завершена!**\n\n"
        f"Пример: `{result['expression']}`\n"
        f"Правильный ответ: `{result['correct_answer']:.2f}`\n\n"
    )

    if result["winner_id"] == 0:
        response_text += "Ничья! У обоих одинаковое отклонение от истины."
    elif result["winner_id"] == message.from_user.id:
        response_text += "Вы победили!** Ваша точность оказалась выше."
    else:
        response_text += "Победил ваш партнёр!** Его ответ был ближе."

    await message.answer(response_text, parse_mode="Markdown")

    partner_text = (
        f"Ваш партнёр завершил игру!**\n\n"
        f"Выражение: `{result['expression']}`\n"
        f"Истинный ответ: `{result['correct_answer']:.2f}`\n\n"
    )

    if result["winner_id"] == 0:
        partner_text += "Ничья! У обоих одинаковое отклонение от истины."
    elif result["winner_id"] == partner_tg_id:
        partner_text += "Вы победили!** Ваш ответ оказался ближе."
    else:
        partner_text += "Победил ваш партнёр!** Его точность выше."

    try:
        await bot.send_message(
            chat_id=partner_tg_id, text=partner_text, parse_mode="Markdown"
        )
    except Exception:
        pass

@router.message()
async def forward_handler(message: Message, bot: Bot, db: AsyncSession):
    if not message.from_user:
        return

    if message.text and message.text.startswith("/"):
        return

    service = ChatService(db)

    partner_tg_id = await service.get_partner_id(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )

    if not partner_tg_id:
        await message.answer(
            "Ты сейчас ни с кем не общаешься.\n"
            "Напиши /search"
        )
        return

    action = "typing"

    if message.photo:
        action = "upload_photo"
    elif message.video:
        action = "upload_video"
    elif message.document:
        action = "upload_document"
    elif message.voice:
        action = "upload_voice"

    try:
        await bot.send_chat_action(
            chat_id=partner_tg_id,
            action=action
        )
    except Exception as e:
        print("Ошибка при отправке действия:", e)

    try:
        await message.send_copy(chat_id=partner_tg_id)
    except Exception as e:
        print("Ошибка при пересылке сообщения:", e)
        await message.answer(
            "Не удалось отправить сообщение собеседнику."
        )