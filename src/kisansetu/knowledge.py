"""Deterministic knowledge base for kisansetu.

Everything here is keyless and offline: category keyword sets, a crop
dictionary (English plus common transliterated Hindi names so a farmer can
type either), per-category action steps, and the government scheme that fits
each kind of problem. The stub backend reasons entirely from these tables, so
the whole tool runs with no API key.
"""

from __future__ import annotations

# Category keyword sets. A query is classified by which set it hits most.
CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "disease": (
        "disease",
        "fungus",
        "fungal",
        "blight",
        "rust",
        "rot",
        "wilt",
        "mildew",
        "mosaic",
        "spots",
        "lesion",
        "bimari",
        "rog",
    ),
    "pest": (
        "pest",
        "insect",
        "bug",
        "locust",
        "aphid",
        "borer",
        "caterpillar",
        "worm",
        "mite",
        "whitefly",
        "termite",
        "keeda",
        "keede",
        "sundi",
    ),
    "weather": (
        "weather",
        "storm",
        "frost",
        "heatwave",
        "heat wave",
        "flood",
        "hail",
        "cyclone",
        "drought",
        "unseasonal",
        "mausam",
    ),
    "irrigation": (
        "water",
        "irrigation",
        "irrigate",
        "drip",
        "sprinkler",
        "canal",
        "borewell",
        "watering",
        "pani",
        "sinchai",
    ),
    "soil": (
        "soil",
        "fertilizer",
        "fertiliser",
        "nutrient",
        "nitrogen",
        "urea",
        "compost",
        "manure",
        "ph ",
        "acidic",
        "mitti",
        "khaad",
        "khad",
    ),
    "market": (
        "price",
        "sell",
        "selling",
        "market",
        "mandi",
        "msp",
        "rate",
        "profit",
        "buyer",
        "bhav",
        "daam",
    ),
    "scheme": (
        "scheme",
        "subsidy",
        "loan",
        "insurance",
        "yojana",
        "sarkar",
        "government",
        "kcc",
        "credit card",
        "pm-kisan",
        "pmkisan",
        "benefit",
    ),
}

# Classification priority. On a keyword-count tie, earlier wins — urgent,
# crop-threatening categories outrank informational ones.
PRIORITY: tuple[str, ...] = (
    "disease",
    "pest",
    "weather",
    "irrigation",
    "soil",
    "market",
    "scheme",
)

# Canonical crop -> alternate names a farmer might type (incl. transliterated Hindi).
CROPS: dict[str, tuple[str, ...]] = {
    "rice": ("paddy", "dhan", "chawal"),
    "wheat": ("gehu", "gehun"),
    "cotton": ("kapas",),
    "sugarcane": ("ganna",),
    "maize": ("corn", "makka", "makai"),
    "soybean": ("soya", "soyabean"),
    "tomato": ("tamatar",),
    "potato": ("aloo", "alu"),
    "onion": ("pyaaz", "pyaz"),
    "chilli": ("chili", "mirch", "mirchi"),
    "groundnut": ("peanut", "moongphali"),
    "mustard": ("sarson",),
    "banana": ("kela",),
    "mango": ("aam",),
}

# Words that force HIGH urgency regardless of category.
URGENT_WORDS: tuple[str, ...] = (
    "urgent",
    "emergency",
    "dying",
    "died",
    "spreading",
    "spread fast",
    "rapidly",
    "immediately",
    "whole field",
    "entire field",
    "everywhere",
    "all my",
    "overnight",
    "turning yellow",
    "wiped out",
)

