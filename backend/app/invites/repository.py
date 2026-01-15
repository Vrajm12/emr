from app.db.repository import BaseRepository

class InviteRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["invites"])

    async def find_by_token(self, token: str):
        return await self.find_one({"token": token, "status": "pending"})
