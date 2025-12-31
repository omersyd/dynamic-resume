"""
Anthropic Provider Implementation

Supports: Claude Sonnet 4, Claude 3.5 Haiku, Claude 3 Opus
"""

from typing import Optional
import anthropic

from .base import BaseLLMProvider, GenerationConfig


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        super().__init__(api_key=api_key, model=model)
        self.client = anthropic.Anthropic(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "Anthropic"

    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> str:
        """Generate text using Anthropic API."""
        cfg = self._get_config(config)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=cfg.max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=cfg.temperature,
            )
            # Extract text from response
            if response.content and len(response.content) > 0:
                return response.content[0].text
            return ""
        except Exception as e:
            raise RuntimeError(f"Anthropic generation failed: {str(e)}")

    def validate_connection(self) -> bool:
        """Validate Anthropic API connection."""
        try:
            # Simple test - try to create a minimal message
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception:
            return False
