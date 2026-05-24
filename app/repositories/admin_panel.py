from app.models.match import Match
from app.repositories.match_repo import MatchRepository
from app.repositories.user_repo import UserRepository
from app.models.user import User
from sqlalchemy import delete, select, func

class AdminPanelRepository:
    def __init__(self, db):
        self.db = db
        self.user_repo = UserRepository(db)
        self.match_repo = MatchRepository(db)

    async def get_all_users(self) -> list[User]:
        return (await self.db.execute(self.db.query(User))).scalars().all()
    
    async def get_all_matches(self) -> list[Match]:
        return (await self.db.execute(self.db.query(Match))).scalars().all()
    
    async def ban_user(self, user_id: int):
        user = await self.db.get(User, user_id)
        if user:
            user.banned = True
            await self.db.commit()
            
    async def unban_user(self, user_id: int):
        user = await self.db.get(User, user_id)
        if user:
            user.banned = False
            await self.db.commit()
            
    async def delete_match(self, match_id: int):
        match = await self.db.get(Match, match_id)
        if match:
            await self.db.delete(match)
            await self.db.commit()
            
    async def get_user_by_id(self, user_id: int) -> User | None | str:
        user = await self.db.get(User, user_id)
        
        if not user:
            return f'user with id {user_id} not found'
        
        if user.banned:
            return f'user with id {user_id} is banned'
        
        if user and not user.banned:
            return user
        
    async def get_match_by_id(self, match_id: int) -> Match | None:
        match = await self.db.get(Match, match_id)
        
        if not match:
            return None
        
        return match
    
    async def get_user_by_name(self, name: str) -> User | None:
        result = await self.db.execute(self.db.query(User).filter(User.name == name))
        return result.scalar_one_or_none()
    
    async def ban_user_by_name(self, name: str):
        user = await self.get_user_by_name(name)
        if user:
            user.banned = True
            await self.db.commit()
            
    async def unban_user_by_name(self, name: str):
        user = await self.get_user_by_name(name)
        if user:
            user.banned = False
            await self.db.commit()
            
    async def get_statistics(self) -> dict:
        total_users = await self.db.execute(select(func.count(User.id)))
        total_users = total_users.scalar()
        
        active_matches = await self.db.execute(select(func.count(Match.id)).where(Match.active.is_(True)))
        active_matches = active_matches.scalar()
        
        banned_users = await self.db.execute(select(func.count(User.id)).where(User.banned.is_(True)))
        banned_users = banned_users.scalar()
        
        total_matches = await self.db.execute(select(func.count(Match.id)))
        total_matches = total_matches.scalar()
        
        return {
            "total_users": total_users,
            "total_matches": total_matches,
            "active_matches": active_matches,
            "banned_users": banned_users
        }
        
    async def get_user_by_tg_id(self, tg_id: int) -> User | None:
        result = await self.db.execute(self.db.query(User).filter(User.tg_id == tg_id))
        return result.scalar_one_or_none()
    
    async def ban_user_by_tg_id(self, tg_id: int):
        user = await self.get_user_by_tg_id(tg_id)
        if not user:
            return f'user with tg_id {tg_id} not found'
        
        user.banned = True
        return user
        
    async def unban_user_by_tg_id(self, tg_id: int):
        user = await self.get_user_by_tg_id(tg_id)
        if not user:
            return f'user with tg_id {tg_id} not found'
            
        user.banned = False
        return user
    
    async def delete_user_by_tg_id(self, tg_id: int):
        user = await self.get_user_by_tg_id(tg_id)
        if not user:
            return f'user with tg_id {tg_id} not found'
        
        await self.db.execute(
            delete(Match).where((Match.user1_id == user.id) | (Match.user2_id == user.id))
        )
        await self.db.delete(user)
        await self.db.commit()
        return f'user with tg_id {tg_id} deleted successfully'
    
    async def add_new_admin(self, tg_id: int) -> User | str:
        
        user = await self.user_repo.get_user_by_id(tg_id) 
        
        if not user:
            return f"Пользователь с TG ID {tg_id} еще не запускал бота."
            
        user.is_admin = True
        return user

    
    async def delete_admin(self, tg_id: int) -> str:
        user = await self.get_user_by_tg_id(tg_id)
        if not user:
            return f'user with tg_id {tg_id} not found'
        user.is_admin = False
        await self.db.commit()
        return f'user with tg_id {tg_id} removed from admins successfully'
    
    async def get_all_admins(self) -> list[User]:
        result = await self.db.execute(self.db.query(User).filter(User.is_admin.is_(True)))
        return result.scalars().all()
    
    async def get_all_banned_users(self) -> list[User]:
        result = await self.db.execute(self.db.query(User).filter(User.banned.is_(True)))
        return result.scalars().all()
    
    async def get_all_active_matches(self) -> list[Match]:
        result = await self.db.execute(self.db.query(Match).filter(Match.active.is_(True)))
        return result.scalars().all()