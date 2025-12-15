"""Prompt templates for story validation (validator agent)."""
from typing import List
from pydantic import BaseModel, Field

from app.models.storybook import Storybook


class ValidationIssue(BaseModel):
    """A single validation issue found in the story."""

    page_number: int = Field(description="Page number where issue was found")
    issue_type: str = Field(description="Type of issue (e.g., 'character_inconsistency', 'age_inappropriate')")
    description: str = Field(description="Detailed description of the issue")
    severity: str = Field(description="Severity level: 'minor', 'moderate', 'critical'")


class ValidationOutput(BaseModel):
    """Structured output for story validation."""

    is_valid: bool = Field(description="Whether the story passes validation")
    overall_quality: str = Field(description="Overall quality assessment")
    issues: List[ValidationIssue] = Field(description="List of issues found")
    suggestions: List[str] = Field(description="Suggestions for improvement")


def build_validation_prompt(storybook: Storybook) -> str:
    """
    Build prompt for validating a complete story.

    Args:
        storybook: Complete storybook to validate

    Returns:
        Formatted prompt for validation
    """
    # Build pages summary
    pages_text = _format_pages_for_validation(storybook)

    # Build character descriptions
    character_info = _format_character_descriptions(storybook.metadata.character_descriptions)

    prompt = f"""You are a children's story editor reviewing a completed storybook for quality and consistency.

**Story Information:**
- Title: {storybook.title}
- Target Age: {storybook.generation_inputs.audience_age} years old
- Topic: {storybook.generation_inputs.topic}
- Number of Pages: {len(storybook.pages)}

**Story Outline:**
{storybook.metadata.story_outline}

{character_info}

**Complete Story Pages:**
{pages_text}

**Your Task:**
Validate this story for:

1. **Character Consistency**:
   - Do characters maintain consistent physical descriptions across pages?
   - Are personality traits consistent?
   - Are character names used correctly?

2. **Narrative Flow**:
   - Does the story flow logically from page to page?
   - Is there a clear beginning, middle, and end?
   - Are there any plot holes or confusing transitions?

3. **Age Appropriateness**:
   - Is the language suitable for {storybook.generation_inputs.audience_age}-year-olds?
   - Are the themes and content appropriate?
   - Is the vocabulary at the right level?
   - Is the story length appropriate?

4. **Story Coherence**:
   - Does the story make sense as a whole?
   - Are all plot points resolved?
   - Is there a clear moral or lesson (if appropriate)?

5. **Illustration Prompts**:
   - Are illustration prompts detailed enough?
   - Do they maintain visual consistency?
   - Do they match the specified style ({storybook.generation_inputs.illustration_style})?

For each issue found, specify:
- Page number
- Type of issue
- Detailed description
- Severity (minor/moderate/critical)

Critical issues require regeneration. Minor issues can be accepted.

Provide an overall quality assessment and suggestions for improvement."""

    return prompt


def _format_pages_for_validation(storybook: Storybook) -> str:
    """Format pages for validation prompt."""
    lines = []
    for page in storybook.pages:
        lines.append(f"**Page {page.page_number}:**")
        lines.append(f"Text: {page.text}")
        lines.append(f"Illustration: {page.illustration_prompt[:100]}...")
        lines.append("")
    return "\n".join(lines)


def _format_character_descriptions(character_descriptions) -> str:
    """Format character descriptions for validation."""
    if not character_descriptions:
        return ""

    lines = ["**Character Descriptions:**"]
    for char in character_descriptions:
        lines.append(
            f"- {char.name}: {char.physical_description}. "
            f"{char.personality}"
        )
    return "\n".join(lines)
