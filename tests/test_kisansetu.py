"""kisansetu test suite. Runs fully offline against the StubBackend."""

from __future__ import annotations

import json

from kisansetu import (
    Advisor,
    assess_urgency,
    classify_query,
    extract_crop,
    match_scheme,
)

# ---- classification --------------------------------------------------------


def test_classify_each_category():
    assert classify_query("brown rust spots and fungus on the wheat leaves") == "disease"
    assert classify_query("aphids and worms crawling over the plants") == "pest"
    assert classify_query("a hailstorm and flood flattened everything") == "weather"
    assert classify_query("how much water should I give the paddy") == "irrigation"
    assert classify_query("which fertilizer and how much urea to add") == "soil"
    assert classify_query("what is today's mandi price for the crop") == "market"
    assert classify_query("am I eligible for the pm-kisan subsidy") == "scheme"


def test_classify_no_keywords_is_general():
    assert classify_query("hello, I would like some advice") == "general"


def test_classify_priority_breaks_ties_toward_crop_threat():
    # one pest keyword + one market keyword -> pest wins on priority
    assert classify_query("aphid in the mandi") == "pest"


# ---- crop extraction -------------------------------------------------------


def test_extract_crop_english_and_hindi_aliases():
    assert extract_crop("white flies on my cotton") == "cotton"
    assert extract_crop("my paddy is not growing") == "rice"
    assert extract_crop("tamatar ke paude") == "tomato"


def test_extract_crop_none_when_absent():
    assert extract_crop("there is a problem in my field") is None


# ---- urgency ---------------------------------------------------------------


def test_urgency_high_for_pest_and_urgent_words():
    assert assess_urgency("aphids on cotton", "pest") == "high"
    assert assess_urgency("the whole field is dying", "general") == "high"


def test_urgency_medium_and_low():
    assert assess_urgency("today's mandi price", "market") == "medium"
    assert assess_urgency("eligibility for pm-kisan", "scheme") == "low"


# ---- scheme matching -------------------------------------------------------


def test_scheme_matches_category():
    assert "Soil Health Card" in match_scheme("soil", "urea dose")
    assert "Fasal Bima" in match_scheme("pest", "worms everywhere")


def test_scheme_credit_overrides_on_loan_words():
    assert "Kisan Credit Card" in match_scheme("soil", "I need a crop loan")


# ---- end-to-end advice -----------------------------------------------------


def test_advise_populates_all_fields():
    result = Advisor().advise("white insects are spreading on my cotton")
    assert result.category == "pest"
    assert result.crop == "cotton"
    assert result.urgency == "high"
    assert len(result.steps) >= 3
    assert "cotton" in result.summary
    assert result.scheme
    assert result.backend == "stub"


def test_default_backend_is_stub():
    assert Advisor().advise("how much water for paddy").backend == "stub"


def test_advice_is_deterministic():
    a = Advisor().advise("brown rust on the wheat")
    b = Advisor().advise("brown rust on the wheat")
    assert a.to_dict() == b.to_dict()


def test_to_dict_has_expected_keys():
    d = Advisor().advise("mandi price for onion").to_dict()
    for key in ("category", "crop", "urgency", "summary", "steps", "scheme", "backend"):
        assert key in d


# ---- audit log -------------------------------------------------------------


def test_audit_log_is_written_and_privacy_safe(tmp_path):
    audit = tmp_path / "audit.jsonl"
    Advisor(audit_path=str(audit)).advise(
        "my cotton has worms, call me at (555) 123-4567"
    )

    lines = audit.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])

    assert event["backend"] == "stub"
    assert event["category"] == "pest"
    assert event["crop"] == "cotton"
    assert event["urgency"] == "high"

    # privacy: the audit log must never carry the farmer's raw text
    assert "summary" not in event
    assert "query" not in event
    blob = json.dumps(event)
    assert "(555) 123-4567" not in blob
    assert "worms" not in blob
