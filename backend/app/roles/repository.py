from app.db.repository import BaseRepository

class RoleRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["roles"])

    async def find_by_name(self, name: str):
        return await self.find_one({"name": name})
