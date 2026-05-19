from sqlalchemy import select

from app.repositories.user_repo import UserRepository 
from app.repositories.match_repo import MatchRepository 

class ChatService:
    def __init__(self, db):
        self.db = db
        self.user_repo = UserRepository(db)
        self.match_repo = MatchRepository(db)

    async def get_partner_id(self, tg_id: int, usname: str | None, nickname: str) -> int | None:
        user = await self.user_repo.get_or_create(tg_id, usname, nickname)
        match = await self.match_repo.get_active_match_by_user(user.id)

        if not match:
            return None
        
        partner_id = match.user2_id if match.user1_id == user.id else match.user1_id
        
        partner = await self.user_repo.db.get(type(user), partner_id)

        return partner.tg_id if partner else None
    
    async def stop_chat(self, user_tg_id: int, usname: str | None, nickname:str) -> None:
        user = await self.user_repo.get_or_create(user_tg_id, usname, nickname)

        match = await self.match_repo.get_active_match_by_user(user.id)
        if not match:
            return
        
        partner_id = match.user2_id if match.user1_id == user.id else match.user1_id
        partner = await self.db.get(type(user), partner_id)

        await self.match_repo.deactivate_match(match)

        await self.user_repo.set_state(user, "idle")
        if partner:
            await self.user_repo.set_state(partner, "idle")
        
    async def report_partner(self, user_tg_id: int, usname: str | None, nickname:str) -> None:
        user = await self.user_repo.get_or_create(user_tg_id, usname, nickname)

        match = await self.match_repo.get_active_match_by_user(user.id)
        if not match:
            return
        
        partner_id = match.user2_id if match.user1_id == user.id else match.user1_id
        partner = await self.db.get(type(user), partner_id)

        if partner:
            await self.user_repo.report_user(partner)
            if partner.report_count >= 5:
                await self.user_repo.ban_user(partner)
                
    async def find_partner(self, user_tg_id: int, usname: str | None, nickname:str) -> int | None:
        user = await self.user_repo.get_or_create(user_tg_id, usname, nickname)

        if user.state == "chatting":
            match = await self.match_repo.get_active_match_by_user(user.id)
            if match:
                partner_id = match.user2_id if match.user1_id == user.id else match.user1_id
                partner = await self.db.get(type(user), partner_id)
                return partner.tg_id if partner else None

        waiting_user_query = await self.db.execute(
            select(type(user)).where(type(user).state == "waiting", type(user).id != user.id)
        )
        waiting_user = waiting_user_query.scalars().first()

        if waiting_user:
            await self.match_repo.create_match(user.id, waiting_user.id)
            await self.user_repo.set_state(user, "chatting")
            await self.user_repo.set_state(waiting_user, "chatting")
            return waiting_user.tg_id
        
        await self.user_repo.set_state(user, "waiting")
        return None