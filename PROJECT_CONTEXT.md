# Dynamic Resume Creator — Project Context for LLMs

This document describes the Dynamic Resume Creator project in a structured format optimized for LLM comprehension. Use it as grounding context when working on, extending, or debugging this codebase.

---

## 1. Purpose

This application generates tailored LaTeX resumes by analyzing job descriptions and matching them against a candidate's experience. It uses a multi-agent LLM pipeline orchestrated by LangGraph, served via FastAPI, and presented through a Streamlit UI.

**Core value:** A user pastes a job description, their raw experience, and a sample LaTeX resume. The system produces a new LaTeX resume tailored to that specific job, preserving the original template's structure.

---

## 2. Tech Stack

| Layer | Technology | Role |
|-------|-----------|------|
| Frontend | Streamlit | Web UI for input/output |
| API | FastAPI + Uvicorn | REST backend |
| Orchestration | LangGraph (StateGraph) | Multi-agent pipeline with retry loop |
| LLM Abstraction | LangChain (ChatPromptTemplate, ChatModel) | Uniform interface across providers |
| Validation | Pydantic v2 | Request/response schemas |
| LLM Providers | OpenAI, Anthropic, Google Gemini, Groq, Ollama | Pluggable model backends |

Python 3.12. All dependencies listed in `requirements.txt`.

---

## 3. Project Structure

```
dynamic-resume-creator/
├── app.py                            # Streamlit frontend
├── app_server.py                     # FastAPI backend (POST /generate, GET /health)
├── requirements.txt
├── core/
│   ├── state.py                      # ResumeState TypedDict (pipeline state)
│   ├── graph.py                      # LangGraph StateGraph (nodes + edges)
│   ├── model_factory.py              # Factory: provider string → ChatModel instance
│   ├── prompts.py                    # Prompt templates for 5 creativity levels
│   ├── orchestrator.py               # Legacy generator-based orchestrator (unused by current flow)
│   ├── resume_generator.py           # Legacy generator class (unused by current flow)
│   ├── agents/
│   │   ├── base.py                   # Legacy BaseAgent ABC
│   │   ├── analyzer.py               # JobAnalyzerAgent — extracts job requirements
│   │   ├── strategist.py             # StrategyAgent — plans resume content
│   │   └── developer.py              # LatexDeveloperAgent — generates LaTeX code
│   └── tools/
│       ├── latex_validator.py        # Syntax checks (brace balance, env pairing)
│       ├── template_parser.py        # Splits template into preamble + body + cheatsheet
│       └── template_verifier.py      # Structural checks (document class, boundaries)
├── providers/                        # LLM provider wrappers (legacy direct-call layer)
│   ├── base.py                       # BaseLLMProvider ABC + GenerationConfig
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── gemini_provider.py
│   ├── groq_provider.py
│   └── ollama_provider.py
├── .github/
│   └── copilot-instructions.md       # IDE coding standards
├── README.md                         # User-facing quick start
└── sample.tex                        # Example LaTeX template
```

**Note on legacy files:** `core/orchestrator.py`, `core/resume_generator.py`, `core/agents/base.py`, and the `providers/` directory contain earlier non-agentic implementations. The current flow uses `core/graph.py` with LangChain ChatModel instances created by `core/model_factory.py`.

---

## 4. Data Flow

### 4.1 End-to-End Request Lifecycle

```
User (Streamlit)
  │
  │  HTTP POST /generate
  │  Body: { job_description, raw_experience, sample_latex, model config }
  ▼
FastAPI (app_server.py)
  │  1. Validates request via Pydantic
  │  2. Creates ChatModel instances via ModelFactory (one per agent)
  │  3. Builds and compiles LangGraph StateGraph
  │  4. Invokes graph with initial state
  ▼
LangGraph Pipeline (core/graph.py)
  │
  │  ┌─────────────┐
  │  │ parser_node  │  → Splits template into preamble, body, command cheatsheet
  │  └──────┬──────┘
  │         ▼
  │  ┌──────────────┐
  │  │ analyzer_node │  → Extracts skills, keywords, hidden needs, culture
  │  └──────┬───────┘
  │         ▼
  │  ┌──────────────┐
  │  │ strategy_node │  → Plans which experience to highlight and how
  │  └──────┬───────┘
  │         ▼
  │  ┌───────────────┐
  │  │ developer_node │  → Generates body-only LaTeX; reassembled with preamble
  │  └──────┬────────┘
  │         ▼
  │  ┌────────────────┐     ┌─── If invalid AND revision_count < 3:
  │  │ validator_node  │────►│    route back to developer_node with errors
  │  └────────────────┘     │
  │                         └─── If valid OR revision_count >= 3:
  │                              route to END
  ▼
FastAPI returns ResumeResponse
  │  { latex_code, job_analysis, strategy, is_valid, errors, revision_count }
  ▼
Streamlit displays results + download button
```

