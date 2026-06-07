# kisansetu 🌾

A farmer types a question in plain words — *"white insects spreading on my
cotton"* — and `kisansetu` triages it into a **category**, the **crop**, how
**urgent** it is, a **plain-language answer**, a concrete **action checklist**,
and the **government scheme** that fits. It runs **offline with no API key**, so
it works on a cheap phone with a patchy connection.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-unittest%20%2F%20pytest-blueviolet.svg)](tests/)
[![Typed](https://img.shields.io/badge/typed-py.typed-informational.svg)](src/kisansetu/py.typed)

> Built for the Rising India theme: practical AI for agriculture and the
> last mile, where connectivity and API budgets are scarce.

---

## Why

India has ~120 million farmers and a tiny number of extension officers. The
advice exists — which pesticide, when to irrigate, which subsidy — but it is
buried in PDFs, English, and government portals. `kisansetu` is the bridge
(*setu*): one plain question in, one clear answer out, with the right scheme
attached. No app store, no key, works offline.

- **Understands plain questions** in English or common transliterated Hindi
  crop names (*paddy*, *dhan*, *kapas*, *tamatar* …).
- **Triages** into pest, disease, weather, irrigation, soil, market, or scheme.
- **Flags urgency** so a spreading pest jumps the queue over a price question.
- **Gives a checklist**, not a wall of text — what to do, in order.
- **Routes to the right scheme** (PMFBY, PM-KISAN, Soil Health Card, e-NAM, KCC …)
  with the official website.
- **Privacy-safe audit log** that records categories and counts, never the
  farmer's words.

## Quickstart (no API key)

```bash
pip install -e .
python examples/demo.py
```

```python
from kisansetu import Advisor

result = Advisor().advise("white insects are spreading on my cotton")

print(result.category)   # pest
print(result.crop)       # cotton
print(result.urgency)    # high
print(result.summary)    # plain-language answer
for step in result.steps:
    print("-", step)
print(result.scheme)     # Pradhan Mantri Fasal Bima Yojana ...
```

The default `StubBackend` reasons entirely from a built-in knowledge base
(keyword classifier + crop dictionary + scheme map), so it gives a real, useful
answer with zero setup. Swap in an LLM backend for richer, conversational advice.

## Dashboard

```bash
pip install -e ".[dashboard]"
streamlit run app.py
```

Tap an example or type your own question; see the category, crop, urgency, plain
answer, checklist, and scheme.

## LLM backends

All optional and lazily imported — the core install pulls **zero** vendor deps.

| Backend            | Install        | Needs                 |
| ------------------ | -------------- | --------------------- |
| `StubBackend`      | (built in)     | nothing — runs offline|
| `GeminiBackend`    | `.[gemini]`    | `GEMINI_API_KEY`      |
| `AnthropicBackend` | `.[anthropic]` | `ANTHROPIC_API_KEY`   |
| `OllamaBackend`    | `.[ollama]`    | a local Ollama server |

```python
from kisansetu import Advisor, GeminiBackend

result = Advisor(backend=GeminiBackend()).advise("how much urea for my wheat?")
```

The triage (category, crop, urgency, steps, scheme) is always deterministic and
keyless; only the conversational `summary` changes when you plug in an LLM.

## How it works

```
farmer's question
   │
   ├─► classify   → category   (most-hit keyword set, ties favor crop threats)
   ├─► extract    → crop        (English + Hindi aliases)
   ├─► assess     → urgency      (high / medium / low)
   ├─► match      → scheme       (PMFBY / PM-KISAN / Soil Health Card / e-NAM / KCC)
   └─► advise     → summary      (Stub template, or an LLM)
                  → steps        (deterministic checklist per category)
```

## Audit (privacy-safe)

```python
Advisor(audit_path="audit.jsonl").advise("worms on my cotton")
# {"ts":..., "backend":"stub", "category":"pest", "crop":"cotton",
#  "urgency":"high", "scheme_matched":true, "steps":4}
```

The log stores categories and counts for monitoring — never the farmer's raw
question.

## Tests

The fastest way needs **no install and no third-party packages** — the
standard-library suite runs against a source checkout directly:

```bash
python3 -m unittest discover -s tests
```

A pytest suite is also provided (it adds the `tmp_path` fixture for the audit
test):

```bash
pip install -e ".[dev]"
pytest
```

Both suites run fully offline against the stub backend. CI byte-compiles every
source file and runs the stdlib suite on Python 3.10–3.13.

## License

MIT — see [LICENSE](LICENSE).
