from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from shared.config import get_settings


class MongoDBClient:

    def __init__(self):
        settings = get_settings()

        self.client = AsyncIOMotorClient(
            settings.MONGODB_URL
        )

        self.database: AsyncIOMotorDatabase = self.client[
            settings.MONGODB_DATABASE
        ]

    def get_database(self) -> AsyncIOMotorDatabase:
        return self.database

    def close(self) -> None:
        self.client.close()