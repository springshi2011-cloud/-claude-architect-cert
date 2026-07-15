import pytest
from greetings import greet


def test_defaults_to_french():
    assert greet("Marie") == "Bonjour, Marie !"


def test_english_is_available():
    assert greet("Marie", lang="en") == "Hello, Marie!"


def test_name_is_trimmed():
    assert greet("  Léa  ") == "Bonjour, Léa !"


def test_blank_name_is_rejected():
    with pytest.raises(ValueError, match="must not be blank"):
        greet("   ")


def test_unsupported_language_is_rejected():
    with pytest.raises(ValueError, match="unsupported language"):
        greet("Marie", lang="de")
