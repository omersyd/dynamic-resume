"""
Resume Generator Core Logic

This module orchestrates the resume generation process using the pluggable LLM providers.
"""

from typing import Optional
from providers.base import BaseLLMProvider, GenerationConfig
from core.prompts import get_system_prompt, get_generation_prompt, CREATIVITY_LEVELS


class ResumeGenerator:
    """Main class for generating tailored resumes."""

    def __init__(self, provider: BaseLLMProvider):
        """
        Initialize the resume generator with an LLM provider.

        Args:
            provider: An instance of a class implementing BaseLLMProvider
        """
        self.provider = provider

    def generate(
        self,
        sample_latex: str,
        experience: str,
        job_description: str,
        creativity_level: int = 3,
        custom_instructions: str = ""
    ) -> str:
        """
        Generate a tailored resume.

        Args:
            sample_latex: Sample LaTeX resume defining the style
            experience: Candidate's full experience and background
            job_description: Target job description
            creativity_level: 1-5, how much creative liberty to take
            custom_instructions: Optional additional instructions

        Returns:
            Generated LaTeX resume as a string
        """
        # Validate creativity level
        if creativity_level not in CREATIVITY_LEVELS:
            creativity_level = 3

        # Get system prompt based on creativity level
        system_prompt = get_system_prompt(creativity_level)

        # Build the generation prompt
        generation_prompt = get_generation_prompt(
            sample_latex=sample_latex,
            experience=experience,
            job_description=job_description,
            custom_instructions=custom_instructions
        )

        # Combine system and user prompts
        full_prompt = f"{system_prompt}\n\n{generation_prompt}"

        # Get temperature from creativity level
        temperature = CREATIVITY_LEVELS[creativity_level]["temperature"]

        # Configure generation
        config = GenerationConfig(
            temperature=temperature,
            max_tokens=8192  # Resumes can be lengthy in LaTeX
        )

        # Generate the resume
        generated_latex = self.provider.generate(full_prompt, config)

        # Clean up the output (remove any markdown code blocks if present)
        generated_latex = self._clean_latex_output(generated_latex)

        return generated_latex

    def _clean_latex_output(self, output: str) -> str:
        """
        Clean the generated output to ensure it's valid LaTeX.

        Args:
            output: Raw output from the LLM

        Returns:
            Cleaned LaTeX string
        """
        # Remove markdown code blocks if present
        output = output.strip()

        # Remove ```latex or ``` wrapping
        if output.startswith("```latex"):
            output = output[8:]
        elif output.startswith("```"):
            output = output[3:]

        if output.endswith("```"):
            output = output[:-3]

        output = output.strip()

        # Ensure it starts with a LaTeX command
        # Find the first backslash (start of LaTeX)
        first_backslash = output.find("\\")
        if first_backslash > 0:
            # There might be some text before the LaTeX, remove it
            output = output[first_backslash:]

        return output


def create_provider(
    provider_name: str,
    api_key: Optional[str] = None,
    model: str = "",
    ollama_endpoint: str = "http://localhost:11434"
) -> BaseLLMProvider:
    """
    Factory function to create the appropriate provider.

    Args:
        provider_name: Name of the provider (OpenAI, Anthropic, etc.)
        api_key: API key for cloud providers
        model: Model name to use
        ollama_endpoint: Endpoint for Ollama (only used for Ollama provider)

    Returns:
        An instance of the appropriate provider
    """
    from providers import PROVIDERS, PROVIDER_MODELS

    if provider_name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider_name}")

    # Get default model if not specified
    if not model:
        model = PROVIDER_MODELS[provider_name][0]

    provider_class = PROVIDERS[provider_name]

    # Special handling for Ollama (doesn't need API key)
    if provider_name == "Ollama":
        from providers.ollama_provider import OllamaProvider
        return OllamaProvider(model=model, endpoint=ollama_endpoint)

    # Cloud providers need API key
    if not api_key:
        raise ValueError(f"{provider_name} requires an API key")

    return provider_class(api_key=api_key, model=model)
