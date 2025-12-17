"""Content safety service for age-appropriate topic validation."""
from typing import Optional, Tuple
from pydantic import BaseModel, Field
from loguru import logger

from app.models.storybook import GenerationInputs
from app.services.llm.base import BaseLLMProvider


class TopicAppropriatenessOutput(BaseModel):
    """Output from topic appropriateness check."""

    is_appropriate: bool = Field(
        description="Whether the topic is appropriate for the target age"
    )
    reason: str = Field(
        description="Explanation of why the topic is or isn't appropriate"
    )
    severity: str = Field(
        description="Severity if inappropriate: 'minor', 'moderate', 'severe'"
    )
    suggested_modification: Optional[str] = Field(
        None,
        description="Suggested way to modify the topic to make it appropriate"
    )


def _get_topic_safety_prompt(inputs: GenerationInputs) -> str:
    """
    Build prompt for topic safety validation.

    Args:
        inputs: User generation inputs

    Returns:
        Prompt string for safety check
    """
    # Age-specific restrictions
    restrictions = _get_age_topic_restrictions(inputs.audience_age)

    prompt = f"""You are a content safety reviewer for children's stories. Your job is to determine if a story topic is appropriate for a specific age group.

**Story Request:**
- Target Age: {inputs.audience_age} years old
- Topic: "{inputs.topic}"
- Setting: "{inputs.setting}"
- Characters: {', '.join(inputs.characters) if inputs.characters else 'Not specified'}

**Age-Specific Content Restrictions for {inputs.audience_age}-year-olds:**
{restrictions}

**Your Task:**
Determine if this topic is appropriate for a {inputs.audience_age}-year-old audience.

Consider:
1. **Topic Content**: Does the topic involve themes that are too mature, scary, or complex?
2. **Setting Safety**: Does the setting suggest dangerous or inappropriate scenarios?
3. **Character Concerns**: Do the characters or their descriptions raise any red flags?
4. **Overall Appropriateness**: Would a responsible parent/educator approve this for their {inputs.audience_age}-year-old?

**IMPORTANT**:
- Be strict for younger ages (3-6): Reject anything remotely scary, sad, or complex
- Be moderate for middle ages (7-12): Allow adventure and mild conflict, reject violence/mature themes
- Be balanced for older ages (13-18): Allow mature themes if handled appropriately, reject explicit content

If the topic is inappropriate, explain why and suggest a modification that would make it appropriate while keeping the spirit of the request.

If the topic is appropriate, explain why it's suitable for this age group."""

    return prompt


