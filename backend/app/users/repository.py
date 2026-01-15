from app.db.repository import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["users"])

    async def find_by_email(self, email: str):
        return await self.find_one({"email": email})

    async def find_by_id(self, user_id: str):
        return await self.find_one({"_id": user_id})
