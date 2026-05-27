import os
from dotenv import load_dotenv

load_dotenv()

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.admin_panel import AdminPanelRepository

router = Router()

SUPER_ADMIN_ID = int(os.getenv("ADMIN_USER_ID", "0"))


async def check_admin_access(user_id: int, db: AsyncSession) -> bool:
    if user_id == SUPER_ADMIN_ID:
        return True
        
    repo = AdminPanelRepository(db)
    user = await repo.get_user_by_tg_id(user_id)
    
    return user is not None and user.is_admin


@router.message(Command("admin_stats"))
async def admin_stats_handler(message: Message, db: AsyncSession):
    if not message.from_user or not await check_admin_access(message.from_user.id, db):
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
async def ban_handler(message: Message, command: CommandObject, db: AsyncSession):
    if not message.from_user or not await check_admin_access(message.from_user.id, db):
        await message.answer("У тебя нет доступа.")
        return

    if not command.args:
        await message.answer("Использование: /ban <tg_id>")
        return

    try:
        tg_id = int(command.args.split()[0])
    except (ValueError, IndexError):
        await message.answer("tg_id должен быть числом.")
        return

    repo = AdminPanelRepository(db)
    result = await repo.ban_user_by_tg_id(tg_id)

    if isinstance(result, str):
        await message.answer(result)
        return

    await db.commit()
    user_name = f"@{result.username}" if result.username else f"ID: {result.tg_id}"
    await message.answer(f"Пользователь {user_name} забанен!")


@router.message(Command("unban"))
async def unban_handler(message: Message, command: CommandObject, db: AsyncSession):
    if not message.from_user or not await check_admin_access(message.from_user.id, db):
        await message.answer("У тебя нет доступа.")
        return

    if not command.args:
        await message.answer("Использование: /unban <tg_id>")
        return

    try:
        tg_id = int(command.args.split()[0])
    except (ValueError, IndexError):
        await message.answer("tg_id должен быть числом.")
        return

    repo = AdminPanelRepository(db)
    result = await repo.unban_user_by_tg_id(tg_id)

    if isinstance(result, str):
        await message.answer(result)
        return

    await db.commit()
    user_name = f"@{result.username}" if result.username else f"ID: {result.tg_id}"
    await message.answer(f"Пользователь {user_name} разбанен!")


@router.message(Command("delete_user"))
async def delete_user_handler(message: Message, command: CommandObject, db: AsyncSession):
    if not message.from_user or not await check_admin_access(message.from_user.id, db):
        await message.answer("У тебя нет доступа.")
        return

    if not command.args:
        await message.answer("Использование: /delete_user <tg_id>")
        return

    try:
        tg_id = int(command.args.split()[0])
    except (ValueError, IndexError):
        await message.answer("tg_id должен быть числом.")
        return

    repo = AdminPanelRepository(db)
    result = await repo.delete_user_by_tg_id(tg_id)

    await db.commit()
    await message.answer(str(result))


@router.message(Command("admin_help"))
async def admin_help_handler(message: Message, db: AsyncSession):
    if not message.from_user or not await check_admin_access(message.from_user.id, db):
        await message.answer("У тебя нет доступа.")
        return

    await message.answer(
        "Админ-команды:\n\n"
        "/admin_stats — статистика\n"
        "/get_user_info <tg_id> — инфо о юзере\n"
        "/ban <tg_id> — бан по ID\n"
        "/unban <tg_id> — разбан по ID\n"
        "/delete_user <tg_id> — удаление из базы\n"
        "/add_admin <tg_id> — добавить нового админа\n"
        "/get_all_users — список всех пользователей\n"
        "/get_admins — список всех админов\n"
        "/get_banned — список забаненных\n"
        "/delete_admin <tg_id> — разжаловать админа (только создатель)\n"

    )


@router.message(Command("add_admin"))
async def add_admin_handler(message: Message, command: CommandObject, db: AsyncSession):
    if not message.from_user or not await check_admin_access(message.from_user.id, db):
        await message.answer("У тебя нет доступа.")
        return

    if not command.args:
        await message.answer("Использование: /add_admin <tg_id>")
        return

    try:
        target_tg_id = int(command.args.split()[0])
    except (ValueError, IndexError):
        await message.answer("tg_id должен быть числом.")
        return

    repo = AdminPanelRepository(db)
    result = await repo.add_new_admin(target_tg_id, added_by=message.from_user.id)

    if isinstance(result, str):
        await message.answer(result)
        return

    await db.commit()
    user_name = f"@{result.username}" if result.username else f"ID: {result.tg_id}"
    await message.answer(f"Пользователь {user_name} успешно стал админом!")


