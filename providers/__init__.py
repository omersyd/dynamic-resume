# LLM Providers - Pluggable architecture
from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .groq_provider import GroqProvider
from .ollama_provider import OllamaProvider
from .gemini_provider import GeminiProvider

PROVIDERS = {
    "OpenAI": OpenAIProvider,
    "Anthropic": AnthropicProvider,
    "Groq": GroqProvider,
    "Ollama": OllamaProvider,
    "Google Gemini": GeminiProvider,
}

PROVIDER_MODELS = {
    "OpenAI": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    "Anthropic": ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
    "Groq": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
    "Ollama": ["llama3.3", "llama3.2", "mistral", "codellama", "phi3"],
    "Google Gemini": ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
}

__all__ = [
    "BaseLLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "GroqProvider",
    "OllamaProvider",
    "GeminiProvider",
    "PROVIDERS",
    "PROVIDER_MODELS",
]
