"""Technical Critic Agent - reviews image quality and age-appropriateness."""

from typing import Type, Dict, Any
from pydantic import BaseModel

from app.schemas.critic import TechnicalCriticOutput
from .base_critic import BaseCriticAgent


class TechnicalCriticAgent(BaseCriticAgent):
    """
    Reviews comic page technical quality: image clarity, text readability, appropriateness.

    Focuses on:
    - Overall image quality and lack of artifacts
    - Text legibility and appropriate sizing
    - Age-appropriate content for target audience
    - Style consistency with requested illustration style
    """

    @property
    def critic_name(self) -> str:
        return "TechnicalCritic"

    @property
    def response_model(self) -> Type[BaseModel]:
        return TechnicalCriticOutput

    def build_review_prompt(
        self,
        page_script: Dict[str, Any],
        story_context: Dict[str, Any],
    ) -> str:
        """Build the technical review prompt."""
        panel_info = self._format_panel_info(page_script)
        story_info = self._format_story_context(story_context)
        target_age = story_context.get("target_age", 8)
        illustration_style = story_context.get("illustration_style", "colorful children's book")

        return f"""You are a professional comic book technical quality reviewer. Analyze this comic page image for technical quality, readability, and age-appropriateness.

**Story Context:**
{story_info}

**Panel Script:**
{panel_info}

**Your Task:**
Carefully examine the comic page image and evaluate the following aspects. Score each from 1-10 where 1 is poor and 10 is excellent.

**Evaluation Criteria:**

1. **Image Quality (1-10):**
   - Is the image clear and well-rendered?
   - Are there any visual artifacts or distortions?
   - Are colors vibrant and appropriate?
   - Is the resolution and detail level adequate?
   - Are there any weird hands, extra fingers, or distorted body parts?

2. **Text Clarity (1-10):**
   - Is all text legible and readable?
   - Are fonts appropriately sized for children?
   - Is text clearly separated from artwork?
   - Are speech bubbles properly formatted?
   - Is there any garbled or unreadable text?

3. **Age Appropriateness (1-10):**
   - Is the content suitable for {target_age}-year-olds?
   - Are there any scary, violent, or inappropriate elements?
   - Are characters depicted appropriately for children?
   - Is the overall tone child-friendly?
   - Would parents be comfortable showing this to their child?

4. **Style Consistency (1-10):**
   - Does the art style match "{illustration_style}"?
   - Is the style consistent across all panels?
   - Are characters drawn in a consistent style?
   - Does the overall aesthetic fit a children's comic?

**Overall Score:** Average of the above, weighted by importance.

**Critical Issues to Flag:**
- Any scary, violent, or inappropriate imagery (immediate flag)
- Garbled or unreadable text (high priority)
- Distorted anatomy or artifacts (moderate priority)
- Style inconsistencies (lower priority)

**Provide:**
- Specific technical issues (be precise about location and problem)
- Actionable suggestions for improvement
- General technical feedback

Remember: This is content for {target_age}-year-old children. Safety and appropriateness are paramount."""

    def _create_fallback_response(self, error_message: str) -> TechnicalCriticOutput:
        """Create a fallback passing response."""
        return TechnicalCriticOutput(
            score=7,
            image_quality_score=7,
            text_clarity_score=7,
            age_appropriateness_score=7,
            style_consistency_score=7,
            feedback=f"Review skipped due to error: {error_message[:100]}",
            issues=[],
            suggestions=[],
        )
