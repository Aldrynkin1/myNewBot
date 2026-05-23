from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select 
from app.models.user import User
from app.repositories.match_repo import MatchRepository
from app.repositories.user_repo import UserRepository

class MatchMakingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.match_repo = MatchRepository(db)

    async def search(self, tg_id: int, usname: str | None, nickname: str) -> tuple[User, User] | None:
        user = await self.user_repo.get_or_create(tg_id, usname, nickname)
        active_match = await self.match_repo.get_active_match_by_user(user.id)

        if active_match: return None
        
        stmt = select(User).where(User.state == 'waiting', User.id != user.id).limit(1)
        res = await self.db.execute(stmt)
        partner = res.scalar_one_or_none()

        if not partner:
            await self.user_repo.set_state(user, 'waiting')
            return None
        
        await self.match_repo.create_match(user.id, partner.id)

        await self.user_repo.set_state(user, "chatting")
        await self.user_repo.set_state(partner, "chatting")
        
        return user, partner