### 4.2 State Object

Defined in `core/state.py` as a `TypedDict`:

```python
class ResumeState(TypedDict):
    job_description: str          # Input: raw job posting text
    raw_experience: str           # Input: candidate's background
    sample_latex: str             # Input: LaTeX template to preserve
    template_preamble: str        # Parsed: verbatim preamble (preserved programmatically)
    template_body: str            # Parsed: original body (structural reference for LLM)
    command_cheatsheet: str       # Parsed: custom command signatures for LLM
    job_analysis: str             # Output of analyzer agent
    strategy_plan: str            # Output of strategist agent
    latex_code: str               # Output of developer agent (final or in-progress)
    compilation_errors: Annotated[list[str], operator.add]  # Accumulating error list
    revision_count: int           # How many developer attempts so far
    is_valid_latex: bool          # Whether latest LaTeX passed validation
```

The `compilation_errors` field uses `operator.add` annotation so LangGraph appends new errors rather than replacing.

---

## 5. Agent Details

### 5.1 JobAnalyzerAgent (`core/agents/analyzer.py`)

**Input:** `job_description` (string)
**Output:** Structured analysis with: CORE SKILLS, KEYWORDS, HIDDEN NEEDS, CULTURE VIBE
**Pattern:** `ChatPromptTemplate | ChatModel` chain, called with `ainvoke()`

### 5.2 StrategyAgent (`core/agents/strategist.py`)

**Input:** `job_analysis` + `raw_experience`
**Output:** Content strategy with: SUMMARY STRATEGY, EXPERIENCE SELECTION, BULLET POINT ANGLES, KEYWORD INTEGRATION
**Pattern:** Same chain pattern as analyzer

### 5.3 TemplateParser (`core/tools/template_parser.py`)

A purely programmatic step (no LLM) that runs before the agents. Splits the sample LaTeX into:
- **preamble:** Everything up to and including `\begin{document}` — preserved verbatim.
- **body:** Content between `\begin{document}` and `\end{document}` — used as structural reference for the LLM.
- **command_cheatsheet:** Human-readable list of custom command signatures extracted from `\newcommand`/`\renewcommand` definitions (e.g., `\resumeSubheading{arg1}{arg2}{arg3}{arg4}`).

### 5.4 LatexDeveloperAgent (`core/agents/developer.py`)

**Input:** `job_analysis` + `strategy_plan` + `template_body` + `command_cheatsheet` + `raw_experience` + optional `previous_errors`
**Output:** Complete LaTeX document (preamble reassembled programmatically)

The LLM generates **only the document body** — not the preamble, not `\begin{document}`, not `\end{document}`. It receives the command cheatsheet and sample body as context so it knows which custom commands to use and what structure to follow.

**Post-processing:**
1. Strip markdown code fences
2. If the LLM accidentally included preamble/boundaries, extract just the body portion
3. Call `TemplateParser.reassemble(preamble, body)` to produce the final LaTeX

This approach means the preamble is always correct (copied verbatim), and local/weaker models only need to produce content using the template's commands.

**Retry behavior:** When `previous_errors` is non-empty, they are included in the user prompt so the developer can fix specific issues.

---

## 6. Validation System

Validation happens in `validator_node` and consists of two checks run in sequence:

### 6.1 Syntax Validation (`core/tools/latex_validator.py`)