# Government scheme that fits each problem category.
SCHEMES: dict[str, str] = {
    "pest": "Pradhan Mantri Fasal Bima Yojana — crop insurance for pest/disease loss (pmfby.gov.in)",
    "disease": "Pradhan Mantri Fasal Bima Yojana — crop insurance for pest/disease loss (pmfby.gov.in)",
    "weather": "Pradhan Mantri Fasal Bima Yojana — weather-loss cover (pmfby.gov.in)",
    "irrigation": "Pradhan Mantri Krishi Sinchayee Yojana — irrigation support (pmksy.gov.in)",
    "soil": "Soil Health Card Scheme — free soil testing and advice (soilhealth.dac.gov.in)",
    "market": "e-NAM national market and MSP procurement (enam.gov.in)",
    "scheme": "PM-KISAN income support — Rs 6,000/year to eligible farmers (pmkisan.gov.in)",
    "general": "PM-KISAN income support — Rs 6,000/year to eligible farmers (pmkisan.gov.in)",
    "credit": "Kisan Credit Card (KCC) — low-interest crop credit through your bank",
}

# Plain-language one-liner per category. {crop} is filled with " on your <crop>"
# when a crop is detected, else an empty string.
SUMMARY: dict[str, str] = {
    "pest": "This looks like a pest problem{crop}. Act quickly, because pests spread fast. Confirm the pesticide and dose with your local Krishi Vigyan Kendra (KVK) before you spray.",
    "disease": "This looks like a plant disease{crop}. Remove the worst-affected plants early so it does not spread, and get the right fungicide from your KVK.",
    "weather": "Weather damage{crop} can usually be claimed. Photograph the damage now and report the loss within 72 hours so your insurance claim is valid.",
    "irrigation": "This is a water/irrigation question{crop}. Match watering to the crop's stage and avoid the midday heat. Drip or sprinkler systems qualify for a government subsidy.",
    "soil": "This is a soil/nutrient question{crop}. Test the soil before adding fertilizer so you apply only what is missing. The Soil Health Card test is free.",
    "market": "This is a price/market question{crop}. Check today's mandi rate on e-NAM and compare it with the MSP before you sell.",
    "scheme": "You are asking about a government scheme{crop}. The most relevant one is listed below with its official website.",
    "general": "Here is general guidance{crop}. For specifics, your nearest Krishi Vigyan Kendra (KVK) gives free, local advice.",
}

# Deterministic action checklist per category.
STEPS: dict[str, list[str]] = {
    "pest": [
        "Check the underside of affected leaves to identify the pest.",
        "Remove and destroy badly infested plants to slow the spread.",
        "Ask your nearest KVK for an approved pesticide and the correct dose.",
        "Spray in the early morning or evening, never in peak heat.",
    ],
    "disease": [
        "Pull out and burn the worst-affected plants early.",
        "Avoid watering the leaves directly; keep water at the roots.",
        "Get the right fungicide and dose from your KVK before spraying.",
        "Rotate to a different crop next season to break the disease cycle.",
    ],
    "weather": [
        "Photograph the damaged crop today, with the whole field visible.",
        "Report the loss to your insurer or bank within 72 hours.",
        "Keep your policy number and sowing records ready for the claim.",
        "Drain standing water quickly to save the surviving plants.",
    ],
    "irrigation": [
        "Water early morning or evening to cut evaporation loss.",
        "Match the amount to the crop's growth stage, not a fixed schedule.",
        "Consider drip or sprinkler irrigation for a subsidy and water savings.",
        "Mulch the soil to hold moisture longer between waterings.",
    ],
    "soil": [
        "Get a free Soil Health Card test before buying any fertilizer.",
        "Apply only the nutrients the test says are missing.",
        "Add compost or farmyard manure to rebuild organic matter.",
        "Avoid over-applying urea; it harms the soil and your budget.",
    ],
    "market": [
        "Check today's mandi price for your crop on the e-NAM portal.",
        "Compare it against the official MSP before deciding to sell.",
        "Grade and clean the produce to fetch a higher rate.",
        "Sell through e-NAM or an FPO to reach more buyers.",
    ],
    "scheme": [
        "Confirm your eligibility on the official scheme website below.",
        "Keep your Aadhaar, land records, and bank passbook ready.",
        "Apply online or at your nearest Common Service Centre (CSC).",
        "Note the application ID so you can track the status.",
    ],
    "general": [
        "Write down exactly what you are seeing in the field.",
        "Visit or call your nearest Krishi Vigyan Kendra (KVK) for free advice.",
        "Take clear photos of the crop to show the expert.",
    ],
}
