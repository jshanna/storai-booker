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

    # Get age-specific content restrictions
    age_restrictions = _get_age_content_restrictions(storybook.generation_inputs.audience_age)

    # Determine editor role based on age
    age = storybook.generation_inputs.audience_age
    if age <= 12:
        editor_role = "children's story editor"
    elif age <= 17:
        editor_role = "young adult fiction editor"
    else:
        editor_role = "fiction editor"

    prompt = f"""You are a {editor_role} reviewing a completed storybook for quality and consistency.

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

3. **Age Appropriateness** (CRITICAL - Must be strictly enforced):
   - Is the language suitable for {storybook.generation_inputs.audience_age}-year-olds?
   - Are the themes and content appropriate?
   - Is the vocabulary at the right level?
   - Is the story length appropriate?

   **Age-Specific Content Restrictions for {storybook.generation_inputs.audience_age}-year-olds:**
{age_restrictions}

   **IMPORTANT**: Flag ANY content that violates these age restrictions as a CRITICAL issue requiring regeneration.

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
    is_comic = storybook.generation_inputs.format == "comic"
    lines = []

    for page in storybook.pages:
        lines.append(f"**Page {page.page_number}:**")

        if is_comic and page.panels:
            # Comic format: show panel content
            for panel in page.panels:
                lines.append(f"  Panel {panel.panel_number}:")
                if panel.illustration_prompt:
                    lines.append(f"    Scene: {panel.illustration_prompt[:80]}...")
                if panel.dialogue:
                    for d in panel.dialogue:
                        lines.append(f"    {d.character}: \"{d.text}\"")
                if panel.caption:
                    lines.append(f"    [Caption: {panel.caption}]")
        else:
            # Storybook format: show text and illustration
            lines.append(f"Text: {page.text or '(no text)'}")
            if page.illustration_prompt:
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


def _get_age_content_restrictions(age: int) -> str:
    """
    Get age-specific content restrictions for validation.

    Args:
        age: Target audience age

    Returns:
        Formatted string of content restrictions
    """
    if age <= 4:
        return """   - NO scary, sad, or tense situations whatsoever
   - NO mention of death, injury, or danger
   - NO conflict beyond simple misunderstandings
   - NO complex emotions (fear, anger, sadness)
   - ONLY positive, happy, safe scenarios
   - Simple, repetitive language only"""

    elif age <= 6:
        return """   - NO scary content or real danger
   - NO violence or aggressive behavior
   - NO sad endings or unresolved sadness
   - NO complex fears or anxieties
   - Very mild conflicts only (lost toy, sharing problems)
   - Simple problem-solving with happy resolutions
   - Gentle emotions only (happy, excited, a little worried)"""

    elif age <= 8:
        return """   - NO frightening or threatening situations
   - NO violence or fighting (even fantasy)
   - NO death or serious injury
   - NO scary creatures or villains
   - Mild conflicts only (disagreements, small challenges)
   - Age-appropriate emotions (curiosity, mild concern, happiness)
   - Positive, encouraging messages only"""

    elif age <= 10:
        return """   - NO graphic violence or detailed descriptions of harm
   - NO scary horror elements (ghosts, monsters as threats)
   - NO death of main characters
   - NO intense emotional trauma
   - Light adventure and mild suspense acceptable
   - Conflicts should be age-appropriate (bullying, competition)
   - Themes of courage, friendship, responsibility"""

    elif age <= 12:
        return """   - NO explicit violence or gore
   - NO horror or intense scary content
   - NO graphic descriptions of death or injury
   - NO mature romantic content
   - Fantasy violence (action scenes) acceptable if not graphic
   - Emotional depth acceptable (sadness, fear, conflict)
   - Themes of identity, independence, friendship challenges"""

    elif age <= 14:
        return """   - NO graphic violence or explicit gore
   - NO sexual content or mature romance
   - NO glorification of dangerous behaviors
   - NO explicit drug/alcohol references
   - Can explore difficult emotions (grief, anxiety, anger)
   - Can address social issues (peer pressure, identity)
   - Action and fantasy violence acceptable if story-appropriate
   - Moral complexity acceptable"""

    elif age <= 16:
        return """   - NO explicit sexual content
   - NO graphic violence for shock value
   - NO promotion of self-harm or dangerous behaviors
   - Can include mature themes (relationships, loss, identity)
   - Can explore difficult topics with sensitivity (mental health, discrimination)
   - Realistic portrayal of teen challenges acceptable
   - Complex moral questions acceptable
   - Keep violence/romance age-appropriate"""

    elif age <= 17:
        return """   - NO pornographic or explicit sexual content
   - NO gratuitous graphic violence
   - NO promotion of illegal activities or self-harm
   - Mature themes acceptable if handled thoughtfully
   - Can explore complex social/political issues
   - Realistic portrayal of young adult experiences
   - Romance acceptable if respectful and appropriate
   - Violence acceptable if story-relevant, not glorified
   - Note: Still young adult content, not adult content"""

    else:  # 18+ Adult
        return """   - Adult content guidelines
   - Full creative freedom for mature storytelling
   - Complex themes and moral ambiguity allowed
   - Romance and relationships handled with maturity
   - Violence acceptable when serving the narrative
   - Focus on quality storytelling and artistic merit
   - No gratuitous content without narrative purpose"""
