from providers.base import BaseLLMProvider
from core.agents.analyzer import JobAnalyzerAgent
from core.agents.strategist import StrategyAgent
from core.agents.developer import LatexDeveloperAgent
from typing import Generator


class ResumeOrchestrator:
    def __init__(self, provider: BaseLLMProvider):
        self.analyzer = JobAnalyzerAgent(provider)
        self.strategist = StrategyAgent(provider)
        self.developer = LatexDeveloperAgent(provider)

    def run_pipeline(
        self,
        sample_latex: str,
        experience: str,
        job_description: str,
        custom_instructions: str = ""
    ) -> Generator[dict, None, None]:
        """
        Runs the full 3-step agent pipeline.
        Returns a dictionary with intermediate artifacts and the final result.
        """

        # Step 1: Analyze
        yield {"step": "analyzing", "message": "🕵️ analyzing job description..."}
        analysis = self.analyzer.analyze(job_description)

        # Step 2: Strategize
        yield {"step": "strategizing", "message": "🧠 formulating resume strategy..."}
        strategy = self.strategist.plan(analysis, experience, custom_instructions)

        # Step 3: Develop
        yield {"step": "developing", "message": "📝 writing LaTeX code..."}
        final_latex = self.developer.build_resume(
            job_analysis=analysis,
            strategy=strategy,
            sample_latex=sample_latex,
            experience=experience
        )

        yield {
            "step": "complete",
            "analysis": analysis,
            "strategy": strategy,
            "latex": final_latex
        }
