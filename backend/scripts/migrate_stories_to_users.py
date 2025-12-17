#!/usr/bin/env python3
"""
Migration script to add user_id to existing stories.

This script:
1. Finds all stories without a user_id field
2. Assigns them to a "default" or specified admin user
3. Ensures settings exist for the admin user

Run with:
    poetry run python scripts/migrate_stories_to_users.py [admin_user_id]

If no admin_user_id is provided, stories will be assigned to "admin".
"""

import asyncio
import sys
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")


async def run_migration(admin_user_id: str = "admin"):
    """
    Run the migration to add user_id to existing stories.

    Args:
        admin_user_id: User ID to assign to orphaned stories
    """
    from app.core.config import settings
    from app.models.storybook import Storybook
    from app.models.settings import AppSettings
    from app.models.user import User

    # Connect to MongoDB
    logger.info(f"Connecting to MongoDB: {settings.mongodb_url}")
    client = AsyncIOMotorClient(settings.mongodb_url)

    # Initialize Beanie
    await init_beanie(
        database=client[settings.mongodb_db_name],
        document_models=[Storybook, AppSettings, User],
    )

    logger.info(f"Connected to database: {settings.mongodb_db_name}")

    # Step 1: Find stories without user_id
    # Note: user_id is now required, but legacy data might not have it
    orphaned_stories = await Storybook.find(
        {"$or": [{"user_id": {"$exists": False}}, {"user_id": None}, {"user_id": ""}]}
    ).to_list()

    logger.info(f"Found {len(orphaned_stories)} stories without user_id")

    if orphaned_stories:
        # Step 2: Check if admin user exists, create if not
        admin_user = await User.find_one({"email": f"{admin_user_id}@local.admin"})

        if not admin_user:
            logger.info(f"Creating admin user: {admin_user_id}")
            admin_user = User(
                email=f"{admin_user_id}@local.admin",
                hashed_password="$2b$12$migration_placeholder_hash",  # Cannot login
                full_name="Admin (Migration)",
                is_active=True,
                email_verified=False,
            )
            await admin_user.insert()
            admin_user_id = str(admin_user.id)
            logger.info(f"Created admin user with ID: {admin_user_id}")
        else:
            admin_user_id = str(admin_user.id)
            logger.info(f"Using existing admin user: {admin_user_id}")

        # Step 3: Update orphaned stories
        updated_count = 0
        for story in orphaned_stories:
            story.user_id = admin_user_id
            story.updated_at = datetime.now(timezone.utc)
            await story.save()
            updated_count += 1
            logger.info(f"Updated story {story.id}: {story.title}")

        logger.info(f"Updated {updated_count} stories with user_id: {admin_user_id}")

        # Step 4: Ensure settings exist for admin user
        admin_settings = await AppSettings.find_one({"user_id": admin_user_id})
        if not admin_settings:
            logger.info(f"Creating default settings for admin user: {admin_user_id}")
            admin_settings = AppSettings(user_id=admin_user_id)
            await admin_settings.insert()
            logger.info("Created default settings for admin user")
        else:
            logger.info("Admin user already has settings")

    # Step 5: Migrate "default" settings to admin user if needed
    default_settings = await AppSettings.find_one({"user_id": "default"})
    if default_settings:
        logger.info("Found 'default' settings document")
        # Keep it for backward compatibility during migration period
        logger.info("Keeping 'default' settings for backward compatibility")

    # Step 6: Summary
    total_stories = await Storybook.count()
    stories_with_user = await Storybook.find(
        {"user_id": {"$exists": True, "$ne": None, "$ne": ""}}
    ).count()

    logger.info("=" * 50)
    logger.info("Migration Summary:")
    logger.info(f"  Total stories: {total_stories}")
    logger.info(f"  Stories with user_id: {stories_with_user}")
    logger.info(f"  Stories migrated: {len(orphaned_stories)}")
    logger.info("=" * 50)

    # Close connection
    client.close()
    logger.info("Migration complete")


def main():
    """Main entry point."""
    admin_user_id = sys.argv[1] if len(sys.argv) > 1 else "admin"
    logger.info(f"Running migration with admin user: {admin_user_id}")
    asyncio.run(run_migration(admin_user_id))


if __name__ == "__main__":
    main()
