# Claude AI Architect Certification

Hands-on Claude API exercises for AI Architect certification prep.

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
export ANTHROPIC_API_KEY=sk-ant-...
```

## Exercises

Each module in `src/exercises/` is runnable on its own:

```sh
.venv/bin/python -m exercises.ex01_messages    # single Messages API call
.venv/bin/python -m exercises.ex02_streaming   # streaming + final message
.venv/bin/python -m exercises.ex03_tool_use    # tool runner drives the agentic loop
.venv/bin/python -m exercises.ex04_structured  # structured output into a Pydantic model
```

## Tests

```sh
.venv/bin/pytest              # offline tests only (no API key needed)
.venv/bin/pytest -m live      # smoke tests against the real API
.venv/bin/ruff check .
```
