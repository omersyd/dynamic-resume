from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate


class JobAnalyzerAgent:
    def __init__(self, model: BaseChatModel):
        self.model = model

    async def analyze(self, job_description: str) -> str:
        system_prompt = (
            "You are an expert Talent Acquisition Specialist."
            "Your goal is to extract the critical signal from a job description to help a"
            "candidate tailor their resume perfectly."
            "Analyze the provided job description and output the following analysis:"
            "1. CORE SKILLS: The top 3-5 hard skills absolutely required."
            "2. KEYWORDS: Specific terminology, tools, or buzzwords the ATS (Applicant Tracking System) will search for"
            "3. HIDDEN NEEDS: What is the underlying problem they are hiring to solve?"
            " (e.g., 'scaling legacy systems', 'building a team from scratch')."
            "4. CULTURE VIBE: The tone of the company "
            "(e.g., 'fast-paced startup', 'structured corporate', 'academic/research')."
            "Keep your analysis concise and actionable."
        )

        prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", "{job_description}")]
        )

        chain = prompt | self.model
        response = await chain.ainvoke({"job_description": job_description})
        return response.content
