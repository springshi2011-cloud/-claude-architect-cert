"""Exercise 2 — streaming, and why large max_tokens requires it.

A non-streaming request with a large max_tokens can exceed the SDK's HTTP
timeout; streaming keeps the connection fed. `get_final_message()` still hands
back the complete Message once the stream drains.

Run: python -m exercises.ex02_streaming
"""

from collections.abc import Iterator

import anthropic

from exercises.config import MODEL, VISIBLE_THINKING, get_client


def stream_text(prompt: str) -> Iterator[str]:
    """Yield text deltas as they arrive."""
    client = get_client()
    with client.messages.stream(
        model=MODEL,
        max_tokens=64000,
        thinking=VISIBLE_THINKING,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        yield from stream.text_stream


def stream_and_collect(prompt: str) -> anthropic.types.Message:
    """Stream to stdout, then return the accumulated final message."""
    client = get_client()
    with client.messages.stream(
        model=MODEL,
        max_tokens=64000,
        thinking=VISIBLE_THINKING,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for chunk in stream.text_stream:
            print(chunk, end="", flush=True)
        print()
        return stream.get_final_message()


if __name__ == "__main__":
    final = stream_and_collect("Explain the tradeoff between effort levels in three bullets.")
    print(f"\n[input {final.usage.input_tokens} / output {final.usage.output_tokens} tokens]")
