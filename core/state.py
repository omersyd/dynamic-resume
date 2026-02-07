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

    # --- PARSED TEMPLATE ---
    template_preamble: Optional[str]   # Verbatim preamble (preserved programmatically)
    template_body: Optional[str]       # Original body (structural reference for LLM)
    command_cheatsheet: Optional[str]  # Custom command signatures

    # --- INTERNAL STATE (Agent Thoughts) ---
    job_analysis: Optional[str]      # Output of Analyzer
    strategy_plan: Optional[str]     # Output of Strategist

    # --- OUTPUTS (Drafts) ---
    latex_code: Optional[str]        # Current draft

    # --- FEEDBACK LOOP ---
    compilation_errors: Annotated[List[str], operator.add]  # Accumulates errors over steps
    revision_count: int              # To prevent infinite loops (e.g., max 3 retries)
    is_valid_latex: bool             # Flag to signal completion