@router.message(Command("get_user_info"))
async def get_user_info_handler(message: Message, command: CommandObject, db: AsyncSession):
    if not message.from_user or not await check_admin_access(message.from_user.id, db):
        await message.answer("У тебя нет доступа.")
        return

    if not command.args:
        await message.answer("Использование: /get_user_info <tg_id>")
        return

    try:
        target_tg_id = int(command.args.split()[0])
    except (ValueError, IndexError):
        await message.answer("tg_id должен быть числом.")
        return

    repo = AdminPanelRepository(db)
    user = await repo.get_user_by_tg_id(target_tg_id)

    if not user:
        await message.answer(f"Пользователь с TG ID {target_tg_id} не найден.")
        return

    user_info = (
        f"Информация о пользователе:\n\n"
        f"ID: {user.tg_id}\n"
        f"Имя: {user.name}\n"
        f"Username: @{user.username if user.username else 'нет'}\n"
        f"Заблокирован: {'Да' if user.banned else 'Нет'}\n"
        f"Админ: {'Да' if user.is_admin else 'Нет'}\n"
        f"Количество репортов: {user.report_count}"
    )

    await message.answer(user_info)

@router.message(Command("get_all_users"))
async def get_all_users_handler(message: Message, db: AsyncSession):
    if not message.from_user or not await check_admin_access(message.from_user.id, db):
        await message.answer("У тебя нет доступа.")
        return

    repo = AdminPanelRepository(db)
    users = await repo.get_all_users()

    if not users:
        await message.answer("В базе данных еще нет пользователей.")
        return

    text = "Список всех пользователей:\n\n"
    for u in users:
        status = "БАН" if u.banned else ("АДМИН" if u.is_admin else "Юзер")
        if u.tg_id == SUPER_ADMIN_ID:
            status = "Владелец"
        username = f"@{u.username}" if u.username else "нет юзернейма"
        line = f"• {u.name} ({username}) | TG ID: {u.tg_id} [{status}]\n"
        
        if len(text) + len(line) > 3900:
            await message.answer(text)
            text = ""
        text += line

    if text:
        await message.answer(text)


@router.message(Command("get_admins"))
async def get_admins_handler(message: Message, db: AsyncSession):
    if not message.from_user or not await check_admin_access(message.from_user.id, db):
        await message.answer("У тебя нет доступа.")
        return

    repo = AdminPanelRepository(db)
    admins = await repo.get_all_admins()

    text = "Список администраторов бота:\n\n"
    for a in admins:
        username = f"@{a.username}" if a.username else "нет юзернейма"
        text += f"• {a.name} ({username}) | TG ID: {a.tg_id}\n"

    await message.answer(text)


@router.message(Command("get_banned"))
async def get_banned_handler(message: Message, db: AsyncSession):
    if not message.from_user or not await check_admin_access(message.from_user.id, db):
        await message.answer("У тебя нет доступа.")
        return

    repo = AdminPanelRepository(db)
    banned = await repo.get_all_banned_users()

    if not banned:
        await message.answer("Заблокированных пользователей нет. База чиста!")
        return

    text = "Список забаненных пользователей:\n\n"
    for b in banned:
        username = f"@{b.username}" if b.username else "нет юзернейма"
        text += f"• {b.name} ({username}) | TG ID: {b.tg_id}\n"

    await message.answer(text)


@router.message(Command("delete_admin"))
async def delete_admin_handler(message: Message, command: CommandObject, db: AsyncSession):
    if not message.from_user or message.from_user.id != SUPER_ADMIN_ID:
        await message.answer("Эта команда доступна только Главному Администратору.")
        return

    if not command.args:
        await message.answer("Использование: /delete_admin <tg_id>")
        return

    try:
        tg_id = int(command.args.split()[1])
    except (ValueError, IndexError):
        await message.answer("tg_id должен быть числом.")
        return

    repo = AdminPanelRepository(db)
    result = await repo.delete_admin(tg_id)
    
    await db.commit()
    await message.answer(str(result))