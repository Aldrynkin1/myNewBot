from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.match import Match

class MatchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_match(self, user1_id: int, user2_id: int) -> Match:
        match = Match(user1_id = user1_id, user2_id = user2_id, active=True)
        self.db.add(match)
        await self.db.commit()
        await self.db.refresh(match)
        return match
    
    async def get_active_match_by_user(self, user_id: int) -> Match | None:
        if not user_id:
            return None
        
        get_match = select(Match).where(
            Match.active.is_(True),
            or_(
                Match.user1_id == user_id,
                Match.user2_id == user_id
                )
        )
        res = await self.db.execute(get_match)
        return res.scalar_one_or_none()

    async def deactivate_match(self, match: Match):
        match.active = False
        await self.db.commit()