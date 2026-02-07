from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from core.tools.template_parser import TemplateParser


class LatexDeveloperAgent:
    def __init__(self, model: BaseChatModel):
        self.model = model

    async def build_resume(
        self,
        job_analysis: str,
        strategy: str,
        sample_latex: str,
        experience: str,
        template_preamble: str,
        template_body: str,
        command_cheatsheet: str,
        previous_errors: list = None
    ) -> str:
        system_prompt = """You are an expert Resume Content Writer.

Your job is to generate ONLY the document body of a LaTeX resume.
The preamble (packages, commands, settings) is handled separately — you must NOT produce it.

RULES:
1. Output ONLY the body content that goes between \\begin{{document}} and \\end{{document}}.
2. Do NOT include \\documentclass, \\usepackage, \\newcommand, \\begin{{document}}, or \\end{{document}}.
3. Use ONLY the custom commands listed in the cheatsheet below — these are defined in the template preamble.
4. Follow the structure of the sample body as a reference for how to organize sections and use commands.
5. Replace the content (names, titles, bullets, skills, education) with the candidate's experience.
6. Follow the content strategy to decide which experiences to highlight and how to frame them.
7. Do NOT wrap your output in markdown code blocks or add any explanations.
8. Output raw LaTeX body content only — nothing else.

{command_cheatsheet}"""

        user_prompt_parts = [
            "JOB REQUIREMENTS ANALYSIS:",
            "{job_analysis}",
            "",
            "CONTENT STRATEGY (What to emphasize):",
            "{strategy}",
            "",
            "SAMPLE BODY (Use this structure as reference — replace content only):",
            "{template_body}",
            "",
            "CANDIDATE'S RAW EXPERIENCE (Content source):",
            "{experience}",
            ""
        ]

        if previous_errors:
            user_prompt_parts.extend([
                "PREVIOUS ATTEMPT FAILED — FIX THESE ERRORS:",
                "{error_feedback}",
                "",
            ])

        user_prompt_parts.extend([
            "Generate the resume body content now.",
            "Use the custom commands from the cheatsheet.",
            "Follow the sample body structure.",
            "Output ONLY the LaTeX body — no preamble, no \\begin{{document}}, no \\end{{document}}."
        ])

        user_prompt = "\n".join(user_prompt_parts)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", user_prompt),
            ]
        )

        chain = prompt | self.model | StrOutputParser()

        invoke_params = {
            "job_analysis": job_analysis,
            "strategy": strategy,
            "template_body": template_body,
            "experience": experience,
            "command_cheatsheet": command_cheatsheet,
        }

        if previous_errors:
            error_text = "\n".join(f"- {err}" for err in previous_errors)
            invoke_params["error_feedback"] = error_text

        response = await chain.ainvoke(invoke_params)

        # Clean the LLM body output
        body = self._clean_body(response)

        # Reassemble with the preserved preamble
        return TemplateParser.reassemble(template_preamble, body)

    @staticmethod
    def _clean_body(raw: str) -> str:
        """Clean LLM output to extract just the body content."""
        clean = raw.replace("```latex", "").replace("```", "").strip()

        # If the LLM accidentally included preamble, extract just the body
        begin_marker = r"\begin{document}"
        end_marker = r"\end{document}"

        if begin_marker in clean:
            start = clean.find(begin_marker) + len(begin_marker)
            clean = clean[start:]

        if end_marker in clean:
            end = clean.find(end_marker)
            clean = clean[:end]

        # Strip \documentclass and everything before first real content
        if "\\documentclass" in clean:
            # Find first section or center or other body command
            for marker in ["\\begin{center}", "\\section", "\\resumeSubHeadingListStart"]:
                idx = clean.find(marker)
                if idx != -1:
                    clean = clean[idx:]
                    break

        return clean.strip()
