# LLM-Context Development Guide

## Build/Test/Lint Commands
- Build: `uv build`
- Run Tests: `uv run pytest tests/`
- Run Single Test: `uv run pytest tests/test_file.py::test_name -v`
- Code Linting: `ruff check .`
- Type Checking: `mypy src/`

## Code Style Guidelines
- Line Length: 100 characters max
- Python Version: 3.10+, targeting 3.13
- Import Order: standard library, third-party, local (using isort)
- Type Hints: Required, with `warn_return_any = true`
- Error Handling: Use custom exceptions from `exceptions.py`
- Naming: Snake case for functions/variables, PascalCase for classes
- Documentation: Docstrings for public functions and classes
- Code Structure: Small, focused modules with clear responsibilities
- Config Format: YAML (converted from TOML in v0.2.9)

## Repository Structure
- `src/llm_context/`: Main package code
- `tests/`: Test files (prefix with `test_`)
- `.llm-context/`: Configuration directory
- `docs/`: Documentation files