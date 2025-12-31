"""
Ollama Provider Implementation

Supports: Llama 3.3, Llama 3.2, Mistral, CodeLlama, Phi3
100% local and free!
"""

from typing import Optional
import requests

from .base import BaseLLMProvider, GenerationConfig


class OllamaProvider(BaseLLMProvider):
    """Ollama local provider - Free, private, runs locally."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "llama3.3",
        endpoint: str = "http://localhost:11434"
    ):
        super().__init__(api_key=api_key, model=model)
        self.endpoint = endpoint

    @property
    def provider_name(self) -> str:
        return "Ollama"

    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> str:
        """Generate text using Ollama local API."""
        cfg = self._get_config(config)

        try:
            response = requests.post(
                f"{self.endpoint}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": cfg.temperature,
                        "num_predict": cfg.max_tokens,
                    }
                },
                timeout=300  # 5 min timeout for local models
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Cannot connect to Ollama. Make sure Ollama is running:\n"
                "1. Install Ollama from https://ollama.ai\n"
                "2. Run 'ollama serve' in terminal\n"
                f"3. Pull model with 'ollama pull {self.model}'"
            )
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")

    def validate_connection(self) -> bool:
        """Validate Ollama connection."""
        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def list_available_models(self) -> list:
        """List models available in local Ollama installation."""
        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m["name"] for m in models]
            return []
        except Exception:
            return []
