from providers.base import BaseLLMProvider, GenerationConfig


class BaseAgent:
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        config = GenerationConfig(temperature=temperature)
        return self.provider.generate(full_prompt, config)
