from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os

from core.graph import ResumeGraphBuilder
from core.model_factory import ModelFactory

app = FastAPI(title="Dynamic Resume Creator API")


# --- Pydantic Models ---
class ModelConfig(BaseModel):
    """Configuration for a single LLM model."""
    provider: str
    model: str
    api_key: Optional[str] = None


class ResumeRequest(BaseModel):
    job_description: str
    raw_experience: str
    sample_latex: str

    # Individual model configs for each agent
    analyzer_config: Optional[ModelConfig] = None
    strategist_config: Optional[ModelConfig] = None
    developer_config: Optional[ModelConfig] = None

    # Legacy single model config (for backward compatibility)
    # If individual configs are not provided, these will be used for all agents
    provider: Optional[str] = "openai"
    model: Optional[str] = "gpt-4o"
    api_key: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "job_description": "We need a Python dev...",
                "raw_experience": "I have 5 years of Python...",
                "sample_latex": "\\documentclass{article}...",
                "analyzer_config": {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo"
                },
                "strategist_config": {
                    "provider": "anthropic",
                    "model": "claude-3-sonnet-20240229"
                },
                "developer_config": {
                    "provider": "openai",
                    "model": "gpt-4o"
                }
            }
        }


class ResumeResponse(BaseModel):
    final_latex: str
    analysis: str
    strategy: str
    is_valid: bool
    errors: List[str]
    revision_count: int


# --- Routes ---
@app.post("/generate", response_model=ResumeResponse)
async def generate_resume(request: ResumeRequest):
    try:
        # Helper function to get model config
        def get_model_config(agent_name: str, agent_config: Optional[ModelConfig]) -> tuple:
            """Returns (provider, model_name, api_key) for an agent."""
            if agent_config:
                # Use agent-specific config
                provider = agent_config.provider
                model_name = agent_config.model
                api_key = agent_config.api_key or os.getenv(f"{provider.upper()}_API_KEY")
            else:
                # Fallback to legacy single config
                provider = request.provider
                model_name = request.model
                api_key = request.api_key or os.getenv(f"{provider.upper()}_API_KEY")

            # Validate API key for paid providers
            if provider in ["openai", "anthropic", "gemini", "groq"] and not api_key:
                raise HTTPException(
                    status_code=400,
                    detail=f"API Key for {provider} is required for {agent_name}."
                )

            return provider, model_name, api_key

        # 1. Initialize Models for each agent
        analyzer_provider, analyzer_model_name, analyzer_api_key = get_model_config(
            "Analyzer", request.analyzer_config
        )
        strategist_provider, strategist_model_name, strategist_api_key = get_model_config(
            "Strategist", request.strategist_config
        )
        developer_provider, developer_model_name, developer_api_key = get_model_config(
            "Developer", request.developer_config
        )

        analyzer_model = ModelFactory.get_model(
            provider=analyzer_provider,
            model_name=analyzer_model_name,
            api_key=analyzer_api_key
        )
        strategist_model = ModelFactory.get_model(
            provider=strategist_provider,
            model_name=strategist_model_name,
            api_key=strategist_api_key
        )
        developer_model = ModelFactory.get_model(
            provider=developer_provider,
            model_name=developer_model_name,
            api_key=developer_api_key
        )

        # 2. Build Graph with individual models
        builder = ResumeGraphBuilder(
            analyzer_model=analyzer_model,
            strategist_model=strategist_model,
            developer_model=developer_model
        )
        graph = builder.build()

        # 3. Invoke Graph
        inputs = {
            "job_description": request.job_description,
            "raw_experience": request.raw_experience,
            "sample_latex": request.sample_latex,
            "revision_count": 0,
            "compilation_errors": []
        }

        # Invoke (this runs the loop)
        final_state = await graph.ainvoke(inputs)

        return ResumeResponse(
            final_latex=final_state.get("latex_code", ""),
            analysis=final_state.get("job_analysis", ""),
            strategy=final_state.get("strategy_plan", ""),
            is_valid=final_state.get("is_valid_latex", False),
            errors=final_state.get("compilation_errors", []),
            revision_count=final_state.get("revision_count", 0)
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}
