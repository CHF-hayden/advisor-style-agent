from __future__ import annotations

import streamlit as st

from llm.rewrite_engine import build_rewrite_result
from llm.style_analyzer import build_style_profile
from llm.zotero_input import build_literature_context


st.set_page_config(
    page_title="AdvisorStyle Agent",
    page_icon="ASA",
    layout="wide",
)


def show_prompt_block(label: str, prompt: str) -> None:
    with st.expander(label, expanded=False):
        st.code(prompt, language="markdown")


st.title("AdvisorStyle Agent")
st.caption(
    "A beginner-friendly academic writing assistant for supervisor style analysis, "
    "draft rewriting, and Zotero-ready literature input."
)

with st.sidebar:
    st.header("Workflow")
    module = st.radio(
        "Choose a module",
        [
            "Supervisor Style Analyzer",
            "Academic Draft Rewriter",
            "Zotero-assisted Literature Input",
        ],
    )
    st.divider()
    st.info(
        "This prototype does not require an API key. It prepares structured prompts "
        "that can later be sent to an LLM provider."
    )


if module == "Supervisor Style Analyzer":
    st.subheader("Supervisor Style Analyzer")
    st.write(
        "Paste representative writing from a supervisor or target author. "
        "The app will create a structured style profile and an LLM-ready prompt."
    )

    supervisor_text = st.text_area(
        "Supervisor or target-author writing sample",
        height=280,
        placeholder="Paste abstract, introduction, discussion, or full paper excerpts here...",
    )
    field = st.text_input(
        "Research field or topic",
        placeholder="Example: sedimentology, carbonate reservoirs, academic geology",
    )

    if st.button("Analyze Style", type="primary"):
        if not supervisor_text.strip():
            st.warning("Please paste a writing sample first.")
        else:
            result = build_style_profile(supervisor_text, field)
            st.success("Style profile prompt generated.")
            st.json(result["profile"])
            show_prompt_block("Reusable style-analysis prompt", result["prompt"])


elif module == "Academic Draft Rewriter":
    st.subheader("Academic Draft Rewriter")
    st.write(
        "Paste your draft and an optional style profile. The app will prepare a "
        "structured rewrite request that preserves academic rigor."
    )

    draft = st.text_area(
        "Your academic draft",
        height=260,
        placeholder="Paste the paragraph, abstract, or section you want to revise...",
    )
    style_profile = st.text_area(
        "Style profile from the analyzer (optional)",
        height=160,
        placeholder="Paste style profile notes here, or leave blank for a general academic style.",
    )
    rewrite_goal = st.selectbox(
        "Rewrite goal",
        [
            "Improve clarity and academic tone",
            "Make logic more explicit",
            "Condense repetitive writing",
            "Match supervisor style more closely",
        ],
    )

    if st.button("Prepare Rewrite", type="primary"):
        if not draft.strip():
            st.warning("Please paste a draft first.")
        else:
            result = build_rewrite_result(draft, style_profile, rewrite_goal)
            st.success("Rewrite prompt generated.")
            st.markdown("#### Suggested revision plan")
            for item in result["revision_plan"]:
                st.write(f"- {item}")
            show_prompt_block("Reusable draft-rewriting prompt", result["prompt"])


else:
    st.subheader("Zotero-assisted Literature Input")
    st.write(
        "Prepare clean literature context for future Zotero Skill or Zotero API integration. "
        "For now, paste citation notes manually; later this module can read Zotero items."
    )

    citation_notes = st.text_area(
        "Citation notes, BibTeX snippets, or Zotero item summaries",
        height=260,
        placeholder=(
            "Example:\n"
            "- Author Year: key finding, method, study area, why it matters.\n"
            "- Citation key: @smith2024...\n"
        ),
    )
    draft_context = st.text_area(
        "How these sources should support your draft",
        height=140,
        placeholder="Example: Use these papers to support the discussion of depositional environment...",
    )

    if st.button("Prepare Literature Context", type="primary"):
        if not citation_notes.strip():
            st.warning("Please paste at least one literature note or citation item.")
        else:
            result = build_literature_context(citation_notes, draft_context)
            st.success("Zotero-ready literature prompt generated.")
            st.json(result["literature_map"])
            show_prompt_block("Reusable literature-input prompt", result["prompt"])
