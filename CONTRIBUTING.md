# Contributing to Dynamic Resume Creator

## Development Workflow

1.  **Code Style**:
    *   Follow PEP 8 guidelines for Python code.
    *   Ensure all code is typed (mypy) and linted (flake8).
    *   Use `black` for formatting.

2.  **Project Structure**:
    *   New agents should go into `core/agents/`.
    *   New LLM providers should inherit from `providers.base.BaseProvider` and sit in `providers/`.

3.  **Testing**:
    *   Write unit tests for new agents and providers.
    *   Ensure existing tests pass before committing.

## Commit Messages
*   Use clear, descriptive commit messages.
*   Start with a verb (e.g., "Add", "Fix", "Update").
