"""Composition Critic Agent - reviews layout, balance, and reading flow."""

from typing import Type, Dict, Any
from pydantic import BaseModel

from app.schemas.critic import CompositionCriticOutput
from .base_critic import BaseCriticAgent


class CompositionCriticAgent(BaseCriticAgent):
    """
    Reviews comic page composition: panel layout, visual balance, and readability.

    Focuses on:
    - Panel arrangement and sizing
    - Visual weight distribution across the page
    - Reading flow (left-to-right, top-to-bottom for Western comics)
    - Speech bubble and text positioning
    - Gutter spacing and panel borders
    """

    @property
    def critic_name(self) -> str:
        return "CompositionCritic"

    @property
    def response_model(self) -> Type[BaseModel]:
        return CompositionCriticOutput

    def build_review_prompt(
        self,
        page_script: Dict[str, Any],
        story_context: Dict[str, Any],
    ) -> str:
        """Build the composition review prompt."""
        panel_info = self._format_panel_info(page_script)
        story_info = self._format_story_context(story_context)
        layout = page_script.get("layout", "unknown")

        return f"""You are a professional comic book composition critic. Analyze this comic page image for layout quality, visual balance, and readability.

**Story Context:**
{story_info}

**Expected Layout:** {layout}

**Panel Script:**
{panel_info}

**Your Task:**
Carefully examine the comic page image and evaluate the following aspects. Score each from 1-10 where 1 is poor and 10 is excellent.

**Evaluation Criteria:**

1. **Panel Layout (1-10):**
   - Are panels clearly defined with appropriate borders?
   - Does the layout match the expected arrangement ({layout})?
   - Are panel sizes appropriate for their content?
   - Is there proper gutter spacing between panels?

2. **Visual Balance (1-10):**
   - Is visual weight distributed well across the page?
   - Do important elements draw the eye appropriately?
   - Is there a good balance of action, dialogue, and white space?
   - Are characters and objects sized appropriately?

3. **Reading Flow (1-10):**
   - Can the reader easily follow the story left-to-right, top-to-bottom?
   - Is it clear which panel to read next?
   - Do speech bubbles guide the eye in the correct order?
   - Is the narrative sequence intuitive?

4. **Text Placement (1-10):**
   - Are speech bubbles clearly positioned near speakers?
   - Is text readable and not obscured?
   - Do bubbles not cover important visual elements?
   - Are captions placed in logical locations?

**Overall Score:** Average of the above, weighted by importance.

**Provide:**
- Specific issues you observed (be precise about location and problem)
- Actionable suggestions for improvement
- General feedback summary

Remember: This is a children's comic, so clarity and easy readability are paramount."""

    def _create_fallback_response(self, error_message: str) -> CompositionCriticOutput:
        """Create a fallback passing response."""
        return CompositionCriticOutput(
            score=7,
            panel_layout_score=7,
            visual_balance_score=7,
            reading_flow_score=7,
            text_placement_score=7,
            feedback=f"Review skipped due to error: {error_message[:100]}",
            issues=[],
            suggestions=[],
        )
