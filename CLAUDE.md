# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Hands-on Claude API exercises for AI Architect certification prep. Python, `anthropic` SDK, pytest.

## Language

Respond in **English**. This is the default for the whole repository.

Subdirectories may override it with their own `CLAUDE.md` — when working on files under such a
directory, the more specific file wins. See `module-a/CLAUDE.md`.

## Commands

```sh
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"   # setup

.venv/bin/pytest                          # offline tests (default; no API key needed)
.venv/bin/pytest -m live                  # smoke tests against the real API
.venv/bin/pytest tests/test_config.py::test_text_of_skips_non_text_blocks   # single test
.venv/bin/ruff check .                    # lint

.venv/bin/python -m exercises.ex01_messages   # run an exercise (ex01..ex04)
```

## Architecture

`src/exercises/config.py` is the single place that pins the model and request defaults —
`MODEL`, `ADAPTIVE_THINKING`, `VISIBLE_THINKING`, `get_client()`, and `text_of()`. Every
exercise imports from it instead of constructing its own client or repeating a model string.
Change the model in one place, not five.

`text_of(message)` exists because `message.content` is a list of blocks that can include
`thinking` and `tool_use` alongside `text` — indexing `content[0].text` is not safe.

Exercises `ex01`–`ex04` are independent, each a runnable `__main__` plus importable functions
so tests can call them: single call, streaming, tool use, structured output.

## API constraints this code is built around

These return a **400** on `claude-opus-4-8` and are load-bearing to how the code is written —
do not reintroduce them:

- `thinking: {"type": "enabled", "budget_tokens": N}` — removed. Use `{"type": "adaptive"}`
  and control depth with `output_config: {"effort": ...}`.
- `temperature`, `top_p`, `top_k` — removed. Steer with prompting.
- Assistant-turn prefill (a trailing `{"role": "assistant"}` message) — removed. Use
  `messages.parse()` with a Pydantic model (see `ex04_structured.py`).

Two silent behaviors, not errors:

- Omitting `thinking` runs with thinking **off**; it must be set explicitly.
- `thinking.display` defaults to `"omitted"`, which streams thinking blocks whose text is an
  empty string. `VISIBLE_THINKING` sets `"summarized"` to get readable reasoning back.

`tests/test_ex01_messages.py` asserts the outgoing request shape against all of the above, so
a regression fails offline rather than costing an API round trip.

## Testing

Offline tests mock the client (`monkeypatch` over `get_client`) and run with no credentials —
keep it that way, so the default `pytest` run stays free and fast. Anything hitting the real
API goes behind `@pytest.mark.live`, which `addopts` deselects by default.
