# GitHub Copilot Instructions

You are an expert Python developer working on a "Dynamic Resume Creator" project. This project uses a **LangGraph-based agentic workflow** served via **FastAPI** to analyze and generate resumes.

## Project Structure
- **app_server.py**: The FastAPI entry point (API Layer).
- **app_ui.py**: The Streamlit frontend (Presentation Layer).
- **core/**: Contains the business logic.
  - **graph.py**: Defines the LangGraph StateGraph, Nodes, and Edges.
  - **state.py**: Defines the `ResumeState` TypedDict.
  - **agents/**: LangChain-based agent implementations.
  - **tools/**: Custom tools (e.g., LaTeX compiler/validator).
  - **model_factory.py**: Factory to instantiate LangChain ChatModels (OpenAI, Anthropic, etc.).

## Coding Standards

### Python
- **Type Hinting**: All function signatures must have type hints. Use `typing` (TypedDict, Annotated) and standard types.
- **Async/Await**: The core system is **async-first**. Use `async def` for FastAPI routes and LangGraph nodes.
- **Pydantic**: Use Pydantic V2 models for all API request/response validation.

### Architecture
- **LangGraph**: ALL orchestration logic goes into `core/graph.py`. Do NOT write linear imperative scripts; use Nodes and Edges.
- **LangChain**: Use standard LangChain integration packages (`langchain-openai`, `langchain-anthropic`). Do NOT write custom HTTP wrappers for LLMs.
- **Separation of Concerns**: 
  - The UI (`app_ui.py`) should NEVER import from `core` directly. It must communicate via HTTP requests to `app_server.py`.
  - Agents should operate on the `ResumeState` and return state updates.

## Behavior
- Prioritize **reliability**. When agents generate code (LaTeX), assume it will fail and provide a feedback loop (compiler tool) to correct it.
- Use `TypedDict` for graph state to ensure type safety between nodes.
- Ensure all environment variables (API keys) are handled securely via `pydantic-settings` or `os.environ`.
