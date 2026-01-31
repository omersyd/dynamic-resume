from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate


class StrategyAgent:
    def __init__(self, model: BaseChatModel):
        self.model = model

    async def plan(self, job_analysis: str, experience: str) -> str:
        system_prompt = (
            "You are a Senior Career Coach and Resume Strategist."
            "Your goal is to create a 'Content Strategy' for a resume that bridges a"
            "candidate's experience with a target job."
            "You will be given:"
            "1. A Job Analysis (containing core skills, keywords, and hidden needs)"
            "2. The Candidate's Experience"
            "Your task:"
            "Create a detailed plan for how to write the resume. Do NOT write the final resume."
            "Instead, write a strategy document that includes:"
            "1. SUMMARY STRATEGY: What 2-3 key strengths should be highlighted in the professional summary?"
            "2. EXPERIENCE SELECTION: Which specific roles or projects from the"
            "candidate's history are most relevant?"
            "Which ones should be minimized?"
            "3. BULLET POINT ANGLES: For the top relevant roles, explain how to frame"
            "the achievements to match the Job Analysis."
            "- Example:"
            " For the Senior Dev role, focus less on Java maintenance and more on the cloud migration "
            "project to align with the job's Hidden Need."
            "4. KEYWORD INTEGRATION: List specific keywords from the analysis that must be"
            "naturally woven into the bullet points."
            "Be specific and tactical."
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "human",
                    """
                    JOB ANALYSIS:
                    {job_analysis}

                    CANDIDATE EXPERIENCE:
                    {experience}
                    """,
                ),
            ]
        )

        chain = prompt | self.model
        response = await chain.ainvoke(
            {"job_analysis": job_analysis, "experience": experience}
        )
        return response.content
