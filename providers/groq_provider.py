"""
Groq Provider Implementation

Supports: Llama 3.3 70B, Llama 3.1 8B, Mixtral 8x7B
Free tier available!
"""

from typing import Optional
from groq import Groq

from .base import BaseLLMProvider, GenerationConfig


class GroqProvider(BaseLLMProvider):
    """Groq API provider - Fast inference with free tier."""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        super().__init__(api_key=api_key, model=model)
        self.client = Groq(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "Groq"

    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> str:
        """Generate text using Groq API."""
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
            raise RuntimeError(f"Groq generation failed: {str(e)}")

    def validate_connection(self) -> bool:
        """Validate Groq API connection."""
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
