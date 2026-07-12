"""Exercise 1 — a single Messages API call.

Run: python -m exercises.ex01_messages
"""

from exercises.config import MODEL, VISIBLE_THINKING, get_client, text_of


def ask(question: str, effort: str = "medium") -> str:
    """Send one question and return the answer text."""
    client = get_client()
    message = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        thinking=VISIBLE_THINKING,
        output_config={"effort": effort},
        system="You are a concise technical assistant.",
        messages=[{"role": "user", "content": question}],
    )
    return text_of(message)


if __name__ == "__main__":
    print(ask("In two sentences, what is prompt caching and when does it pay off?"))
