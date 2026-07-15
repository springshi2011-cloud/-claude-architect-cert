"""Bilingual greeting, defaulting to French to match this module's language override."""


GREETINGS = {
    "fr": "Bonjour, {name} !",
    "en": "Hello, {name}!",
}


def greet(name: str, lang: str = "fr") -> str:
    """Return a greeting for ``name`` in the given language.

    Args:
        name: Who to greet.
        lang: Language code; one of ``GREETINGS``. Defaults to French.

    Raises:
        ValueError: If ``name`` is blank or ``lang`` is unsupported.
    """
    if not name.strip():
        raise ValueError("name must not be blank")
    if lang not in GREETINGS:
        raise ValueError(f"unsupported language {lang!r}; expected one of {sorted(GREETINGS)}")
    return GREETINGS[lang].format(name=name.strip())
