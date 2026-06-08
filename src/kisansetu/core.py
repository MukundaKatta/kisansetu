"""kisansetu core: triage a farmer's free-text question into a category, the
crop it is about, how urgent it is, a plain-language answer, a concrete action
checklist, and the government scheme that fits.

    from kisansetu import Advisor
    result = Advisor().advise("white insects all over my cotton leaves")
    print(result.category, result.urgency)
    print(result.summary)
    for step in result.steps:
        print("-", step)
    print(result.scheme)
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import asdict, dataclass, field

from .backends import Backend, StubBackend
from .knowledge import (
    CATEGORY_KEYWORDS,
    CROPS,
    PRIORITY,
    SCHEMES,
    STEPS,
    URGENT_WORDS,
)

# ---- triage primitives -----------------------------------------------------


def classify_query(text: str) -> str:
    """Pick the category whose keyword set the query hits most.

    Ties break by PRIORITY order, so a crop-threatening issue (disease, pest)
    outranks an informational one. No keyword hit at all -> "general".
    """
    low = text.lower()
    scores = {
        cat: sum(1 for kw in kws if kw in low) for cat, kws in CATEGORY_KEYWORDS.items()
    }
    best = max(PRIORITY, key=lambda c: (scores[c], -PRIORITY.index(c)))
    return best if scores[best] > 0 else "general"


def extract_crop(text: str) -> str | None:
    """Return the canonical English crop name mentioned, or None.

    Matches English names and common transliterated Hindi names.
    """
    low = text.lower()
    for crop, aliases in CROPS.items():
        for name in (crop, *aliases):
            if re.search(rf"\b{re.escape(name)}\b", low):
                return crop
    return None


def assess_urgency(text: str, category: str) -> str:
    """One of "high", "medium", "low"."""
    low = text.lower()
    if any(word in low for word in URGENT_WORDS):
        return "high"
    if category in ("pest", "disease", "weather"):
        return "high"
    if category in ("irrigation", "soil", "market"):
        return "medium"
    return "low"


def match_scheme(category: str, text: str) -> str:
    """The government scheme that best fits this query."""
    low = text.lower()
    if any(word in low for word in ("loan", "credit", "kcc", "borrow")):
        return SCHEMES["credit"]
    return SCHEMES.get(category, SCHEMES["general"])


# ---- result ----------------------------------------------------------------


@dataclass
class AdviceResult:
    category: str
    crop: str | None
    urgency: str
    summary: str
    steps: list[str]
    scheme: str
    backend: str
    language: str

    def to_dict(self) -> dict:
        return asdict(self)


# ---- advisor ---------------------------------------------------------------


@dataclass
class Advisor:
    """Configure once, reuse. Defaults to the keyless StubBackend so the whole
    pipeline runs offline."""

    backend: Backend = field(default_factory=StubBackend)
    language: str = "en"
    audit_path: str | None = None

    def advise(self, query: str, *, language: str | None = None) -> AdviceResult:
        lang = language or self.language

        category = classify_query(query)
        crop = extract_crop(query)
        urgency = assess_urgency(query, category)
        scheme = match_scheme(category, query)
        summary = self.backend.advise(
            query, category=category, crop=crop, language=lang
        )

        result = AdviceResult(
            category=category,
            crop=crop,
            urgency=urgency,
            summary=summary,
            steps=list(STEPS.get(category, STEPS["general"])),
            scheme=scheme,
            backend=getattr(self.backend, "name", type(self.backend).__name__),
            language=lang,
        )
        self._audit(result)
        return result

    def _audit(self, result: AdviceResult) -> None:
        """Append one privacy-safe JSONL line. Never logs the farmer's text."""
        if not self.audit_path:
            return
        os.makedirs(
            os.path.dirname(os.path.abspath(self.audit_path)) or ".", exist_ok=True
        )
        event = {
            "ts": round(time.time(), 3),
            "backend": result.backend,
            "category": result.category,
            "crop": result.crop,
            "urgency": result.urgency,
            "scheme_matched": bool(result.scheme),
            "steps": len(result.steps),
        }
        with open(self.audit_path, "a", encoding="utf-8") as fp:
            fp.write(json.dumps(event, separators=(",", ":")) + "\n")
