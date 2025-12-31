"""
Prompt Templates for Resume Generation

Contains system prompts for different creativity levels and the main generation prompt.
"""

# Creativity level descriptions for UI
CREATIVITY_LEVELS = {
    1: {
        "name": "Conservative",
        "description": "Minimal changes - only reorganize and select relevant content",
        "temperature": 0.3,
    },
    2: {
        "name": "Moderate",
        "description": "Light rewording to incorporate job description keywords",
        "temperature": 0.5,
    },
    3: {
        "name": "Balanced",
        "description": "Actively tailor content while staying truthful",
        "temperature": 0.7,
    },
    4: {
        "name": "Creative",
        "description": "Significant rewriting to emphasize relevant skills",
        "temperature": 0.8,
    },
    5: {
        "name": "Bold",
        "description": "Maximum adaptation - infer and highlight transferable skills",
        "temperature": 0.9,
    },
}


def get_system_prompt(creativity_level: int) -> str:
    """Get the system prompt based on creativity level."""

    base_instructions = """You are an expert resume writer and career coach with deep knowledge of
ATS (Applicant Tracking Systems) and hiring practices.

Your task is to generate a tailored LaTeX resume based on:
1. A sample LaTeX resume (which defines the style and structure to follow)
2. The candidate's experience and background
3. A target job description

CRITICAL RULES:
- Output ONLY valid LaTeX code that can be compiled directly
- Do NOT include any explanations, markdown, or text outside the LaTeX
- Do NOT wrap the output in ```latex``` code blocks
- Preserve the exact LaTeX structure, packages, and formatting from the sample
- The output should compile without errors in Overleaf or any LaTeX compiler
"""

    creativity_instructions = {
        1: """
CONSERVATIVE MODE:
- Only select and reorganize existing experience points that match the job
- Make minimal text changes - mostly structural reorganization
- Keep original wording as much as possible
- Prioritize relevant experiences at the top
- Remove irrelevant experiences if space is needed
""",
        2: """
MODERATE MODE:
- Reorganize content to highlight relevant experience
- Lightly reword bullet points to incorporate keywords from the job description
- Keep the essence of original experiences intact
- Adjust emphasis without changing facts
- Mirror terminology used in the job posting
""",
        3: """
BALANCED MODE:
- Actively tailor each bullet point to resonate with the job requirements
- Rewrite content to emphasize relevant skills and achievements
- Add context that connects experience to job requirements
- Quantify achievements where possible
- Maintain truthfulness while optimizing presentation
""",
        4: """
CREATIVE MODE:
- Significantly rewrite bullet points to maximize relevance
- Highlight transferable skills even if not directly mentioned
- Reframe experiences to align with job requirements
- Create stronger connections between past work and target role
- Use powerful action verbs and impactful language
""",
        5: """
BOLD MODE:
- Maximum adaptation to match the job description
- Infer and articulate implied skills from the experience
- Creatively connect seemingly unrelated experiences to job requirements
- Craft compelling narratives that position the candidate as ideal
- Push the boundaries while staying within truthful bounds
- Make the resume impossible to ignore
"""
    }

    return base_instructions + creativity_instructions.get(creativity_level, creativity_instructions[3])


def get_generation_prompt(
    sample_latex: str,
    experience: str,
    job_description: str,
    custom_instructions: str = ""
) -> str:
    """Build the complete prompt for resume generation."""

    prompt = f"""## SAMPLE LATEX RESUME (Follow this exact style and structure):

{sample_latex}

---

## CANDIDATE'S EXPERIENCE AND BACKGROUND:

{experience}

---

## TARGET JOB DESCRIPTION:

{job_description}

---"""

    if custom_instructions.strip():
        prompt += f"""

## ADDITIONAL INSTRUCTIONS FROM USER:

{custom_instructions}

---"""

    prompt += """

## YOUR TASK:

Generate a complete, compilable LaTeX resume that:
1. Uses the EXACT same LaTeX structure, packages, and styling from the sample
2. Tailors the candidate's experience to match the job description
3. Highlights relevant skills and achievements
4. Is optimized for ATS systems
5. Fits appropriately (typically 1-2 pages)

Output the complete LaTeX code now, starting with \\documentclass:
"""

    return prompt
