from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoClient:
    client: AsyncIOMotorClient = None

    mongo = MongoClient()
    
    async def connect_to_mongo(self):
        mongo.client = AsyncIOMotorClient(settings.MONGO_URL)
        print("Connected to MongoDB")

        async def close_mongo_connection():
            mongo.client.close()
            print("Closed connection to MongoDB")

            def get_db():
                return mongo.client[settings.MONGO_DB_NAME]