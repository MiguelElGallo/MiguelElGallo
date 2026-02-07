# Copilot Instructions

## Project structure

- The main project code lives in `update_readme/src/`.
- Tests live in `update_readme/tests/`.
- The project uses `uv` as the package manager with `pyproject.toml`.

## After every code change

You **must** run the following checks from the `update_readme/` directory and fix any issues before considering the task done:

1. **Lint & format with ruff:**
   ```bash
   cd update_readme && uv run ruff check . && uv run ruff format --check .
   ```
   Fix any issues with `uv run ruff check --fix .` and `uv run ruff format .`.

2. **Type-check with ty:**
   ```bash
   cd update_readme && uv run ty check src/
   ```

3. **Run tests:**
   ```bash
   cd update_readme && uv run pytest
   ```

All three must pass with zero errors before the change is complete.
