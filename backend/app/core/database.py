"""MongoDB database connection and initialization."""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from loguru import logger

from app.core.config import settings


class Database:
    """MongoDB database manager."""

    client: Optional[AsyncIOMotorClient] = None
    db_name: str = settings.mongodb_db_name

    @classmethod
    async def connect_db(cls) -> None:
        """Create database connection and initialize Beanie ODM."""
        try:
            cls.client = AsyncIOMotorClient(settings.mongodb_url, tz_aware=True)
            # Test connection
            await cls.client.admin.command("ping")
            logger.info(f"Connected to MongoDB at {settings.mongodb_url}")

            # Initialize Beanie with document models
            from app.models.storybook import Storybook
            from app.models.settings import AppSettings
            from app.models.user import User

            await init_beanie(
                database=cls.client[cls.db_name],
                document_models=[Storybook, AppSettings, User],
            )
            logger.info("Beanie ODM initialized successfully")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def close_db(cls) -> None:
        """Close database connection."""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection")

    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        """Get MongoDB client instance."""
        if not cls.client:
            raise RuntimeError("Database not initialized. Call connect_db() first.")
        return cls.client

    @classmethod
    def get_database(cls):
        """Get database instance."""
        if not cls.client:
            raise RuntimeError("Database not initialized. Call connect_db() first.")
        return cls.client[cls.db_name]


# Convenience alias
db = Database
