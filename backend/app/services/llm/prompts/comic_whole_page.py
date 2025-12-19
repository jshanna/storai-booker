"""Prompt builder for whole-page comic generation."""

from typing import Optional, List, Dict, Any
from loguru import logger

from app.models.storybook import Page, GenerationInputs, StoryMetadata


def build_whole_page_image_prompt(
    page: Page,
    metadata: StoryMetadata,
    inputs: GenerationInputs,
    critic_feedback: Optional[str] = None,
) -> str:
    """
    Build a prompt for generating an entire comic page as a single image.

    This creates a detailed prompt that describes the complete page layout,
    including all panels, their content, dialogue bubbles, captions, and
    sound effects.

    Args:
        page: Page object with panels data
        metadata: Story metadata with character descriptions
        inputs: Generation inputs with style and age settings
        critic_feedback: Optional feedback from critics for regeneration

    Returns:
        Complete prompt for whole-page image generation
    """
    # Gather page information
    panel_count = len(page.panels) if page.panels else 1
    layout = page.layout or _infer_layout(panel_count)

    # Build character reference section
    character_section = _build_character_section(metadata)

    # Build layout description
    layout_section = _build_layout_description(layout, panel_count)

    # Build panel descriptions
    panels_section = _build_panels_section(page, inputs)

    # Build style instructions
    style_section = _build_style_section(inputs)

    # Build the complete prompt
    prompt_parts = [
        f"Create a complete comic book page with {panel_count} panels.",
        "",
        "**PAGE LAYOUT:**",
        layout_section,
        "",
        "**ART STYLE:**",
        style_section,
        "",
    ]

    if character_section:
        prompt_parts.extend([
            "**CHARACTERS:**",
            character_section,
            "",
        ])

    prompt_parts.extend([
        "**PANEL CONTENTS:**",
        panels_section,
        "",
        "**IMPORTANT INSTRUCTIONS:**",
        _build_instructions_section(inputs, panel_count),
    ])

    # Add critic feedback if provided (for regeneration)
    if critic_feedback:
        prompt_parts.extend([
            "",
            "**CRITICAL IMPROVEMENTS NEEDED (from previous attempt):**",
            critic_feedback,
            "",
            "Address the above issues in this version.",
        ])

    return "\n".join(prompt_parts)


def _infer_layout(panel_count: int) -> str:
    """Infer layout from panel count."""
    layouts = {
        1: "1x1 (full page)",
        2: "1x2 (stacked vertically)",
        3: "1-2 (one on top, two on bottom)",
        4: "2x2 (grid)",
        5: "2-3 (two on top, three on bottom)",
        6: "3x2 (grid)",
    }
    return layouts.get(panel_count, "2x2 (grid)")


def _build_character_section(metadata: StoryMetadata) -> str:
    """Build character descriptions section."""
    if not metadata.character_descriptions:
        return ""

    lines = []
    for char in metadata.character_descriptions:
        lines.append(f"- {char.name}: {char.physical_description}")

    return "\n".join(lines)


def _build_layout_description(layout: str, panel_count: int) -> str:
    """Build detailed layout description."""
    layout_lower = layout.lower().replace(" ", "")

    descriptions = {
        "1x1": "Single full-page panel filling the entire page.",
        "1x2": f"Two panels stacked vertically, each taking half the page height.",
        "2x1": f"Two panels side by side, each taking half the page width.",
        "2x2": "Four panels in a 2x2 grid, each taking a quarter of the page.",
        "1-2": "One large panel on top (full width), two smaller panels on bottom (side by side).",
        "2-1": "Two smaller panels on top (side by side), one large panel on bottom (full width).",
        "3x2": "Six panels in a 3-column, 2-row grid.",
        "2-3": "Two panels on top row, three panels on bottom row.",
        "3x3": "Nine panels in a 3x3 grid.",
    }

    base_desc = descriptions.get(layout_lower, f"Arrange {panel_count} panels in a {layout} layout.")

    return f"""Layout: {layout}
{base_desc}

Each panel should have:
- Clear black borders/gutters separating panels
- Consistent gutter width between all panels
- Panels should fill the page with appropriate margins"""


def _build_panels_section(page: Page, inputs: GenerationInputs) -> str:
    """Build detailed panel descriptions."""
    if not page.panels:
        return "No panel data available."

    lines = []

    for panel in page.panels:
        panel_num = panel.panel_number
        lines.append(f"**Panel {panel_num}:**")

        # Panel illustration
        if panel.illustration_prompt:
            lines.append(f"  Scene: {panel.illustration_prompt}")

        # Dialogue
        if panel.dialogue:
            lines.append("  Dialogue:")
            for d in panel.dialogue:
                bubble_style = _get_bubble_style(d.style)
                position = d.position or "appropriate position"
                lines.append(
                    f"    - {d.character} ({bubble_style} at {position}): \"{d.text}\""
                )

        # Caption
        if panel.caption:
            lines.append(f"  Caption box: \"{panel.caption}\"")

        # Sound effects
        if panel.sound_effects:
            for sfx in panel.sound_effects:
                style_desc = _get_sfx_style(sfx.style)
                lines.append(
                    f"  Sound effect at {sfx.position}: \"{sfx.text}\" ({style_desc})"
                )

        lines.append("")  # Blank line between panels

    return "\n".join(lines)


