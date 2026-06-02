import time
import asyncio
from aiogram import Router, Bot, types, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.repositories.user_repo import UserRepository
from app.services.matchmaking_service import MatchMakingService
from app.services.chat_service import ChatService
from app.utils.icebreaker import get_random_icebreaker
from ..utils.count.count import check_winner, generate_question
from app.fractals.create_fractal import get_beatiful_fractal


router = Router()
active_math_games = {} 
logger = logging.getLogger(__name__)

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

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
        "/count - сыграть с партнером в интеллектуальную игру\n"
        "/fractal - сделать свой собственный фрактал\n"
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
async def count_handler(message: types.Message, db: AsyncSession, bot: Bot):
    if not message.from_user:
        return

    user_id = message.from_user.id

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

    question = generate_question()

    correct_res = float(question["Правильный ответ: "])

    game_data = {
        "partner_id": partner_tg_id,
        "correct_res": correct_res,
        "answers": {user_id: None, partner_tg_id: None} 
    }
    active_math_games[user_id] = game_data
    active_math_games[partner_tg_id] = game_data

    await message.answer(
    f'10 секунд! Реши пример:\n\n{question["Пример: "]} = ?'
)

    await bot.send_message(
        partner_tg_id,
        f'10 секунд! Реши пример:\n\n{question["Пример: "]} = ?'
    )

    await asyncio.sleep(10.0)

    active_math_games.pop(user_id, None)
    active_math_games.pop(partner_tg_id, None)

    u1_ans = game_data["answers"][user_id]
    u2_ans = game_data["answers"][partner_tg_id]

    final_ans_u1 = u1_ans if u1_ans is not None else -99999.0
    final_ans_u2 = u2_ans if u2_ans is not None else -99999.0

    winner_data = check_winner(
        correct_res,
        message.from_user.id,
        final_ans_u1,
        partner_tg_id,
        final_ans_u2
    )

    winner_id = winner_data["Победитель: "]

    result_for_owner = f'Правильный ответ: {correct_res}\n\n' \
                f'Твой ответ: {final_ans_u1}\n' \
                f'Ответ собеседника: {final_ans_u2}\n\n'
    
    if winner_id == 0:
        result_for_owner += "Ничья!"
    elif winner_id == user_id:
        result_for_owner += "Ты победил!"
    else:
        result_for_owner += "Победил собеседник!"

    await message.answer(result_for_owner, parse_mode="Markdown")

    result_for_partner = f'Правильный ответ: {correct_res}\n\n' \
                f'Твой ответ: {final_ans_u2}\n' \
                f'Ответ собеседника: {final_ans_u1}\n\n'

    if winner_id == 0:
        result_for_partner += "Ничья!"
    elif winner_id == partner_tg_id:
        result_for_partner += "Ты победил!"
    else:
        result_for_partner += "Победил собеседник!"
    await bot.send_message(partner_tg_id, result_for_partner, parse_mode="Markdown")

@router.message(Command('fractal'))
async def send_fractal_handler(message: Message, db: AsyncSession):
    if not message.from_user:
        return
    
    logger.info(f"Пользователь {message.from_user.id} сделал запро сна фрактал")
    await message.answer('Секунду, пожалуйста...')

    try:
        loop = asyncio.get_running_loop()
        photo_bytes = await loop.run_in_executor(None, get_beatiful_fractal)

        photo_file_to_send = BufferedInputFile(photo_bytes, filename='fractal.png')
        await message.answer_photo(photo=photo_file_to_send, caption='Ваш уникальный фрактал')
    except Exception as e:
        logger.exception(f"Сбой при отправке фрактала юзеру {message.from_user.id}, {e}")
        await message.answer("Извините, при генерации фрактала что-то пошло не так, попробуйте позже")


@router.message(F.text, ~F.text.startswith("/"))
async def forward_handler(message: Message, bot: Bot, db: AsyncSession):
    if not message.from_user:
        return

    if (message.text or not is_float(message.text)) and message.text.startswith("/"):
        return

    service = ChatService(db)

    user_id = message.from_user.id

    if user_id in active_math_games:
        text = message.text.strip()

        if (is_float(text) or (text.startswith("-") and is_float(text[1:]))) and active_math_games[user_id]["answers"][user_id] is None:
            active_math_games[user_id]["answers"][user_id] = float(text)
            await message.answer('Ответ принят!')
            return

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