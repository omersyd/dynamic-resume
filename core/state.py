from typing import TypedDict, List, Optional, Annotated
import operator


class ResumeState(TypedDict):
    """
    Represents the working memory of the resume generation process.
    This state is transient and exists only during the generation job.
    """

    # --- INPUTS (Dynamic Data from User) ---
    job_description: str
    raw_experience: str
    sample_latex: str  # The template style to match

    # --- INTERNAL STATE (Agent Thoughts) ---
    job_analysis: Optional[str]      # Output of Analyzer
    strategy_plan: Optional[str]     # Output of Strategist

    # --- OUTPUTS (Drafts) ---
    latex_code: Optional[str]        # Current draft

    # --- FEEDBACK LOOP ---
    compilation_errors: Annotated[List[str], operator.add]  # Accumulates errors over steps
    revision_count: int              # To prevent infinite loops (e.g., max 3 retries)
    is_valid_latex: bool             # Flag to signal completion
