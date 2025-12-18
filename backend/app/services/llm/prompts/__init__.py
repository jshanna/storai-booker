"""Prompt templates for story generation agents."""
from app.services.llm.prompts.story_planning import (
    build_story_planning_prompt,
    StoryPlanningOutput,
)
from app.services.llm.prompts.page_generation import (
    build_page_generation_prompt,
    PageGenerationOutput,
)
from app.services.llm.prompts.comic_page_generation import (
    build_comic_page_generation_prompt,
    ComicPageGenerationOutput,
    PanelOutput,
    DialogueOutput,
    SoundEffectOutput,
    get_layout_for_panel_count,
)
from app.services.llm.prompts.validation import (
    build_validation_prompt,
    ValidationOutput,
)

__all__ = [
    "build_story_planning_prompt",
    "StoryPlanningOutput",
    "build_page_generation_prompt",
    "PageGenerationOutput",
    "build_comic_page_generation_prompt",
    "ComicPageGenerationOutput",
    "PanelOutput",
    "DialogueOutput",
    "SoundEffectOutput",
    "get_layout_for_panel_count",
    "build_validation_prompt",
    "ValidationOutput",
]
