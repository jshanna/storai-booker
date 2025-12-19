"""Critic agents for reviewing generated comic pages."""

from .base_critic import BaseCriticAgent
from .composition_critic import CompositionCriticAgent
from .story_critic import StoryCriticAgent
from .technical_critic import TechnicalCriticAgent

__all__ = [
    "BaseCriticAgent",
    "CompositionCriticAgent",
    "StoryCriticAgent",
    "TechnicalCriticAgent",
]
