"""Validator agent for story quality and coherence checking."""
from loguru import logger

from app.models.storybook import Storybook
from app.services.llm.base import BaseLLMProvider
from app.services.llm.prompts.validation import (
    build_validation_prompt,
    ValidationOutput,
    ValidationIssue,
)


class ValidatorAgent:
    """
    Validator agent responsible for quality assurance.

    This agent validates a complete story for:
    - Character consistency
    - Narrative flow
    - Age-appropriateness
    - Story coherence
    - Illustration prompt quality
    """

    def __init__(self, llm_provider: BaseLLMProvider):
        """
        Initialize validator agent.

        Args:
            llm_provider: LLM provider instance for validation
        """
        self.llm = llm_provider
        logger.info(f"Initialized ValidatorAgent with {self.llm}")

    async def validate_story(self, storybook: Storybook) -> ValidationOutput:
        """
        Validate a complete storybook for quality and coherence.

        Args:
            storybook: Complete storybook with all pages generated

        Returns:
            ValidationOutput with validation results and issues

        Raises:
            Exception: If validation fails
        """
        try:
            logger.info(
                f"Validating story '{storybook.title}' "
                f"({len(storybook.pages)} pages)"
            )

            # Build the validation prompt
            prompt = build_validation_prompt(storybook)

            # Generate structured validation output
            validation_output: ValidationOutput = await self.llm.generate_structured(
                prompt=prompt,
                response_model=ValidationOutput,
            )

            # Log results
            if validation_output.is_valid:
                logger.info(
                    f"Story '{storybook.title}' passed validation. "
                    f"Quality: {validation_output.overall_quality}"
                )
            else:
                logger.warning(
                    f"Story '{storybook.title}' failed validation. "
                    f"Found {len(validation_output.issues)} issues."
                )
                # Log critical issues
                critical_issues = [
                    issue for issue in validation_output.issues
                    if issue.severity == "critical"
                ]
                if critical_issues:
                    logger.warning(
                        f"Critical issues found on pages: "
                        f"{[issue.page_number for issue in critical_issues]}"
                    )

            return validation_output

        except Exception as e:
            logger.error(f"Story validation failed: {e}")
            raise

    async def validate_page(
        self,
        storybook: Storybook,
        page_number: int,
    ) -> tuple[bool, list[str]]:
        """
        Validate a single page within the story context.

        Args:
            storybook: Complete storybook for context
            page_number: Page number to validate

        Returns:
            Tuple of (is_valid, issues_list)

        Raises:
            Exception: If validation fails
        """
        try:
            logger.info(f"Validating page {page_number} of '{storybook.title}'")

            # Get the page
            page = next(
                (p for p in storybook.pages if p.page_number == page_number),
                None
            )
            if not page:
                raise ValueError(f"Page {page_number} not found in story")

            # Build focused validation prompt
            prompt = self._build_page_validation_prompt(storybook, page)

            # Generate structured validation
            validation_output: ValidationOutput = await self.llm.generate_structured(
                prompt=prompt,
                response_model=ValidationOutput,
            )

            # Extract issues for this specific page
            page_issues = [
                issue.description
                for issue in validation_output.issues
                if issue.page_number == page_number
            ]

            is_valid = len(page_issues) == 0

            logger.info(
                f"Page {page_number} validation: "
                f"{'passed' if is_valid else f'failed with {len(page_issues)} issues'}"
            )

            return is_valid, page_issues

        except Exception as e:
            logger.error(f"Page {page_number} validation failed: {e}")
            raise

    def _build_page_validation_prompt(self, storybook: Storybook, page) -> str:
        """
        Build validation prompt for a single page.

        Args:
            storybook: Complete storybook for context
            page: Page to validate

        Returns:
            Formatted prompt for page validation
        """
        is_comic = storybook.generation_inputs.format == "comic"

        # Get character descriptions
        character_info = ""
        if storybook.metadata.character_descriptions:
            chars = [
                f"- {char.name}: {char.physical_description}"
                for char in storybook.metadata.character_descriptions
            ]
            character_info = f"\n**Characters:**\n" + "\n".join(chars)

        # Get previous and next page context
        prev_page = None
        next_page = None
        for p in storybook.pages:
            if p.page_number == page.page_number - 1:
                prev_page = p
            if p.page_number == page.page_number + 1:
                next_page = p

        context = ""
        if prev_page:
            prev_content = self._format_page_content(prev_page, is_comic)
            context += f"\n**Previous Page:**\n{prev_content}\n"
        if next_page:
            next_content = self._format_page_content(next_page, is_comic)
            context += f"\n**Next Page:**\n{next_content}\n"

        # Format current page content
        page_content = self._format_page_content(page, is_comic)

        prompt = f"""You are validating page {page.page_number} of a children's {"comic book" if is_comic else "storybook"}.

**Story Information:**
- Title: {storybook.title}
- Target Age: {storybook.generation_inputs.audience_age} years old
- Overall Story: {storybook.metadata.story_outline}
{character_info}
{context}

**Page {page.page_number} Content:**
{page_content}

**Validation Criteria:**
1. Character consistency with descriptions
2. Narrative flow with surrounding pages
3. Age-appropriate language and themes
4. {"Panel composition and dialogue quality" if is_comic else "Illustration prompt quality and consistency"}
5. {"Dialogue length appropriate for comics" if is_comic else "Text length appropriate for page and age"}

Identify any issues with this page. For each issue:
- Specify page number: {page.page_number}
- Issue type (character_inconsistency, narrative_flow, age_inappropriate, etc.)
- Description of the problem
- Severity (minor/moderate/critical)

If no issues, mark as valid."""

        return prompt

    def _format_page_content(self, page, is_comic: bool) -> str:
        """Format page content for validation prompt."""
        if is_comic and page.panels:
            lines = []
            for panel in page.panels:
                lines.append(f"Panel {panel.panel_number}:")
                if panel.illustration_prompt:
                    lines.append(f"  Scene: {panel.illustration_prompt[:80]}...")
                if panel.dialogue:
                    for d in panel.dialogue:
                        lines.append(f"  {d.character}: \"{d.text}\"")
                if panel.caption:
                    lines.append(f"  [Caption: {panel.caption}]")
            return "\n".join(lines)
        else:
            text = page.text or "(no text)"
            illustration = page.illustration_prompt or "(no illustration prompt)"
            return f"Text: {text}\nIllustration Prompt: {illustration}"

    def get_pages_needing_regeneration(
        self,
        validation_output: ValidationOutput,
    ) -> list[tuple[int, str]]:
        """
        Extract page numbers that need regeneration from validation output.

        Args:
            validation_output: Validation results

        Returns:
            List of (page_number, issue_description) tuples for pages
            that have critical or moderate issues requiring regeneration
        """
        pages_to_regenerate = {}

        for issue in validation_output.issues:
            # Only regenerate moderate or critical issues
            if issue.severity in ["moderate", "critical"]:
                page_num = issue.page_number
                if page_num not in pages_to_regenerate:
                    pages_to_regenerate[page_num] = []
                pages_to_regenerate[page_num].append(
                    f"[{issue.severity.upper()}] {issue.issue_type}: {issue.description}"
                )

        # Convert to list of tuples
        result = [
            (page_num, "\n".join(issues))
            for page_num, issues in pages_to_regenerate.items()
        ]

        logger.info(
            f"Identified {len(result)} pages needing regeneration: "
            f"{[p[0] for p in result]}"
        )

        return result
