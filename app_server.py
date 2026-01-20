from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os

from core.graph import ResumeGraphBuilder
from core.model_factory import ModelFactory

app = FastAPI(title="Dynamic Resume Creator API")


# --- Pydantic Models ---
class ResumeRequest(BaseModel):
    job_description: str
    raw_experience: str
    sample_latex: str

    # LLM Config
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "job_description": "We need a Python dev...",
                "raw_experience": "I have 5 years of Python...",
                "sample_latex": "\\documentclass{article}...",
                "provider": "openai",
                "model": "gpt-4o"
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
        # 1. Initialize Model
        # If API key is not provided in request, check env var
        api_key = request.api_key or os.getenv(f"{request.provider.upper()}_API_KEY")

        # Validation for keys if using paid providers
        if request.provider in ["openai", "anthropic", "gemini", "groq"] and not api_key:
            raise HTTPException(status_code=400, detail=f"API Key for {request.provider} is required.")

        model = ModelFactory.get_model(
            provider=request.provider,
            model_name=request.model,
            api_key=api_key
        )

        # 2. Build Graph
        builder = ResumeGraphBuilder(model)
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
