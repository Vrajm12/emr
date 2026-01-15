from app.db.repository import BaseRepository

class TenantRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["tenants"])

    async def find_by_name(self, name: str):
        return await self.find_one({"name": name})
