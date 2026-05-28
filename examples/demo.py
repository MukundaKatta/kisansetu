"""kisansetu demo — runs offline, no API key required.

    python examples/demo.py

Triages a handful of real farmer questions: category, crop, urgency, a plain
answer, the action checklist, and the government scheme that fits.
"""

from __future__ import annotations

from kisansetu import Advisor

QUERIES = [
    "White insects are spreading fast on my cotton leaves, what do I do?",
    "Brown rust spots and fungus on the wheat, getting worse every day.",
    "How much water should I give my paddy at flowering stage?",
    "What is today's mandi price for onion and should I sell now?",
    "Am I eligible for the PM-Kisan subsidy and how do I apply?",
]


def main() -> None:
    advisor = Advisor()
    for query in QUERIES:
        result = advisor.advise(query)
        print("=" * 72)
        print("Q:", query)
        print("-" * 72)
        crop = result.crop or "—"
        print(f"category: {result.category}   crop: {crop}   urgency: {result.urgency}")
        print()
        print(result.summary)
        print()
        print("What to do:")
        for step in result.steps:
            print(f"  [ ] {step}")
        print()
        print("Scheme:", result.scheme)
        print()


if __name__ == "__main__":
    main()
