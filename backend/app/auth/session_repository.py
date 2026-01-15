from app.db.repository import BaseRepository

class SessionRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["sessions"])

    async def find_by_token(self, token: str):
        return await self.find_one({"token": token})
