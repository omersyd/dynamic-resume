from typing import Dict
from langgraph.graph import StateGraph, END
from langchain_core.language_models import BaseChatModel

from core.state import ResumeState
from core.agents.analyzer import JobAnalyzerAgent
from core.agents.strategist import StrategyAgent
from core.agents.developer import LatexDeveloperAgent
from core.tools.latex_validator import LatexValidator


class ResumeGraphBuilder:
    def __init__(self, model: BaseChatModel):
        self.model = model
        self.analyzer = JobAnalyzerAgent(model)
        self.strategist = StrategyAgent(model)
        self.developer = LatexDeveloperAgent(model)
        self.validator = LatexValidator()

    def build(self):
        workflow = StateGraph(ResumeState)

        # --- NODES ---
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
            print("--- DEVELOPING (Drafting) ---")
            # If we have errors, we might want to append them to the strategy roughly
            # For now, let's just regenerate based on strategy
            # In a more advanced version, we'd feed the errors back into the prompt

            code = await self.developer.build_resume(
                state["job_analysis"],
                state["strategy_plan"],
                state["sample_latex"],
                state["raw_experience"]
            )
            return {"latex_code": code, "revision_count": state.get("revision_count", 0) + 1}

        def validator_node(state: ResumeState) -> Dict:
            print("--- VALIDATING ---")
            is_valid, errors = self.validator.validate(state["latex_code"])
            return {
                "is_valid_latex": is_valid,
                "compilation_errors": errors
            }

        # --- GRAPH CONSTRUCTION ---
        workflow.add_node("analyzer", analyze_node)
        workflow.add_node("strategist", strategy_node)
        workflow.add_node("developer", developer_node)
        workflow.add_node("validator", validator_node)

        # --- EDGES ---
        workflow.set_entry_point("analyzer")
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
