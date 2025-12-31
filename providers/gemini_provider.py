"""
Google Gemini Provider Implementation

Supports: Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash
"""

from typing import Optional
from google import genai
from google.genai import types

from .base import BaseLLMProvider, GenerationConfig


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        super().__init__(api_key=api_key, model=model)
        self.client = genai.Client(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "Google Gemini"

    def generate(
        self, prompt: str, config: Optional[GenerationConfig] = None
    ) -> str:
        """Generate text using Google Gemini API."""
        cfg = self._get_config(config)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=cfg.temperature,
                    max_output_tokens=cfg.max_tokens,
                ),
            )
            return response.text or ""
        except Exception as e:
            raise RuntimeError(f"Gemini generation failed: {str(e)}")

    def validate_connection(self) -> bool:
        """Validate Gemini API connection."""
        try:
            # Simple test generation
            response = self.client.models.generate_content(
                model=self.model,
                contents="Hi",
            )
            return response.text is not None
        except Exception:
            return False
