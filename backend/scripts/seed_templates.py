#!/usr/bin/env python3
"""Seed script to populate the database with story templates.

Usage:
    cd backend
    poetry run python scripts/seed_templates.py
"""
import asyncio
from datetime import datetime, timezone
from loguru import logger

from app.core.database import db
from app.models.template import Template, TemplateGenerationInputs


SEED_TEMPLATES = [
    {
        "name": "The Brave Little Dragon",
        "description": "A young dragon learns that being brave doesn't mean not being scared.",
        "icon": "\U0001F409",  # Dragon emoji
        "category": "fantasy",
        "tags": ["dragons", "courage", "self-discovery"],
        "age_range_min": 4,
        "age_range_max": 7,
        "generation_inputs": {
            "audience_age": 5,
            "topic": "A small dragon named Ember who is afraid of flying discovers that bravery means trying even when you're scared",
            "setting": "A magical mountain kingdom where dragons live in crystal caves above the clouds",
            "format": "storybook",
            "illustration_style": "watercolor",
            "characters": ["Ember the small purple dragon", "Grandmother Dragon who is wise and kind"],
            "page_count": 10,
        },
        "sort_order": 1,
    },
    {
        "name": "Ocean Friends Adventure",
        "description": "An underwater journey about friendship and helping others.",
        "icon": "\U0001F420",  # Tropical fish emoji
        "category": "animals",
        "tags": ["ocean", "friendship", "teamwork"],
        "age_range_min": 3,
        "age_range_max": 6,
        "generation_inputs": {
            "audience_age": 4,
            "topic": "A curious clownfish helps a lost baby sea turtle find its way home to the beach",
            "setting": "A colorful coral reef with seaweed forests and sandy ocean floor",
            "format": "storybook",
            "illustration_style": "cartoon",
            "characters": ["Coral the friendly clownfish", "Shelly the baby sea turtle"],
            "page_count": 8,
        },
        "sort_order": 2,
    },
    {
        "name": "Space Explorer Academy",
        "description": "Join young astronauts on their first mission to discover a new planet!",
        "icon": "\U0001F680",  # Rocket emoji
        "category": "adventure",
        "tags": ["space", "science", "exploration", "teamwork"],
        "age_range_min": 6,
        "age_range_max": 10,
        "generation_inputs": {
            "audience_age": 8,
            "topic": "Three junior astronauts from Space Explorer Academy discover a friendly alien on their first mission to a mysterious purple planet",
            "setting": "A futuristic space station and a mysterious purple planet with floating crystals and strange plants",
            "format": "comic",
            "illustration_style": "digital-painting",
            "characters": ["Captain Maya the brave leader", "Engineer Leo who loves gadgets", "Scientist Nova who studies aliens", "Zip the friendly purple alien"],
            "page_count": 12,
            "panels_per_page": 4,
        },
        "sort_order": 3,
    },
    {
        "name": "The Kindness Garden",
        "description": "A magical garden grows when children do kind things for others.",
        "icon": "\U0001F33B",  # Sunflower emoji
        "category": "educational",
        "tags": ["kindness", "emotions", "social-skills"],
        "age_range_min": 3,
        "age_range_max": 6,
        "generation_inputs": {
            "audience_age": 4,
            "topic": "Every time a child does something kind, a magical flower blooms in the village's forgotten garden",
            "setting": "A small friendly village with a mysterious empty garden in the center that everyone had forgotten about",
            "format": "storybook",
            "illustration_style": "watercolor",
            "characters": ["Lily the thoughtful girl who notices small things", "Various village children who learn about kindness"],
            "page_count": 10,
        },
        "sort_order": 4,
    },
    {
        "name": "Dinosaur Detective",
        "description": "Help Detective Rex solve the mystery of the missing eggs!",
        "icon": "\U0001F995",  # Sauropod emoji
        "category": "adventure",
        "tags": ["dinosaurs", "mystery", "problem-solving"],
        "age_range_min": 5,
        "age_range_max": 8,
        "generation_inputs": {
            "audience_age": 6,
            "topic": "Detective Rex the T-Rex investigates who took the eggs from the dinosaur nursery, following clues through the jungle",
            "setting": "A prehistoric jungle with a dinosaur village featuring cozy nests and mysterious caves",
            "format": "comic",
            "illustration_style": "cartoon",
            "characters": ["Detective Rex the clever T-Rex with a magnifying glass", "Officer Steggy the helpful deputy", "Mama Triceratops who is worried about her eggs"],
            "page_count": 10,
            "panels_per_page": 4,
        },
        "sort_order": 5,
    },
    {
        "name": "The Robot Who Learned to Feel",
        "description": "A little robot discovers emotions and what it means to have a friend.",
        "icon": "\U0001F916",  # Robot emoji
        "category": "educational",
        "tags": ["emotions", "friendship", "technology", "empathy"],
        "age_range_min": 5,
        "age_range_max": 9,
        "generation_inputs": {
            "audience_age": 7,
            "topic": "A helper robot named Beep starts experiencing feelings for the first time after befriending a lonely child named Sam",
            "setting": "A near-future city where friendly robots help with everyday tasks in homes and schools",
            "format": "storybook",
            "illustration_style": "digital-painting",
            "characters": ["Beep the curious robot learning about feelings", "Sam the lonely child who needs a friend"],
            "page_count": 12,
        },
        "sort_order": 6,
    },
    {
        "name": "Princess Knight Adventure",
        "description": "A princess who prefers swords to gowns rescues her kingdom.",
        "icon": "\u2694\uFE0F",  # Crossed swords emoji
        "category": "fantasy",
        "tags": ["princess", "adventure", "courage", "breaking-stereotypes"],
        "age_range_min": 5,
        "age_range_max": 9,
        "generation_inputs": {
            "audience_age": 7,
            "audience_gender": "Girl",
            "topic": "Princess Elena trades her crown for a sword to save her kingdom from a grumpy giant who just wants a friend",
            "setting": "A fairytale kingdom with a tall castle, an enchanted forest, and a lonely mountain where the misunderstood giant lives",
            "format": "comic",
            "illustration_style": "anime",
            "characters": ["Princess Elena the brave warrior princess", "Sir Whiskers the loyal cat knight", "Gregory the lonely giant who just wants friends"],
            "page_count": 12,
            "panels_per_page": 4,
        },
        "sort_order": 7,
    },
    {
        "name": "The Magic Treehouse Library",
        "description": "A secret library where books come to life and stories become real.",
        "icon": "\U0001F4DA",  # Books emoji
        "category": "fantasy",
        "tags": ["books", "reading", "imagination", "adventure"],
        "age_range_min": 6,
        "age_range_max": 10,
        "generation_inputs": {
            "audience_age": 8,
            "topic": "Twins discover a magical treehouse library where opening a book transports them into the story",
            "setting": "An ancient oak tree with a hidden cozy library full of glowing books, located in the backyard of their new home",
            "format": "storybook",
            "illustration_style": "watercolor",
            "characters": ["Mia the curious twin who loves reading", "Max the adventurous twin who loves action", "The Book Keeper, a mysterious owl who guards the library"],
            "page_count": 14,
        },
        "sort_order": 8,
    },
    {
        "name": "Bedtime in the Animal Kingdom",
        "description": "Follow different baby animals as they get ready for bed around the world.",
        "icon": "\U0001F319",  # Crescent moon emoji
        "category": "animals",
        "tags": ["bedtime", "animals", "calming", "educational"],
        "age_range_min": 2,
        "age_range_max": 5,
        "generation_inputs": {
            "audience_age": 3,
            "topic": "Baby animals around the world say goodnight in their own special ways: a koala in Australia, a polar bear in the Arctic, and a lion in Africa",
            "setting": "Different beautiful nighttime landscapes: moonlit eucalyptus forest in Australia, starry ice plains in the Arctic, and warm African savanna under a big golden moon",
            "format": "storybook",
            "illustration_style": "watercolor",
            "characters": ["Baby koala snuggling with mama", "Baby polar bear in a snow den", "Baby lion cub yawning on the savanna"],
            "page_count": 8,
        },
        "sort_order": 9,
    },
    {
        "name": "Super Veggie Squad",
        "description": "Vegetables come to life to teach kids about healthy eating!",
        "icon": "\U0001F955",  # Carrot emoji
        "category": "educational",
        "tags": ["health", "nutrition", "vegetables", "superheroes"],
        "age_range_min": 4,
        "age_range_max": 7,
        "generation_inputs": {
            "audience_age": 5,
            "topic": "Captain Carrot and the Super Veggie Squad help a picky eater discover that vegetables give you real superpowers like strong muscles and sharp eyes",
            "setting": "A kitchen that transforms into a superhero headquarters when parents are not looking",
            "format": "comic",
            "illustration_style": "cartoon",
            "characters": ["Captain Carrot the orange leader with super vision", "Broccoli Buddy with super strength", "Tomato Girl who is super fast", "The Picky Eater Kid who learns to love veggies"],
            "page_count": 10,
            "panels_per_page": 4,
        },
        "sort_order": 10,
    },
]


async def seed_templates():
    """Seed the database with story templates."""
    logger.info("Connecting to database...")
    await db.connect_db()

    try:
        # Check if templates already exist
        existing_count = await Template.count()
        if existing_count > 0:
            logger.warning(f"Found {existing_count} existing templates. Clearing and re-seeding...")
            await Template.delete_all()

        # Insert templates
        logger.info(f"Seeding {len(SEED_TEMPLATES)} templates...")
        now = datetime.now(timezone.utc)

        for template_data in SEED_TEMPLATES:
            generation_inputs = TemplateGenerationInputs(**template_data["generation_inputs"])
            template = Template(
                name=template_data["name"],
                description=template_data["description"],
                generation_inputs=generation_inputs,
                age_range_min=template_data["age_range_min"],
                age_range_max=template_data["age_range_max"],
                category=template_data["category"],
                tags=template_data["tags"],
                icon=template_data.get("icon"),
                sort_order=template_data["sort_order"],
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            await template.insert()
            logger.info(f"  Created: {template.icon} {template.name}")

        final_count = await Template.count()
        logger.info(f"Successfully seeded {final_count} templates!")

    finally:
        await db.close_db()


if __name__ == "__main__":
    asyncio.run(seed_templates())
