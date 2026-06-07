"""Standard-library test suite for kisansetu.

This module is written with the built-in :mod:`unittest` framework only, so it
runs with zero third-party dependencies:

    python3 -m unittest discover -s tests

It complements ``tests/test_kisansetu.py`` (which uses pytest) by exercising the
same real code through the stdlib runner, and adds coverage for several edge
cases: empty input, the ``credit`` scheme override, audit-log appending,
``StubBackend`` formatting, and the public ``__all__`` surface.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

# Make the package importable when run from the repo root without an install
# (e.g. ``python3 -m unittest discover -s tests``).
_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import kisansetu  # noqa: E402
from kisansetu import (  # noqa: E402
    AdviceResult,
    Advisor,
    StubBackend,
    assess_urgency,
    classify_query,
    extract_crop,
    match_scheme,
)


class ClassifyTests(unittest.TestCase):
    def test_each_category(self) -> None:
        cases = {
            "brown rust spots and fungus on the wheat leaves": "disease",
            "aphids and worms crawling over the plants": "pest",
            "a hailstorm and flood flattened everything": "weather",
            "how much water should I give the paddy": "irrigation",
            "which fertilizer and how much urea to add": "soil",
            "what is today's mandi price for the crop": "market",
            "am I eligible for the pm-kisan subsidy": "scheme",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(classify_query(text), expected)

    def test_no_keywords_is_general(self) -> None:
        self.assertEqual(classify_query("hello, I would like some advice"), "general")

    def test_empty_string_is_general(self) -> None:
        self.assertEqual(classify_query(""), "general")

    def test_priority_breaks_ties_toward_crop_threat(self) -> None:
        # one pest keyword + one market keyword -> pest wins on priority.
        self.assertEqual(classify_query("aphid in the mandi"), "pest")

    def test_is_case_insensitive(self) -> None:
        self.assertEqual(classify_query("APHIDS ON THE COTTON"), "pest")


class ExtractCropTests(unittest.TestCase):
    def test_english_and_hindi_aliases(self) -> None:
        self.assertEqual(extract_crop("white flies on my cotton"), "cotton")
        self.assertEqual(extract_crop("my paddy is not growing"), "rice")
        self.assertEqual(extract_crop("tamatar ke paude"), "tomato")
        self.assertEqual(extract_crop("kapas me keede"), "cotton")

    def test_none_when_absent(self) -> None:
        self.assertIsNone(extract_crop("there is a problem in my field"))

    def test_empty_string_returns_none(self) -> None:
        self.assertIsNone(extract_crop(""))

    def test_word_boundary_avoids_substring_false_positive(self) -> None:
        # "scorn" contains "corn" (a maize alias) but is not a whole-word match.
        self.assertIsNone(extract_crop("do not scorn the harvest"))


class UrgencyTests(unittest.TestCase):
    def test_high_for_threat_categories(self) -> None:
        self.assertEqual(assess_urgency("aphids on cotton", "pest"), "high")
        self.assertEqual(assess_urgency("blight on the leaves", "disease"), "high")

    def test_urgent_words_force_high_regardless_of_category(self) -> None:
        self.assertEqual(assess_urgency("the whole field is dying", "general"), "high")
        self.assertEqual(assess_urgency("price spreading rapidly", "market"), "high")

    def test_medium_and_low(self) -> None:
        self.assertEqual(assess_urgency("today's mandi price", "market"), "medium")
        self.assertEqual(assess_urgency("eligibility for pm-kisan", "scheme"), "low")


class SchemeTests(unittest.TestCase):
    def test_matches_category(self) -> None:
        self.assertIn("Soil Health Card", match_scheme("soil", "urea dose"))
        self.assertIn("Fasal Bima", match_scheme("pest", "worms everywhere"))

    def test_credit_overrides_on_loan_words(self) -> None:
        self.assertIn("Kisan Credit Card", match_scheme("soil", "I need a crop loan"))
        self.assertIn("Kisan Credit Card", match_scheme("market", "how do I borrow money"))

    def test_unknown_category_falls_back_to_general(self) -> None:
        # A category not present in SCHEMES must not raise; it falls back.
        self.assertTrue(match_scheme("nonexistent-category", "plain question"))


class StubBackendTests(unittest.TestCase):
    def test_name(self) -> None:
        self.assertEqual(StubBackend().name, "stub")

    def test_includes_crop_phrase_when_crop_present(self) -> None:
        out = StubBackend().advise("q", category="pest", crop="cotton")
        self.assertIn("cotton", out)

    def test_omits_crop_phrase_when_crop_absent(self) -> None:
        out = StubBackend().advise("q", category="pest", crop=None)
        self.assertNotIn("None", out)

    def test_unknown_category_uses_general_template(self) -> None:
        out = StubBackend().advise("q", category="made-up", crop=None)
        self.assertTrue(out)


class AdviseEndToEndTests(unittest.TestCase):
    def test_populates_all_fields(self) -> None:
        result = Advisor().advise("white insects are spreading on my cotton")
        self.assertIsInstance(result, AdviceResult)
        self.assertEqual(result.category, "pest")
        self.assertEqual(result.crop, "cotton")
        self.assertEqual(result.urgency, "high")
        self.assertGreaterEqual(len(result.steps), 3)
        self.assertIn("cotton", result.summary)
        self.assertTrue(result.scheme)
        self.assertEqual(result.backend, "stub")
        self.assertEqual(result.language, "en")

    def test_default_backend_is_stub(self) -> None:
        self.assertEqual(Advisor().advise("how much water for paddy").backend, "stub")

    def test_advice_is_deterministic(self) -> None:
        a = Advisor().advise("brown rust on the wheat")
        b = Advisor().advise("brown rust on the wheat")
        self.assertEqual(a.to_dict(), b.to_dict())

    def test_steps_are_a_copy_not_shared_state(self) -> None:
        # Mutating one result's steps must not leak into the next call.
        first = Advisor().advise("aphids on cotton")
        first.steps.append("MUTATED")
        second = Advisor().advise("aphids on cotton")
        self.assertNotIn("MUTATED", second.steps)

    def test_per_call_language_override(self) -> None:
        result = Advisor(language="en").advise("paddy water", language="hi")
        self.assertEqual(result.language, "hi")

    def test_to_dict_has_expected_keys(self) -> None:
        d = Advisor().advise("mandi price for onion").to_dict()
        for key in (
            "category",
            "crop",
            "urgency",
            "summary",
            "steps",
            "scheme",
            "backend",
            "language",
        ):
            with self.subTest(key=key):
                self.assertIn(key, d)


class AuditLogTests(unittest.TestCase):
    def test_written_and_privacy_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audit = os.path.join(tmp, "audit.jsonl")
            Advisor(audit_path=audit).advise(
                "my cotton has worms, call me at (555) 123-4567"
            )

            with open(audit, encoding="utf-8") as fp:
                lines = fp.read().strip().splitlines()

            self.assertEqual(len(lines), 1)
            event = json.loads(lines[0])
            self.assertEqual(event["backend"], "stub")
            self.assertEqual(event["category"], "pest")
            self.assertEqual(event["crop"], "cotton")
            self.assertEqual(event["urgency"], "high")

            # Privacy: the audit log must never carry the farmer's raw text.
            self.assertNotIn("summary", event)
            self.assertNotIn("query", event)
            blob = json.dumps(event)
            self.assertNotIn("(555) 123-4567", blob)
            self.assertNotIn("worms", blob)

    def test_appends_across_calls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audit = os.path.join(tmp, "audit.jsonl")
            advisor = Advisor(audit_path=audit)
            advisor.advise("aphids on cotton")
            advisor.advise("today's mandi price for onion")

            with open(audit, encoding="utf-8") as fp:
                lines = fp.read().strip().splitlines()
            self.assertEqual(len(lines), 2)

    def test_no_audit_file_when_path_unset(self) -> None:
        # Should not raise and should not create any file when audit_path is None.
        result = Advisor().advise("aphids on cotton")
        self.assertEqual(result.category, "pest")


class PackageSurfaceTests(unittest.TestCase):
    def test_version_is_a_string(self) -> None:
        self.assertIsInstance(kisansetu.__version__, str)
        self.assertTrue(kisansetu.__version__)

    def test_public_names_are_exported(self) -> None:
        for name in ("Advisor", "AdviceResult", "StubBackend", "Backend"):
            with self.subTest(name=name):
                self.assertIn(name, kisansetu.__all__)
                self.assertTrue(hasattr(kisansetu, name))


if __name__ == "__main__":
    unittest.main()