def _get_age_topic_restrictions(age: int) -> str:
    """Get age-specific topic restrictions."""
    if age <= 4:
        return """- Topics MUST be positive, safe, and simple
- NO topics involving: danger, loss, fear, sadness, conflict
- YES to: animals, colors, shapes, friendship, family, everyday activities
- Examples of INAPPROPRIATE topics: "lost in the woods", "scary monster", "missing parent"
- Examples of APPROPRIATE topics: "friendly animal adventure", "colorful day at the park", "making new friends\""""

    elif age <= 6:
        return """- Topics should be gentle, positive, with simple problems
- NO topics involving: real danger, violence, death, abandonment, intense fear
- Mild challenges OK: lost toy, making friends, trying new things
- YES to: exploration, discovery, problem-solving, emotions (happy, excited, little worried)
- Examples of INAPPROPRIATE: "dangerous journey", "scary forest", "abandoned child"
- Examples of APPROPRIATE: "treasure hunt in backyard", "first day of school", "helping a friend\""""

    elif age <= 8:
        return """- Topics can include mild adventure and challenges
- NO topics involving: violence, fighting, death, serious danger, scary monsters as threats
- Mild conflicts OK: disagreements, overcoming fears, learning lessons
- YES to: adventures, discovery, curiosity, teamwork, courage
- Examples of INAPPROPRIATE: "battling evil wizard", "surviving alone", "ghost story"
- Examples of APPROPRIATE: "exploring magical garden", "solving a mystery", "brave squirrel adventure\""""

    elif age <= 10:
        return """- Topics can include adventure, light fantasy, mild suspense
- NO topics involving: graphic violence, death of main characters, intense horror, mature romance
- Challenges and conflicts OK: bullying, competition, overcoming obstacles
- YES to: fantasy adventures, mysteries, friendship challenges, responsibility
- Examples of INAPPROPRIATE: "fighting zombies", "romantic drama", "surviving apocalypse"
- Examples of APPROPRIATE: "fantasy quest", "detective mystery", "sports competition", "magical school\""""

    elif age <= 12:
        return """- Topics can include fantasy, adventure, emotional depth
- NO topics involving: explicit violence, horror, mature sexual content, graphic death
- Complex themes OK: identity, belonging, loss (handled sensitively), conflict
- YES to: action-adventure, fantasy quests, coming-of-age, friendship drama
- Examples of INAPPROPRIATE: "violent war", "graphic survival horror", "explicit romance"
- Examples of APPROPRIATE: "fantasy battle", "dealing with grief", "finding identity", "dystopian adventure\""""

    elif age <= 14:
        return """- Topics can include complex themes and moral questions
- NO topics involving: explicit sexual content, graphic violence, promotion of harmful behaviors
- Mature themes OK if handled appropriately: relationships, social issues, difficult emotions
- YES to: identity exploration, social commentary, complex relationships, ethical dilemmas
- Examples of INAPPROPRIATE: "explicit teen romance", "glorifying violence", "promoting drug use"
- Examples of APPROPRIATE: "navigating first relationship", "dealing with discrimination", "moral dilemma\""""

    elif age <= 16:
        return """- Topics can include mature themes and complex issues
- NO topics involving: pornographic content, gratuitous violence, promotion of illegal/harmful activities
- Complex/difficult themes OK: mental health, sexuality (age-appropriate), loss, identity
- YES to: realistic teen experiences, social issues, complex relationships, difficult choices
- Examples of INAPPROPRIATE: "explicit sexual encounters", "graphic violence", "celebrating drug culture"
- Examples of APPROPRIATE: "exploring sexuality", "coping with loss", "social activism", "complex family dynamics\""""

    else:  # 17-18
        return """- Topics can include sophisticated and mature themes
- NO topics involving: pornography, glorification of violence, promotion of self-harm/illegal activities
- Mature content OK if story-relevant: relationships, complex social/political issues, difficult realities
- YES to: young adult realism, philosophical questions, mature relationships, adult challenges
- Examples of INAPPROPRIATE: "pornographic content", "promoting illegal activities", "explicit violence for shock"
- Examples of APPROPRIATE: "coming of age in difficult circumstances", "exploring purpose", "realistic romance\""""


class ContentSafetyService:
    """Service for validating content safety and age-appropriateness."""

    def __init__(self, llm_provider: BaseLLMProvider):
        """
        Initialize content safety service.

        Args:
            llm_provider: LLM provider for safety checks
        """
        self.llm_provider = llm_provider

    async def check_topic_appropriateness(
        self,
        inputs: GenerationInputs
    ) -> Tuple[bool, str]:
        """
        Check if a topic is appropriate for the target age.

        Args:
            inputs: Story generation inputs

        Returns:
            Tuple of (is_appropriate, reason_or_error_message)
        """
        try:
            prompt = _get_topic_safety_prompt(inputs)

            # Use the LLM to evaluate appropriateness
            result = await self.llm_provider.generate_structured(
                prompt=prompt,
                output_schema=TopicAppropriatenessOutput,
                temperature=0.3,  # Lower temperature for more consistent safety checks
            )

            if not result.is_appropriate:
                logger.warning(
                    f"Topic rejected for age {inputs.audience_age}: {inputs.topic}. "
                    f"Reason: {result.reason}"
                )

                error_message = f"This topic is not appropriate for a {inputs.audience_age}-year-old audience. "
                error_message += result.reason

                if result.suggested_modification:
                    error_message += f"\n\nSuggested modification: {result.suggested_modification}"

                return False, error_message

            logger.info(
                f"Topic approved for age {inputs.audience_age}: {inputs.topic}"
            )
            return True, result.reason

        except Exception as e:
            logger.error(f"Error in topic appropriateness check: {e}")
            # On error, default to allowing (don't block generation on safety check failure)
            # The validator agent will still catch issues later
            return True, f"Safety check unavailable (allowing by default): {str(e)}"
