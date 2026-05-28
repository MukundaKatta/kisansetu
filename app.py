"""kisansetu dashboard — ask a farming question, get a plain answer.

    pip install -e ".[dashboard]"
    streamlit run app.py

Runs offline against the keyless stub backend by default. Swap in Gemini /
Anthropic / Ollama for richer, conversational advice.
"""

from __future__ import annotations

import streamlit as st

from kisansetu import Advisor

EXAMPLES = [
    "White insects are spreading fast on my cotton leaves.",
    "Brown rust spots and fungus on the wheat.",
    "How much water should I give my paddy?",
    "What is today's mandi price for onion?",
    "Am I eligible for the PM-Kisan subsidy?",
]

_URGENCY_COLOR = {"high": "🔴 high", "medium": "🟠 medium", "low": "🟢 low"}

st.set_page_config(page_title="kisansetu", page_icon="🌾", layout="centered")

st.title("🌾 kisansetu")
st.caption(
    "Ask a farming question in plain words. Get the category, the crop, how "
    "urgent it is, what to do, and the government scheme that fits — offline, "
    "no API key."
)

with st.sidebar:
    st.header("Try an example")
    for ex in EXAMPLES:
        if st.button(ex, use_container_width=True):
            st.session_state["query"] = ex
    st.markdown("---")
    st.markdown(
        "Default backend is a **keyless, offline** advisor, so this runs with no "
        "API key. English and common Hindi crop names both work."
    )

query = st.text_area(
    "Your question",
    value=st.session_state.get("query", EXAMPLES[0]),
    height=120,
)

if st.button("Get advice", type="primary"):
    if not query.strip():
        st.warning("Type a question first.")
        st.stop()

    result = Advisor().advise(query)

    c1, c2, c3 = st.columns(3)
    c1.metric("Category", result.category)
    c2.metric("Crop", result.crop or "—")
    c3.metric("Urgency", _URGENCY_COLOR.get(result.urgency, result.urgency))

    st.subheader("Advice")
    st.write(result.summary)

    st.subheader("What to do")
    for step in result.steps:
        st.checkbox(step, key=step)

    st.subheader("Government scheme")
    st.info(result.scheme)

    st.caption(f"Backend: {result.backend}")
