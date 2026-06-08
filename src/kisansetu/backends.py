"""Advice backends. A backend turns a triaged farmer query into a plain answer.

`StubBackend` is deterministic and dependency-free: it fills the plain-language
template for the detected category, so the demo and tests run with no API key.
The LLM backends (`GeminiBackend`, `AnthropicBackend`, `OllamaBackend`) are thin
and import their SDK lazily, so installing kisansetu core never pulls a vendor
dependency.

Every backend implements one method:

    advise(query, *, category, crop, language) -> str
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .knowledge import SUMMARY


@runtime_checkable
class Backend(Protocol):
    name: str

    def advise(
        self, query: str, *, category: str, crop: str | None, language: str
    ) -> str: ...


class StubBackend:
    """Deterministic advisor. No network, no key.

    Fills the plain-language summary template for the detected category and
    crop. Good enough to give a real, useful answer in the demo; swap in an LLM
    backend for richer, conversational advice.
    """

    name = "stub"

    def advise(
        self,
        query: str,
        *,
        category: str,
        crop: str | None = None,
        language: str = "en",
    ) -> str:
        crop_phrase = f" on your {crop}" if crop else ""
        template = SUMMARY.get(category, SUMMARY["general"])
        return template.format(crop=crop_phrase)


_PROMPT = (
    "You are an agricultural extension advisor for small farmers in India. "
    'A farmer asked: "{query}". This has been triaged as a {category} issue'
    "{crop_part}. Give short, practical advice in plain {language} at a grade-6 "
    "reading level. Use simple words and at most 4 sentences. Do not invent "
    "chemical brand names; tell them to confirm with their local KVK. Return "
    "only the advice."
)


def _format_prompt(query: str, category: str, crop: str | None, language: str) -> str:
    crop_part = f" affecting their {crop}" if crop else ""
    return _PROMPT.format(
        query=query, category=category, crop_part=crop_part, language=language
    )


class GeminiBackend:
    """Google Gemini backend. Requires `google-genai` and GEMINI_API_KEY."""

    name = "gemini"

    def __init__(self, model: str = "gemini-2.5-flash", api_key: str | None = None):
        from google import genai  # lazy import

        import os

        self._client = genai.Client(api_key=api_key or os.environ["GEMINI_API_KEY"])
        self._model = model

    def advise(
        self,
        query: str,
        *,
        category: str,
        crop: str | None = None,
        language: str = "en",
    ) -> str:
        prompt = _format_prompt(query, category, crop, language)
        resp = self._client.models.generate_content(model=self._model, contents=prompt)
        return (resp.text or "").strip()


class AnthropicBackend:
    """Anthropic Claude backend. Requires `anthropic` and ANTHROPIC_API_KEY."""

    name = "anthropic"

    def __init__(self, model: str = "claude-sonnet-4-6", api_key: str | None = None):
        import anthropic  # lazy import

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def advise(
        self,
        query: str,
        *,
        category: str,
        crop: str | None = None,
        language: str = "en",
    ) -> str:
        prompt = _format_prompt(query, category, crop, language)
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(
            block.text for block in msg.content if block.type == "text"
        ).strip()


class OllamaBackend:
    """Local Ollama backend. Requires a running ollama server. No key."""

    name = "ollama"

    def __init__(self, model: str = "llama3.2", host: str = "http://localhost:11434"):
        self._model = model
        self._host = host.rstrip("/")

    def advise(
        self,
        query: str,
        *,
        category: str,
        crop: str | None = None,
        language: str = "en",
    ) -> str:
        import httpx  # lazy import

        prompt = _format_prompt(query, category, crop, language)
        resp = httpx.post(
            f"{self._host}/api/generate",
            json={"model": self._model, "prompt": prompt, "stream": False},
            timeout=120.0,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
