from typing import Dict
from langgraph.graph import StateGraph, END
from langchain_core.language_models import BaseChatModel

from core.state import ResumeState
from core.agents.analyzer import JobAnalyzerAgent
from core.agents.strategist import StrategyAgent
from core.agents.developer import LatexDeveloperAgent
from core.tools.latex_validator import LatexValidator
from core.tools.template_verifier import TemplateVerifier
from core.tools.template_parser import TemplateParser


class ResumeGraphBuilder:
    def __init__(
        self,
        analyzer_model: BaseChatModel,
        strategist_model: BaseChatModel,
        developer_model: BaseChatModel
    ):
        """
        Initialize the Resume Graph Builder with individual models for each agent.

        Args:
            analyzer_model: Model for job analysis (can be a lighter/faster model)
            strategist_model: Model for strategy planning (requires reasoning)
            developer_model: Model for LaTeX generation (requires precision)
        """
        self.analyzer = JobAnalyzerAgent(analyzer_model)
        self.strategist = StrategyAgent(strategist_model)
        self.developer = LatexDeveloperAgent(developer_model)
        self.validator = LatexValidator()
        self.template_verifier = TemplateVerifier()
        self.template_parser = TemplateParser()

    def build(self):
        workflow = StateGraph(ResumeState)

        # --- NODES ---
        def parser_node(state: ResumeState) -> Dict:
            print("--- PARSING TEMPLATE ---")
            parsed = self.template_parser.parse(state["sample_latex"])
            return {
                "template_preamble": parsed["preamble"],
                "template_body": parsed["body"],
                "command_cheatsheet": parsed["command_cheatsheet"]
            }

        async def analyze_node(state: ResumeState) -> Dict:
            print("--- ANALYZING ---")
            analysis = await self.analyzer.analyze(state["job_description"])
            return {"job_analysis": analysis}

        async def strategy_node(state: ResumeState) -> Dict:
            print("--- STRATEGIZING ---")
            strategy = await self.strategist.plan(
                state["job_analysis"],
                state["raw_experience"]
            )
            return {"strategy_plan": strategy}

        async def developer_node(state: ResumeState) -> Dict:
            revision = state.get("revision_count", 0) + 1
            print(f"--- DEVELOPING (Attempt {revision}) ---")

            # Pass previous errors if this is a retry
            previous_errors = state.get("compilation_errors", []) if revision > 1 else None

            if previous_errors:
                print(f"⚠️  Retry with {len(previous_errors)} previous errors")

            code = await self.developer.build_resume(
                job_analysis=state["job_analysis"],
                strategy=state["strategy_plan"],
                sample_latex=state["sample_latex"],
                experience=state["raw_experience"],
                template_preamble=state["template_preamble"],
                template_body=state["template_body"],
                command_cheatsheet=state["command_cheatsheet"],
                previous_errors=previous_errors
            )
            return {"latex_code": code, "revision_count": revision}

        def validator_node(state: ResumeState) -> Dict:
            print("--- VALIDATING ---")
            errors = []

            # 1. Syntax validation
            is_syntax_valid, syntax_errors = self.validator.validate(state["latex_code"])
            errors.extend(syntax_errors)

            # 2. Template preservation (lightweight: document class + boundaries)
            is_template_valid, template_issues = self.template_verifier.verify_template_preservation(
                state["sample_latex"],
                state["latex_code"]
            )
            errors.extend(template_issues)

            is_valid = is_syntax_valid and is_template_valid

            if not is_valid:
                print(f"⚠️  Validation failed: {len(errors)} issues")

            return {
                "is_valid_latex": is_valid,
                "compilation_errors": errors
            }

        # --- GRAPH CONSTRUCTION ---
        workflow.add_node("parser", parser_node)
        workflow.add_node("analyzer", analyze_node)
        workflow.add_node("strategist", strategy_node)
        workflow.add_node("developer", developer_node)
        workflow.add_node("validator", validator_node)

        # --- EDGES ---
        workflow.set_entry_point("parser")
        workflow.add_edge("parser", "analyzer")
        workflow.add_edge("analyzer", "strategist")
        workflow.add_edge("strategist", "developer")
        workflow.add_edge("developer", "validator")

        # --- CONDITIONAL EDGE (The Loop) ---
        def should_continue(state: ResumeState):
            if state["is_valid_latex"]:
                print("--- DONE: VALID LATEX ---")
                return END

            if state["revision_count"] >= 3:
                print("--- DONE: MAX RETRIES REACHED ---")
                return END

            print(f"--- RETRYING (Errors: {state['compilation_errors']}) ---")
            return "developer"

        workflow.add_conditional_edges(
            "validator",
            should_continue,
            {
                END: END,
                "developer": "developer"
            }
        )

        return workflow.compile()
