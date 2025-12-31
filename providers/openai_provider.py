"""
OpenAI Provider Implementation

Supports: GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
"""

from typing import Optional
from openai import OpenAI

from .base import BaseLLMProvider, GenerationConfig


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(api_key=api_key, model=model)
        self.client = OpenAI(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> str:
        """Generate text using OpenAI API."""
        cfg = self._get_config(config)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {str(e)}")

    def validate_connection(self) -> bool:
        """Validate OpenAI API connection."""
        try:
            # Simple test call
            self.client.models.list()
            return True
        except Exception:
            return False
