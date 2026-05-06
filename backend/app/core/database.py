from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


class Database:
    client: AsyncIOMotorClient = None

    async def connect_to_database(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        print(f"Connected to MongoDB: {settings.DATABASE_NAME}")

    async def close_database_connection(self):
        self.client.close()
        print("Closed MongoDB connection")

    def get_database(self):
        return self.client[settings.DATABASE_NAME]


db = Database()