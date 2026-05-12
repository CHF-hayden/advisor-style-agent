import streamlit as st

st.title("AdvisorStyle Agent")

st.write("AI Academic Writing Assistant (Prototype)")

mode = st.selectbox("Mode", ["Style Analyzer", "Rewrite Paper"])

if mode == "Style Analyzer":
    text = st.text_area("Paste supervisor paper text")

    if st.button("Analyze Style"):
        st.success("Style Profile Generated (Mock)")
        st.json({
            "tone": "formal",
            "structure": "logical + section-driven",
            "style": "concise academic writing",
            "sentence_length": "medium-long"
        })

if mode == "Rewrite Paper":
    draft = st.text_area("Paste your draft")
    style = st.text_area("Style profile (optional)")

    if st.button("Rewrite"):
        st.success("Rewritten Version (Mock Output)")
        st.write(
            "This is a rewritten academic version following supervisor style..."
        )