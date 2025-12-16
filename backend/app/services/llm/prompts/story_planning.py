"""Prompt templates for story planning (coordinating agent)."""
from typing import List
from pydantic import BaseModel, Field

from app.models.storybook import GenerationInputs, CharacterDescription


class StoryPlanningOutput(BaseModel):
    """Structured output for story planning."""

    title: str = Field(
        description="Catchy, engaging book title that captures the story's essence (3-8 words)"
    )
    character_descriptions: List[CharacterDescription] = Field(
        description="Detailed descriptions of all characters in the story"
    )
    character_relations: str = Field(
        description="How the characters relate to each other (if multiple)"
    )
    story_outline: str = Field(
        description="Overall narrative arc with beginning, middle, and end"
    )
    page_outlines: List[str] = Field(
        description="One outline for each page describing what happens"
    )
    illustration_style_guide: str = Field(
        description="Detailed guide for consistent illustration style"
    )


def build_story_planning_prompt(inputs: GenerationInputs) -> str:
    """
    Build prompt for story planning.

    Args:
        inputs: User-provided generation inputs

    Returns:
        Formatted prompt string for the coordinating agent
    """
    # Age-appropriate guidelines
    age_guidelines = _get_age_guidelines(inputs.audience_age)

    # Build character list
    characters_str = ", ".join(inputs.characters) if inputs.characters else "the main character"

    # Build prompt
    prompt = f"""You are an expert children's story writer creating a {inputs.format} for a {inputs.audience_age}-year-old audience.

**Story Parameters:**
- Topic: {inputs.topic}
- Setting: {inputs.setting}
- Characters: {characters_str}
- Illustration Style: {inputs.illustration_style}
- Number of Pages: {inputs.page_count}

{age_guidelines}

**Your Task:**
Create a complete story plan including:

1. **Title**: Create a catchy, engaging book title (3-8 words) that:
   - Captures the essence of the story
   - Is age-appropriate and appealing to the target audience
   - Hints at the adventure or lesson without giving everything away
   - Uses alliteration or rhythm when possible for memorability

2. **Character Descriptions**: For each character mentioned, provide:
   - Name
   - Physical description (appearance, clothing, distinguishing features)
   - Personality traits
   - Role in the story (protagonist, sidekick, antagonist, etc.)

3. **Character Relations**: Describe how the characters interact and relate to each other (if multiple characters)

4. **Story Outline**: Write a complete narrative arc with:
   - Beginning: Setup and introduction
   - Middle: Conflict, adventure, or learning experience
   - End: Resolution with a positive moral or lesson

5. **Page Outlines**: Create exactly {inputs.page_count} page outlines. Each outline should:
   - Describe what happens on that page
   - Mention which characters appear
   - Note key actions or dialogue
   - Flow naturally from the previous page

6. **Illustration Style Guide**: Provide detailed guidance for consistent visuals:
   - Color palette suggestions
   - Artistic style details (e.g., "soft watercolors with gentle brushstrokes")
   - Mood and atmosphere
   - Consistency rules for character appearance

Remember: This story is for a {inputs.audience_age}-year-old, so keep language, themes, and situations age-appropriate and engaging."""

    return prompt


def _get_age_guidelines(age: int) -> str:
    """Get age-appropriate content guidelines."""
    if age <= 4:
        return """**Age Guidelines (Ages 3-4):**
- Very simple sentences (3-5 words)
- Focus on familiar concepts (colors, shapes, animals)
- Lots of repetition
- Clear, happy resolution
- No scary or tense situations
- Emphasis on fun sounds and rhythms"""

    elif age <= 6:
        return """**Age Guidelines (Ages 5-6):**
- Simple sentences (5-8 words)
- Clear cause and effect
- Introduction to simple emotions
- Basic problem-solving
- Very mild suspense (nothing scary)
- Positive messages about friendship, sharing, kindness"""

    elif age <= 8:
        return """**Age Guidelines (Ages 7-8):**
- Moderate sentence complexity (8-12 words)
- More developed characters with feelings
- Simple conflicts and resolutions
- Introduction to curiosity and discovery
- Mild adventure without real danger
- Lessons about courage, honesty, trying new things"""

    elif age <= 10:
        return """**Age Guidelines (Ages 9-10):**
- Fuller sentences with some complexity
- Character development and growth
- More substantial conflicts
- Light humor and wordplay
- Introduction to light fantasy elements
- Themes of independence, responsibility, problem-solving"""

    else:
        return """**Age Guidelines (Ages 11-12):**
- Complex sentences and varied vocabulary
- Deeper character emotions and motivations
- More nuanced conflicts
- Humor, wit, and subtle messages
- Fantasy and adventure elements
- Themes of identity, friendship challenges, perseverance"""
