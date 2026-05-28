"""kisansetu — triage a farmer's question into a category, the crop, how urgent
it is, a plain-language answer, an action checklist, and the right government
scheme. Runs offline with a keyless deterministic backend."""

from __future__ import annotations

from .backends import (
    AnthropicBackend,
    Backend,
    GeminiBackend,
    OllamaBackend,
    StubBackend,
)
from .core import (
    AdviceResult,
    Advisor,
    assess_urgency,
    classify_query,
    extract_crop,
    match_scheme,
)

__version__ = "0.1.0"

__all__ = [
    "Advisor",
    "AdviceResult",
    "classify_query",
    "extract_crop",
    "assess_urgency",
    "match_scheme",
    "Backend",
    "StubBackend",
    "GeminiBackend",
    "AnthropicBackend",
    "OllamaBackend",
    "__version__",
]
