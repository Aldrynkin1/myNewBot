import os

from dotenv import load_dotenv
load_dotenv()

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.admin_panel import AdminPanelRepository



router = Router()

admin_id = int(os.getenv("ADMIN_USER_ID", "0"))


def is_admin(user_id: int) -> bool:
    return user_id == admin_id


@router.message(Command("admin_stats"))
async def admin_stats_handler(message: Message, db: AsyncSession):
    if not message.from_user:
        return

    if not is_admin(message.from_user.id):
        await message.answer("У тебя нет доступа.")
        return

    repo = AdminPanelRepository(db)

    stats = await repo.get_statistics()

    stats_message = (
        f"Статистика бота:\n\n"
        f"Всего пользователей: {stats['total_users']}\n"
        f"Заблокированных: {stats['banned_users']}\n"
        f"Всего матчей: {stats['total_matches']}\n"
        f"Активных матчей: {stats['active_matches']}"
    )

    await message.answer(stats_message)


@router.message(Command("ban"))
async def ban_handler(message: Message, db: AsyncSession):
    if not message.from_user:
        return

    if not is_admin(message.from_user.id):
        await message.answer("У тебя нет доступа.")
        return

    if not message.text:
        await message.answer("Использование: /ban <tg_id>")
        return

    args = message.text.split()

    if len(args) < 2:
        await message.answer("Использование: /ban <tg_id>")
        return

    try:
        tg_id = int(args[1])
    except ValueError:
        await message.answer("tg_id должен быть числом.")
        return

    repo = AdminPanelRepository(db)
    result = await repo.ban_user_by_tg_id(tg_id)

    if isinstance(result, str):
        await message.answer(result)
        return

    await db.commit()
    await message.answer(f"Пользователь {result.username} (ID: {result.tg_id}) забанен!")


@router.message(Command("unban"))
async def unban_handler(message: Message, db: AsyncSession):
    if not message.from_user:
        return

    if not is_admin(message.from_user.id):
        await message.answer("У тебя нет доступа.")
        return

    if not message.text:
        await message.answer("Использование: /unban <tg_id>")
        return

    args = message.text.split()

    if len(args) < 2:
        await message.answer("Использование: /unban <tg_id>")
        return

    try:
        tg_id = int(args[1])
    except ValueError:
        await message.answer("tg_id должен быть числом.")
        return

    repo = AdminPanelRepository(db)
    result = await repo.unban_user_by_tg_id(tg_id)

    if isinstance(result, str):
        await message.answer(result)
        return

    await db.commit()
    await message.answer(f"Пользователь {result.username} (ID: {result.tg_id}) разбанен!")



@router.message(Command("delete_user"))
async def delete_user_handler(message: Message, db: AsyncSession):
    if not message.from_user:
        return

    if not is_admin(message.from_user.id):
        await message.answer("У тебя нет доступа.")
        return

    if not message.text:
        await message.answer("Использование: /delete_user <tg_id>")
        return

    args = message.text.split()

    if len(args) < 2:
        await message.answer("Использование: /delete_user <tg_id>")
        return

    try:
        tg_id = int(args[1])
    except ValueError:
        await message.answer("tg_id должен быть числом.")
        return

    repo = AdminPanelRepository(db)

    result = await repo.delete_user_by_tg_id(tg_id)

    await db.commit()

    await message.answer(str(result))


@router.message(Command("admin_help"))
async def admin_help_handler(message: Message):
    if not message.from_user:
        return

    if not is_admin(message.from_user.id):
        await message.answer("У тебя нет доступа.")
        return

    await message.answer(
        "Админ-команды:\n\n"
        "/admin_stats — статистика\n"
        "/ban <tg_id>\n"
        "/unban <tg_id>\n"
        "/delete_user <tg_id>\n"
        "/add_admin <tg_id> — добавить нового админа\n"
        ""
    )

@router.message(Command("add_admin"))
async def add_admin_handler(message: Message, db: AsyncSession):
    if not message.from_user:
        return

    if not is_admin(message.from_user.id):
        await message.answer("У тебя нет доступа.")
        return

    if not message.text:
        await message.answer("Использование: /add_admin <tg_id>")
        return

    args = message.text.split()

    if len(args) < 2:
        await message.answer("Использование: /add_admin <tg_id>")
        return

    try:
        target_tg_id = int(args[1])
    except ValueError:
        await message.answer("tg_id должен быть числом.")
        return

    repo = AdminPanelRepository(db)
    result = await repo.add_new_admin(target_tg_id)

    if isinstance(result, str):
        await message.answer(result)
        return

    await db.commit()
    await message.answer(f"Пользователь {result.username} (ID: {result.tg_id}) успешно стал админом!")