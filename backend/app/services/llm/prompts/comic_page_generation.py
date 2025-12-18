"""Prompt templates for comic page generation."""
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.storybook import GenerationInputs, StoryMetadata


class DialogueOutput(BaseModel):
    """Structured output for a single dialogue bubble."""

    character: str = Field(description="Name of the character speaking")
    text: str = Field(description="What the character says")
    position: str = Field(
        description="Position in panel: top-left, top-center, top-right, middle-left, middle-right, bottom-left, bottom-center, bottom-right"
    )
    style: str = Field(
        description="Bubble style: speech (normal), thought (internal), shout (loud), whisper (quiet)"
    )


class SoundEffectOutput(BaseModel):
    """Structured output for a sound effect."""

    text: str = Field(description="Sound effect text (e.g., BOOM!, WHOOSH!, CRACK!)")
    position: str = Field(
        description="Position in panel: top-left, top-center, top-right, middle-left, middle-center, middle-right, bottom-left, bottom-center, bottom-right"
    )
    style: str = Field(description="Style: impact, whoosh, ambient, dramatic")


class PanelOutput(BaseModel):
    """Structured output for a single comic panel."""

    panel_number: int = Field(description="Panel number on the page (1-based)")
    illustration_prompt: str = Field(
        description="Detailed prompt for generating this panel's illustration"
    )
    dialogue: List[DialogueOutput] = Field(
        default_factory=list,
        description="Dialogue bubbles in this panel (can be empty for action panels)"
    )
    caption: Optional[str] = Field(
        default=None,
        description="Narrator text box (optional, for setting scenes or inner thoughts)"
    )
    sound_effects: List[SoundEffectOutput] = Field(
        default_factory=list,
        description="Sound effects in this panel"
    )


class ComicPageGenerationOutput(BaseModel):
    """Structured output for comic page generation."""

    panels: List[PanelOutput] = Field(description="All panels for this comic page")
    layout: str = Field(
        description="Panel layout description (e.g., '2x2' for 4 panels, '3x1' for 3 horizontal)"
    )


def get_layout_for_panel_count(panel_count: int) -> str:
    """Get the default layout description for a given panel count."""
    layouts = {
        1: "1x1",  # Single full panel
        2: "2x1",  # Two side-by-side panels
        3: "1-2",  # One on top, two on bottom
        4: "2x2",  # 2x2 grid
        5: "2-3",  # Two on top, three on bottom
        6: "3x2",  # 3x2 grid
        7: "2-3-2",  # 2-3-2 pattern
        8: "2-4-2",  # 2-4-2 pattern
        9: "3x3",  # 3x3 grid
    }
    return layouts.get(panel_count, "2x2")


def build_comic_page_generation_prompt(
    page_number: int,
    page_outline: str,
    metadata: StoryMetadata,
    inputs: GenerationInputs,
) -> str:
    """
    Build prompt for generating a comic page with panels.

    Args:
        page_number: Which page to generate (1-indexed)
        page_outline: Outline for this specific page from story planning
        metadata: Complete story metadata from coordinating agent
        inputs: Original user inputs

    Returns:
        Formatted prompt for comic page generation
    """
    panels_per_page = inputs.panels_per_page or 4
    layout = get_layout_for_panel_count(panels_per_page)

    # Build character descriptions section
    character_info = _format_character_info(metadata.character_descriptions)

    # Get previous context if not first page
    previous_context = ""
    if page_number > 1 and metadata.page_outlines:
        prev_outline = metadata.page_outlines[page_number - 2]
        previous_context = f"\n**Previous Page Context:**\nPage {page_number - 1}: {prev_outline}\n"

    prompt = f"""You are creating page {page_number} of {inputs.page_count} for a children's comic book.

**Comic Format:**
- This page has {panels_per_page} panels in a {layout} layout
- Each panel needs its own illustration prompt and can have dialogue/sound effects
- Comics tell stories through sequential art with speech bubbles and action

**Story Context:**
- Overall Story: {metadata.story_outline}
- Art Style: {metadata.illustration_style_guide}
- Target Age: {inputs.audience_age} years old

{character_info}
{previous_context}
**This Page (Page {page_number}):**
{page_outline}

**Your Task:**
Create {panels_per_page} panels that break down this page's story beat into sequential comic panels.

For EACH panel, provide:

1. **Illustration Prompt**: Describe the scene for this panel
   - Reference characters by name and appearance
   - Describe actions, expressions, and poses
   - Note the setting/background
   - Match the {inputs.illustration_style} art style
   - IMPORTANT: Leave clear space for speech bubbles (avoid cluttering areas where dialogue will appear)
   - Frame the action appropriately (close-up for emotions, wide for action)

2. **Dialogue** (if characters speak):
   - Keep dialogue short and punchy (comics use brief exchanges)
   - Specify which character is speaking
   - Position bubbles logically (reading left-to-right, top-to-bottom)
   - Choose bubble style (speech, thought, shout, whisper)
   - Maximum 2-3 dialogue bubbles per panel

3. **Caption** (optional narrator box):
   - Use for scene-setting ("Meanwhile...", "The next morning...")
   - Or for character's inner thoughts in narrative form
   - Keep very brief

4. **Sound Effects** (if applicable):
   - Use onomatopoeia (BOOM!, WHOOSH!, CRACK!, etc.)
   - Position in the action
   - Choose style (impact, whoosh, ambient, dramatic)

**Panel Flow Guidelines:**
- Panel 1: Establish the scene or continue from previous page
- Middle panels: Build action and tension
- Final panel: Cliffhanger or resolution for this page

**Age-Appropriate Content:**
- Vocabulary suitable for {inputs.audience_age}-year-olds
- Keep dialogue simple and clear
- Action should be exciting but not scary for young readers

Generate all {panels_per_page} panels with varied pacing - mix dialogue-heavy and action-focused panels."""

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
