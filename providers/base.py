"""
Base LLM Provider Interface

All LLM providers must inherit from this class and implement the generate method.
This allows for plug-and-play provider switching.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    temperature: float = 0.7
    max_tokens: int = 4096


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    def __init__(self, api_key: Optional[str] = None, model: str = ""):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> str:
        """
        Generate text based on the given prompt.

        Args:
            prompt: The input prompt for generation
            config: Optional generation configuration

        Returns:
            Generated text as a string
        """
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate that the provider connection is working.

        Returns:
            True if connection is valid, False otherwise
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider."""
        pass

    def _get_config(self, config: Optional[GenerationConfig]) -> GenerationConfig:
        """Helper to get config with defaults."""
        return config or GenerationConfig()
