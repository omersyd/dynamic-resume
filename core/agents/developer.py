from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class LatexDeveloperAgent:
    def __init__(self, model: BaseChatModel):
        self.model = model

    async def build_resume(
        self, job_analysis: str, strategy: str, sample_latex: str, experience: str
    ) -> str:
        system_prompt = (
            "You are an expert LaTeX Developer and Resume Writer."
            "Your goal is to execute a resume rewrite based on a specific strategy and style template."
            "You have three inputs:"
            "1. A Strategy Plan (tells you WHAT to write and emphasize)"
            "2. A Sample LaTeX Resume (tells you HOW it should look - structure/formatting)"
            "3. The Candidate's raw experience (the source data)"
            "CRITICAL RULES:"
            "- Output ONLY valid LaTeX code."
            "- Do NOT output markdown formatting (like ```latex)."
            "- Do NOT include any intro or outro text."
            "- STRICTLY follow the structure/packages/commands of the Sample LaTeX."
            "- Implement the 'Strategy Plan' implicitly in the content you write."
            "- Use the keywords from the strategy."
            "- Ensure the result compiles perfectly."
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "human",
                    """
                    STRATEGY PLAN:
                    {strategy}

                    SAMPLE LATEX (Format Template):
                    {sample_latex}

                    CANDIDATE RAW EXPERIENCE:
                    {experience}

                    Please generate the final LaTeX resume code now.
                    """,
                ),
            ]
        )

        chain = prompt | self.model | StrOutputParser()

        # Invoke asynchronously
        response = await chain.ainvoke(
            {
                "strategy": strategy,
                "sample_latex": sample_latex,
                "experience": experience,
            }
        )

        # Basic cleanup just in case
        clean_latex = response.replace("```latex", "").replace("```", "").strip()
        return clean_latex
