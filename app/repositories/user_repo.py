from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_user_by_id(self, id: int) -> User | None:
        get_user = select(User).where(User.id == id)
        user = await self.db.execute(get_user)
        return user.scalar_one_or_none()
    
    async def create_user(self, id: int, username: str | None, name: str) -> User:
        new_user = User(tg_id=id, username=username, name=name or username or f"user_{id}")
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
    
    async def get_or_create(self, tg_id: int, username: str | None, nickname: str) -> User:
        query = select(User).where(User.tg_id == tg_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            return user
            
        return await self.create_user(tg_id, username, nickname)

    async def set_state(self, user: User, state: str):
        user.state = state
        await self.db.commit()
        
    async def report_user(self, user: User):
        user.report_count += 1
        await self.db.commit()

    async def ban_user(self, user: User):
        user.banned = True
        await self.db.commit()