def _get_bubble_style(style: str) -> str:
    """Get speech bubble style description."""
    styles = {
        "speech": "regular speech bubble",
        "thought": "cloud-shaped thought bubble",
        "shout": "jagged/spiky speech bubble",
        "whisper": "dashed-line speech bubble",
    }
    return styles.get(style, "speech bubble")


def _get_sfx_style(style: str) -> str:
    """Get sound effect style description."""
    styles = {
        "impact": "bold, explosive lettering",
        "whoosh": "stretched, motion-blur lettering",
        "ambient": "subtle, smaller lettering",
        "dramatic": "large, dramatic lettering",
    }
    return styles.get(style, "bold lettering")


def _build_style_section(inputs: GenerationInputs) -> str:
    """Build art style instructions based on target audience age."""
    style = inputs.illustration_style or "colorful illustration"
    age = inputs.audience_age or 8

    if age <= 6:
        return f"""{style}

Target audience: young children (ages 3-6)
- Use soft, gentle colors with pastel tones
- Characters should be cute, friendly, and non-threatening
- No scary, violent, or intense content whatsoever
- Very simple, clear compositions
- Warm, nurturing atmosphere
- Round, soft shapes preferred"""

    elif age <= 12:
        return f"""{style}

Target audience: children (ages 7-12)
- Use bright, cheerful colors
- Characters should be friendly and approachable
- No scary, violent, or inappropriate content
- Simple, clear compositions that are easy to follow
- Age-appropriate expressions and body language"""

    elif age <= 17:
        return f"""{style}

Target audience: teenagers (ages 13-17)
- Use dynamic, bold colors and compositions
- Characters can show a wider range of emotions
- Action scenes can be more intense but not graphic
- More sophisticated visual storytelling allowed
- Stylish, engaging artwork that appeals to teens"""

    else:
        return f"""{style}

Target audience: adults
- Professional, high-quality artwork
- Full range of emotional expression allowed
- Dynamic compositions and sophisticated visual storytelling
- Artistic freedom in style and mood
- Focus on visual impact and narrative depth"""


def _build_instructions_section(inputs: GenerationInputs, panel_count: int) -> str:
    """Build technical instructions for image generation."""
    age = inputs.audience_age or 8

    # Base technical instructions
    base_instructions = f"""1. LAYOUT: Create exactly {panel_count} distinct panels with clear black borders
2. TEXT: All dialogue and text must be clearly readable and properly sized
3. BUBBLES: Speech bubbles should be white with black outlines, properly positioned near speakers
4. READING ORDER: Ensure panels flow left-to-right, top-to-bottom
5. CHARACTERS: Draw characters consistently across all panels
6. STYLE: Maintain consistent art style throughout the page
7. QUALITY: High-quality, clean artwork suitable for print"""

    # Age-appropriate content guidelines
    if age <= 12:
        content_guideline = f"8. CONTENT: Appropriate for {age}-year-old children - nothing scary or inappropriate"
        do_not_section = """
DO NOT:
- Leave any panels empty or incomplete
- Create garbled or unreadable text
- Include any scary, violent, or inappropriate imagery
- Create distorted anatomy (extra fingers, weird proportions)
- Let speech bubbles obscure important visual elements"""
    elif age <= 17:
        content_guideline = "8. CONTENT: Appropriate for teenagers - no explicit or graphic content"
        do_not_section = """
DO NOT:
- Leave any panels empty or incomplete
- Create garbled or unreadable text
- Include explicit, graphic, or overly violent imagery
- Create distorted anatomy (extra fingers, weird proportions)
- Let speech bubbles obscure important visual elements"""
    else:
        content_guideline = "8. CONTENT: Professional quality for adult audience"
        do_not_section = """
DO NOT:
- Leave any panels empty or incomplete
- Create garbled or unreadable text
- Create distorted anatomy (extra fingers, weird proportions)
- Let speech bubbles obscure important visual elements"""

    return f"{base_instructions}\n{content_guideline}\n{do_not_section}"


def extract_page_script(page: Page) -> Dict[str, Any]:
    """
    Extract page script data for critic review.

    Args:
        page: Page object

    Returns:
        Dictionary with page script information
    """
    panels_data = []
    for panel in page.panels or []:
        panel_data = {
            "panel_number": panel.panel_number,
            "illustration_prompt": panel.illustration_prompt,
            "dialogue": [
                {
                    "character": d.character,
                    "text": d.text,
                    "position": d.position,
                    "style": d.style,
                }
                for d in (panel.dialogue or [])
            ],
            "caption": panel.caption,
            "sound_effects": [
                {
                    "text": s.text,
                    "position": s.position,
                    "style": s.style,
                }
                for s in (panel.sound_effects or [])
            ],
        }
        panels_data.append(panel_data)

    return {
        "page_number": page.page_number,
        "layout": page.layout,
        "panels": panels_data,
    }