- Brace balance: count of `{` must equal count of `}`
- Environment pairing: every `\begin{X}` must have a matching `\end{X}`
- Markdown artifact detection: flags leftover ` ```latex ` blocks

### 6.2 Template Preservation (`core/tools/template_verifier.py`)

Lightweight check that the generated LaTeX is structurally consistent with the sample:
- **Document class:** Must match the sample (e.g., both use `article`)
- **Document boundaries:** Must contain `\begin{document}` and `\end{document}`

The verifier intentionally does **not** restrict packages, custom commands, or section structure — the LLM is free to adapt content as needed.

If either syntax or template checks fail, errors are collected into `compilation_errors` and `is_valid_latex` is set to `False`, triggering a retry (up to 3 total attempts).

---

## 7. Model Configuration

### 7.1 Simple Mode

All three agents use the same model:

```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "api_key": "sk-..."
}
```

### 7.2 Advanced Mode

Each agent gets independent configuration:

```json
{
  "analyzer_config":   { "provider": "openai",    "model": "gpt-3.5-turbo", "api_key": "..." },
  "strategist_config": { "provider": "anthropic",  "model": "claude-3-sonnet-20240229", "api_key": "..." },
  "developer_config":  { "provider": "openai",    "model": "gpt-4o", "api_key": "..." }
}
```

### 7.3 Supported Providers

| Provider | Models | API Key Required |
|----------|--------|-----------------|
| OpenAI | gpt-4o, gpt-4-turbo, gpt-3.5-turbo | Yes |
| Anthropic | claude-3-opus, claude-3-sonnet, claude-3-haiku | Yes |
| Google Gemini | gemini-pro, gemini-1.5-pro | Yes |
| Groq | llama3-70b, mixtral-8x7b | Yes |
| Ollama | Any locally pulled model | No (local) |

### 7.4 ModelFactory (`core/model_factory.py`)

Maps `(provider, model_name, api_key, temperature)` to a LangChain `BaseChatModel` instance. Uses `langchain-openai`, `langchain-anthropic`, `langchain-google-genai`, `langchain-groq`, or `langchain-ollama` depending on provider.

---

## 8. Creativity Levels

Defined in `core/prompts.py` but not currently exposed in the UI. Five levels:

| Level | Name | Temperature | Behavior |
|-------|------|-------------|----------|
| 1 | Conservative | 0.3 | Reorganize existing content, minimal rewording |
| 2 | Moderate | 0.5 | Light rewording, add keywords naturally |
| 3 | Balanced | 0.7 | Active tailoring, truthful reframing |
| 4 | Creative | 0.8 | Significant rewriting, emphasize transferable skills |
| 5 | Bold | 0.9 | Maximum adaptation, draw strong connections |

---

## 9. API Reference

### POST /generate

Accepts `ResumeRequest` (Pydantic model) with fields:
- `job_description` (str, required)
- `raw_experience` (str, required)
- `sample_latex` (str, required)
- `provider` (str, optional) — for simple mode
- `model` (str, optional) — for simple mode
- `api_key` (str, optional)
- `analyzer_config` (dict, optional) — for advanced mode
- `strategist_config` (dict, optional) — for advanced mode
- `developer_config` (dict, optional) — for advanced mode

Returns `ResumeResponse`:
- `latex_code` (str)
- `job_analysis` (str)
- `strategy` (str)
- `is_valid` (bool)
- `errors` (list[str])
- `revision_count` (int)

### GET /health

Returns `{"status": "healthy"}`.

---

## 10. Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Set API keys (or provide them in the UI)
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

# Start backend
uvicorn app_server:app --reload        # http://localhost:8000

# Start frontend (separate terminal)
streamlit run app.py                   # http://localhost:8501
```

---

## 11. Key Conventions for Contributors

- **Async-first:** All agent methods and graph nodes use `async def` / `ainvoke()`.
- **LangChain chains:** Agents follow the `ChatPromptTemplate | ChatModel` pattern.
- **State mutations:** Graph nodes return partial dicts; LangGraph merges them into state.
- **Error accumulation:** `compilation_errors` uses `operator.add` so errors append across retries.
- **No direct LLM calls:** Always go through `ModelFactory` → LangChain ChatModel.
- **Preamble preservation:** The template preamble is preserved programmatically — the LLM only generates the body.
- **Max 3 retries:** Hardcoded in `core/graph.py` conditional edge.
- **Linting:** Flake8 with 120-char line limit.

---

## 12. Known Limitations

- No persistent storage — results are ephemeral per session.
- No user authentication.
- Creativity levels exist in code but are not exposed in the UI.
- Retry limit (3) is hardcoded, not configurable.
- No built-in LaTeX-to-PDF compilation — users compile externally (e.g., Overleaf).
- Template verifier only checks document class and boundaries — does not enforce packages, sections, or custom commands.
