import uuid
from datetime import datetime

class BaseRepository:
    def __init__(self, collection):
        self.collection = collection

    async def create(self, data: dict):
        data["_id"] = str(uuid.uuid4())
        data["created_at"] = datetime.utcnow().isoformat()
        await self.collection.insert_one(data)
        return data

    async def find_one(self, query: dict):
        return await self.collection.find_one(query)

    async def find_many(self, query: dict):
        cursor = self.collection.find(query)
        return await cursor.to_list(length=100)

    async def update(self, query: dict, data: dict):
        await self.collection.update_one(query, {"$set": data})

    async def delete(self, query: dict):
        await self.collection.delete_one(query)
