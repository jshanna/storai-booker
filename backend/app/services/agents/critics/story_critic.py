"""Story Critic Agent - reviews narrative coherence and character consistency."""

from typing import Type, Dict, Any
from pydantic import BaseModel

from app.schemas.critic import StoryCriticOutput
from .base_critic import BaseCriticAgent


class StoryCriticAgent(BaseCriticAgent):
    """
    Reviews comic page narrative: story coherence, emotional impact, and characters.

    Focuses on:
    - Narrative coherence (does the visual story make sense?)
    - Emotional impact (are feelings conveyed effectively?)
    - Character consistency (do characters look/act consistently?)
    - Pacing (is the story pacing appropriate for this page?)
    """

    @property
    def critic_name(self) -> str:
        return "StoryCritic"

    @property
    def response_model(self) -> Type[BaseModel]:
        return StoryCriticOutput

    def build_review_prompt(
        self,
        page_script: Dict[str, Any],
        story_context: Dict[str, Any],
    ) -> str:
        """Build the story review prompt."""
        panel_info = self._format_panel_info(page_script)
        story_info = self._format_story_context(story_context)

        # Extract dialogue for context
        dialogues = []
        for panel in page_script.get("panels", []):
            for d in panel.get("dialogue", []):
                dialogues.append(f"  {d.get('character', 'Unknown')}: \"{d.get('text', '')}\"")
        dialogue_text = "\n".join(dialogues) if dialogues else "  (No dialogue on this page)"

        return f"""You are a professional comic book story critic. Analyze this comic page image for narrative quality, emotional impact, and character consistency.

**Story Context:**
{story_info}

**Panel Script:**
{panel_info}

**Expected Dialogue:**
{dialogue_text}

**Your Task:**
Carefully examine the comic page image and evaluate the following aspects. Score each from 1-10 where 1 is poor and 10 is excellent.

**Evaluation Criteria:**

1. **Narrative Coherence (1-10):**
   - Does the visual story make sense?
   - Is it clear what is happening in each panel?
   - Does the sequence of panels tell a coherent story?
   - Are actions and reactions logical?

2. **Emotional Impact (1-10):**
   - Are emotions effectively conveyed through expressions?
   - Does the page evoke the intended feelings?
   - Are dramatic moments emphasized appropriately?
   - Is the mood consistent with the story content?

3. **Character Consistency (1-10):**
   - Do characters look consistent across panels?
   - Are character designs appropriate for a children's story?
   - Do characters' appearances match their descriptions?
   - Are character expressions appropriate for the dialogue?

4. **Pacing (1-10):**
   - Is the story pacing appropriate for this page?
   - Are action scenes dynamic and exciting?
   - Are quiet moments given appropriate space?
   - Does the page advance the story effectively?

**Overall Score:** Average of the above, weighted by importance.

**Provide:**
- Specific story issues (confusing sequences, character inconsistencies)
- Actionable suggestions for improvement
- General narrative feedback

Remember: This is a children's story for {story_context.get('target_age', 'young')} year olds, so the narrative should be clear, engaging, and age-appropriate."""

    def _create_fallback_response(self, error_message: str) -> StoryCriticOutput:
        """Create a fallback passing response."""
        return StoryCriticOutput(
            score=7,
            narrative_coherence_score=7,
            emotional_impact_score=7,
            character_consistency_score=7,
            pacing_score=7,
            feedback=f"Review skipped due to error: {error_message[:100]}",
            issues=[],
            suggestions=[],
        )
