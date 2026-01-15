from app.db.repository import BaseRepository

class InteractionRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["interactions"])

    async def find_active_by_doctor(self, doctor_id: str, tenant_id: str):
        return await self.find_one({
            "doctor_id": doctor_id,
            "tenant_id": tenant_id,
            "status": "active"
        })
