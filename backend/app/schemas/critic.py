"""Pydantic models for critic agent outputs."""

from typing import List, Optional
from pydantic import BaseModel, Field


class CompositionCriticOutput(BaseModel):
    """Output from the Composition Critic - reviews layout, balance, and flow."""

    score: int = Field(..., ge=1, le=10, description="Overall composition score (1-10)")
    panel_layout_score: int = Field(
        ..., ge=1, le=10, description="How well panels are arranged and sized"
    )
    visual_balance_score: int = Field(
        ..., ge=1, le=10, description="Visual weight distribution across the page"
    )
    reading_flow_score: int = Field(
        ..., ge=1, le=10, description="Left-to-right, top-to-bottom reading flow"
    )
    text_placement_score: int = Field(
        ..., ge=1, le=10, description="Speech bubble and text positioning"
    )
    feedback: str = Field(..., description="Detailed feedback on composition")
    issues: List[str] = Field(
        default_factory=list, description="Specific composition issues found"
    )
    suggestions: List[str] = Field(
        default_factory=list, description="Suggestions for improvement"
    )


class StoryCriticOutput(BaseModel):
    """Output from the Story Critic - reviews narrative and characters."""

    score: int = Field(..., ge=1, le=10, description="Overall story score (1-10)")
    narrative_coherence_score: int = Field(
        ..., ge=1, le=10, description="Does the visual narrative make sense"
    )
    emotional_impact_score: int = Field(
        ..., ge=1, le=10, description="Emotional effectiveness of the page"
    )
    character_consistency_score: int = Field(
        ..., ge=1, le=10, description="Characters look/act consistently"
    )
    pacing_score: int = Field(
        ..., ge=1, le=10, description="Story pacing on this page"
    )
    feedback: str = Field(..., description="Detailed feedback on story elements")
    issues: List[str] = Field(
        default_factory=list, description="Specific story issues found"
    )
    suggestions: List[str] = Field(
        default_factory=list, description="Suggestions for improvement"
    )


class TechnicalCriticOutput(BaseModel):
    """Output from the Technical Critic - reviews quality and appropriateness."""

    score: int = Field(..., ge=1, le=10, description="Overall technical score (1-10)")
    image_quality_score: int = Field(
        ..., ge=1, le=10, description="Overall image quality and lack of artifacts"
    )
    text_clarity_score: int = Field(
        ..., ge=1, le=10, description="Text is readable and appropriately sized"
    )
    age_appropriateness_score: int = Field(
        ..., ge=1, le=10, description="Content suitable for target age"
    )
    style_consistency_score: int = Field(
        ..., ge=1, le=10, description="Matches requested illustration style"
    )
    feedback: str = Field(..., description="Detailed technical feedback")
    issues: List[str] = Field(
        default_factory=list, description="Specific technical issues found"
    )
    suggestions: List[str] = Field(
        default_factory=list, description="Suggestions for improvement"
    )


class AggregatedCriticReview(BaseModel):
    """Aggregated review from all three critics."""

    composition_review: CompositionCriticOutput
    story_review: StoryCriticOutput
    technical_review: TechnicalCriticOutput
    weighted_score: float = Field(
        ..., ge=1.0, le=10.0, description="Weighted average of all critic scores"
    )
    min_critic_score: int = Field(
        ..., ge=1, le=10, description="Lowest score from any critic"
    )
    failed_min_threshold: bool = Field(
        ..., description="Whether any critic scored below the minimum threshold"
    )
    passes_threshold: bool = Field(
        ..., description="Whether the page passes the quality threshold"
    )
    combined_feedback: str = Field(
        ..., description="Summary of all critic feedback for regeneration"
    )
    priority_improvements: List[str] = Field(
        default_factory=list, description="Most important fixes needed"
    )
    revision_prompt: Optional[str] = Field(
        None, description="Compiled prompt additions for regeneration"
    )


def aggregate_critic_reviews(
    composition: CompositionCriticOutput,
    story: StoryCriticOutput,
    technical: TechnicalCriticOutput,
    composition_weight: float = 0.30,
    story_weight: float = 0.30,
    technical_weight: float = 0.40,
    quality_threshold: float = 7.5,
    min_score_threshold: float = 5.0,
) -> AggregatedCriticReview:
    """
    Aggregate reviews from all critics into a single result.

    Args:
        composition: Composition critic output
        story: Story critic output
        technical: Technical critic output
        composition_weight: Weight for composition score (default: 0.30)
        story_weight: Weight for story score (default: 0.30)
        technical_weight: Weight for technical score (default: 0.40)
        quality_threshold: Minimum weighted score to pass (default: 7.5)
        min_score_threshold: Minimum score ANY critic must give (default: 5.0)

    Returns:
        AggregatedCriticReview with combined results
    """
    # Calculate weighted score
    weighted_score = (
        composition.score * composition_weight
        + story.score * story_weight
        + technical.score * technical_weight
    )

    # Find minimum critic score
    min_critic_score = min(composition.score, story.score, technical.score)
    failed_min_threshold = min_critic_score < min_score_threshold

    # Page passes only if weighted score meets threshold AND no critic is below minimum
    passes = weighted_score >= quality_threshold and not failed_min_threshold

    # Collect all issues and prioritize by severity (lower scores = more severe)
    all_issues = []
    critic_scores = [
        (composition.score, "composition", composition.issues),
        (story.score, "story", story.issues),
        (technical.score, "technical", technical.issues),
    ]

    # Sort by score (lowest first = most problematic)
    critic_scores.sort(key=lambda x: x[0])

    priority_improvements = []
    for score, critic_type, issues in critic_scores:
        if score < 7:  # Only include issues from critics with below-good scores
            for issue in issues[:2]:  # Top 2 issues per critic
                priority_improvements.append(f"[{critic_type}] {issue}")

    # Build combined feedback
    feedback_parts = []
    if composition.score < 7:
        feedback_parts.append(f"Composition ({composition.score}/10): {composition.feedback}")
    if story.score < 7:
        feedback_parts.append(f"Story ({story.score}/10): {story.feedback}")
    if technical.score < 7:
        feedback_parts.append(f"Technical ({technical.score}/10): {technical.feedback}")

    combined_feedback = " | ".join(feedback_parts) if feedback_parts else "All aspects acceptable."

    # Build revision prompt if not passing
    revision_prompt = None
    if not passes:
        revision_parts = ["IMPORTANT IMPROVEMENTS NEEDED:"]

        # Add note about which threshold was violated
        if failed_min_threshold:
            lowest_critic = critic_scores[0]
            revision_parts.append(
                f"CRITICAL: {lowest_critic[1].capitalize()} critic scored {lowest_critic[0]}/10 "
                f"(below minimum {min_score_threshold}). This must be addressed."
            )

        # Add specific suggestions from lowest-scoring critic
        lowest_critic = critic_scores[0]
        if lowest_critic[0] < 7:
            if lowest_critic[1] == "composition":
                revision_parts.extend(composition.suggestions[:3])
            elif lowest_critic[1] == "story":
                revision_parts.extend(story.suggestions[:3])
            else:
                revision_parts.extend(technical.suggestions[:3])

        revision_prompt = " ".join(revision_parts)

    return AggregatedCriticReview(
        composition_review=composition,
        story_review=story,
        technical_review=technical,
        weighted_score=round(weighted_score, 2),
        min_critic_score=min_critic_score,
        failed_min_threshold=failed_min_threshold,
        passes_threshold=passes,
        combined_feedback=combined_feedback,
        priority_improvements=priority_improvements[:5],  # Top 5 priorities
        revision_prompt=revision_prompt,
    )
