"""Prompt templates for page generation (page agents)."""
from typing import Optional
from pydantic import BaseModel, Field

from app.models.storybook import GenerationInputs, StoryMetadata


class PageGenerationOutput(BaseModel):
    """Structured output for page generation."""

    page_text: str = Field(
        description="The narrative text for this page"
    )
    illustration_prompt: str = Field(
        description="Detailed prompt for generating the page illustration"
    )


def build_page_generation_prompt(
    page_number: int,
    page_outline: str,
    metadata: StoryMetadata,
    inputs: GenerationInputs,
) -> str:
    """
    Build prompt for generating a specific page.

    Args:
        page_number: Which page to generate (1-indexed)
        page_outline: Outline for this specific page from story planning
        metadata: Complete story metadata from coordinating agent
        inputs: Original user inputs

    Returns:
        Formatted prompt for page generation
    """
    # Build character descriptions section
    character_info = _format_character_info(metadata.character_descriptions)

    # Get previous context if not first page
    previous_context = ""
    if page_number > 1 and metadata.page_outlines:
        prev_outline = metadata.page_outlines[page_number - 2]
        previous_context = f"\n**Previous Page Context:**\nPage {page_number - 1}: {prev_outline}\n"

    # Determine format type based on age
    if inputs.audience_age <= 12:
        format_type = "children's storybook"
        text_guidance = "2-4 sentences for young children, longer for older"
    elif inputs.audience_age <= 17:
        format_type = "young adult illustrated story"
        text_guidance = "appropriate length for the scene - can be longer and more detailed"
    else:
        format_type = "illustrated story"
        text_guidance = "appropriate length for the scene - full creative freedom"

    # Build the prompt
    prompt = f"""You are writing page {page_number} of {inputs.page_count} for a {format_type}.

**Story Context:**
- Overall Story: {metadata.story_outline}
- Illustration Style: {metadata.illustration_style_guide}
- Target Age: {inputs.audience_age} years old

{character_info}
{previous_context}
**This Page (Page {page_number}):**
{page_outline}

**Your Task:**
Generate the content for this page including:

1. **Page Text**: Write the narrative text that appears on this page.
   - Match the reading level for a {inputs.audience_age}-year-old
   - Use vocabulary appropriate for the age
   - Keep the text length suitable for one page ({text_guidance})
   - Maintain character consistency with the descriptions provided
   - Flow naturally from the previous page

2. **Illustration Prompt**: Write a detailed prompt for generating this page's illustration.
   - Reference specific characters by name and description
   - Describe the scene, setting, and mood
   - Mention the {inputs.illustration_style} style
   - Include details that match the illustration style guide
   - Be specific about character positions, actions, and expressions
   - Ensure consistency with previous pages

Remember:
- This is page {page_number} of {inputs.page_count}, so pace the story appropriately
- Stay true to the character descriptions and story outline
- The illustration should complement and enhance the text
- Keep everything appropriate for the {inputs.audience_age}-year-old target audience"""

    return prompt


def _format_character_info(character_descriptions) -> str:
    """Format character descriptions for the prompt."""
    if not character_descriptions:
        return ""

    lines = ["**Characters:**"]
    for char in character_descriptions:
        lines.append(
            f"- {char.name}: {char.physical_description}. "
            f"Personality: {char.personality}. Role: {char.role}"
        )

    return "\n".join(lines)
