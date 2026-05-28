# kisansetu — submission copy

**Repo:** https://github.com/MukundaKatta/kisansetu

**Target event:** Rising India Hackathon 1.0 (NIT Nagpur)

**Tagline:** Offline first-response advisory for farmer questions, in plain language.

## Short description

Takes a farmer's question in English or transliterated Hindi, classifies it,
detects the crop, judges urgency, returns concrete next steps, and matches the
right government scheme (PMFBY, PM-KISAN, Soil Health Card, KCC credit, e-NAM).
Runs with no API key so it works on a weak connection.

## Inspiration

A farmer with a sick crop and a weak connection needs a fast, plain answer and
the right government scheme, not a chatbot that falls over without the cloud.

## What it does

Takes a farmer's question in English or transliterated Hindi, sorts it (disease,
pest, weather, irrigation, soil, market price, scheme), detects the crop, judges
urgency, returns concrete next steps, and matches the right government scheme
(PMFBY, PM-KISAN, Soil Health Card, KCC credit, e-NAM). It runs with no API key
so it still works on a weak connection.

## How we built it

A deterministic knowledge base keyed on Indian crops and Hindi terms, a keyword
classifier with priority tie-breaks, urgency rules, a scheme matcher, optional
LLM backends for nicer phrasing, and a privacy-safe audit log that never stores
the raw question.

## Challenges we ran into

Handling transliterated Hindi like keeda, pani, mitti, and mandi, plus crop
aliases such as paddy, dhan, and chawal all mapping to rice. We also had to
break ties cleanly when a question hits more than one category.

## Accomplishments we're proud of

It's useful with no key and no network, it's grounded in real central-government
schemes rather than generic advice, and the logging is privacy-safe by design.

## What we learned

For rural tooling, offline-first is the requirement, not a nice-to-have.

## What's next

District-level KVK contact lookup, voice input, and more regional languages.

## Tech tags

python, agritech, agriculture, india, farmer-advisory, government-schemes,
offline-first, hindi, classification, streamlit, mit
