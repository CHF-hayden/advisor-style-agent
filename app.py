from __future__ import annotations

import json

import streamlit as st

from llm.profile_manager import (
    build_profile_update,
    default_profile_path,
    list_profiles,
    load_profile,
    save_profile,
)
from llm.revision_memory_manager import learn_from_revision_pair
from llm.rewrite_engine import build_rewrite_with_profile_result
from llm.zotero_metadata_ingestor import ingest_zotero_metadata, parse_zotero_metadata


st.set_page_config(
    page_title="AdvisorStyle Agent",
    page_icon="ASA",
    layout="wide",
)


def show_prompt_block(label: str, prompt: str) -> None:
    with st.expander(label, expanded=False):
        st.code(prompt, language="markdown")


def profile_selector(label: str) -> str:
    profiles = list_profiles()
    if not profiles:
        return ""
    return st.selectbox(label, profiles)


st.title("AdvisorStyle Agent")
st.caption(
    "A domain-agnostic academic supervisor memory framework for persistent "
    "style memory, revision learning, and Zotero-assisted writing workflows."
)

with st.sidebar:
    st.header("Academic Memory")
    st.write("This is not a chatbot. It is a local memory framework.")
    st.code("profiles/professor_x_profile.json", language="text")
    st.markdown(
        """
**Memory layers**

- Style memory
- Revision memory
- Workflow memory

Domain knowledge belongs in local Codex Skills, not hardcoded in this public repo.
        """
    )


tab_profile, tab_revision, tab_rewrite, tab_memory, tab_zotero = st.tabs(
    [
        "Build Supervisor Profile",
        "Learn from Revision Pair",
        "Rewrite Academic Draft",
        "Memory Architecture",
        "Zotero + Codex Skills",
    ]
)


with tab_profile:
    st.subheader("Build / Update Supervisor Profile")
    st.write(
        "Paste Zotero metadata, abstracts, notes, or paper text from one supervisor. "
        "The app updates a domain-agnostic style profile in `profiles/`."
    )

    col_a, col_b = st.columns([1, 1])
    with col_a:
        supervisor_id = st.text_input(
            "Supervisor profile ID",
            value="example_supervisor",
            help="Use a short file-safe name such as professor_x or lab_advisor.",
        )
        discipline = st.text_input(
            "Discipline label",
            value="general academic writing",
            help="This is descriptive metadata only. No domain logic is hardcoded.",
        )
    with col_b:
        source_type = st.selectbox(
            "Input source",
            [
                "Zotero metadata",
                "Abstracts",
                "Pasted paper text",
                "Supervisor notes",
                "Mixed literature context",
            ],
        )
        save_json = st.checkbox("Save updated local profile", value=True)

    literature_input = st.text_area(
        "Supervisor literature input",
        height=260,
        placeholder=(
            "Paste supervisor-authored abstracts, Zotero item summaries, notes, "
            "or representative paper excerpts here..."
        ),
    )

    if st.button("Update Style Memory", type="primary"):
        if not supervisor_id.strip():
            st.warning("Please enter a supervisor profile ID.")
        elif not literature_input.strip():
            st.warning("Please paste literature metadata, notes, abstracts, or paper text.")
        else:
            current_profile = load_profile(supervisor_id)
            result = build_profile_update(
                supervisor_id=supervisor_id,
                discipline=discipline,
                source_type=source_type,
                literature_input=literature_input,
                current_profile=current_profile,
            )
            if save_json:
                save_profile(supervisor_id, result["profile"])
                st.success(f"Profile saved to `{default_profile_path(supervisor_id)}`.")
            else:
                st.success("Profile preview generated.")

            st.markdown("#### Updated style memory preview")
            st.json(result["profile"])
            show_prompt_block("Profile-builder prompt", result["builder_prompt"])
            show_prompt_block("Profile-updater prompt", result["updater_prompt"])


with tab_revision:
    st.subheader("Learn from Revision Pair")
    st.write(
        "Paste an original paragraph and the revised version. The app creates "
        "a structured revision memory record and appends it to `revision_memory/`."
    )

    profile_id = profile_selector("Supervisor ID for revision memory")
    original_draft = st.text_area("Original text before revision", height=180)
    revised_draft = st.text_area("Revised text after supervisor/Codex revision", height=180)
    feedback_notes = st.text_area(
        "Optional feedback notes",
        height=120,
        placeholder="Paste reviewer, supervisor, or Codex revision notes here...",
    )

    if st.button("Learn from Revision Pair", type="primary"):
        if not profile_id:
            st.warning("Please create or select a supervisor profile first.")
        elif not original_draft.strip() or not revised_draft.strip():
            st.warning("Please provide both the original and revised text.")
        else:
            result = learn_from_revision_pair(
                original_text=original_draft,
                revised_text=revised_draft,
                supervisor_id=profile_id,
                notes=feedback_notes,
                save=True,
            )
            st.success(f"Revision memory saved to `{result['path']}`.")
            st.markdown("#### Structured revision memory")
            st.json(result["record"])
            show_prompt_block("LLM prompt for deeper revision-pattern extraction", result["prompt"])


with tab_rewrite:
    st.subheader("Rewrite Academic Draft")
    st.write(
        "Select a saved supervisor profile, paste your draft, and generate a "
        "profile-aware academic rewriting prompt. Any discipline-specific rules "
        "should come from local Codex Skills or user-provided context."
    )

    selected_profile = profile_selector("Supervisor profile")
    rewrite_goal = st.selectbox(
        "Rewrite goal",
        [
            "Improve clarity and academic tone",
            "Match supervisor profile more closely",
            "Strengthen logic and paragraph flow",
            "Condense repetitive writing",
            "Prepare a journal-style revision",
        ],
    )
    draft = st.text_area(
        "Your academic draft",
        height=300,
        placeholder="Paste the paragraph, abstract, or section you want to revise...",
    )

    if st.button("Prepare Profile-aware Rewrite", type="primary"):
        if not selected_profile:
            st.warning("Please create or select a supervisor profile first.")
        elif not draft.strip():
            st.warning("Please paste a draft first.")
        else:
            profile = load_profile(selected_profile)
            result = build_rewrite_with_profile_result(
                draft=draft,
                supervisor_profile=profile,
                rewrite_goal=rewrite_goal,
            )
            st.success("Profile-aware rewrite prompt generated.")
            st.markdown("#### Revision plan")
            for item in result["revision_plan"]:
                st.write(f"- {item}")
            show_prompt_block("Draft rewriter with saved profile", result["prompt"])


with tab_memory:
    st.subheader("Memory Architecture")
    selected_profile = profile_selector("View saved profile")

    st.markdown(
        """
AdvisorStyle Agent uses three memory layers:

| Layer | Stored in | Purpose |
|---|---|---|
| Style memory | `profiles/*.json` | Supervisor writing style, tone, structure, expressions |
| Revision memory | `revision_memory/*.json` | Patterns learned from original/revised draft pairs |
| Workflow memory | `templates/` and profile fields | Reusable writing and Zotero-assisted workflow steps |

The public repository stays discipline-independent. Biology, geology, chemistry,
medicine, engineering, and other domain rules should be layered through local
Codex Skills or user-provided context.
        """
    )

    if selected_profile:
        profile = load_profile(selected_profile)
        st.markdown(f"#### `{selected_profile}`")
        st.json(profile)
        with st.expander("Copyable profile JSON", expanded=False):
            st.code(json.dumps(profile, indent=2, ensure_ascii=False), language="json")


with tab_zotero:
    st.subheader("Add Zotero Metadata")
    st.write(
        "Paste Zotero-style metadata, BibTeX, RIS-like text, or plain text. "
        "This parser is local-only and does not call the Zotero API."
    )

    zotero_supervisor_id = st.text_input(
        "Supervisor ID for Zotero sources",
        value="example_supervisor",
        help="Saved records go to profiles/{supervisor_id}_zotero_sources.json.",
    )
    pasted_metadata = st.text_area(
        "Pasted metadata",
        height=220,
        placeholder=(
            "Paste BibTeX, RIS-like metadata, or plain text fields such as "
            "Title:, Authors:, Year:, Journal:, DOI:, Abstract:, Keywords:."
        ),
    )

    col_preview, col_save = st.columns([1, 1])
    parsed_record = None
    with col_preview:
        if st.button("Parse Metadata Preview"):
            if not pasted_metadata.strip():
                st.warning("Please paste metadata first.")
            else:
                parsed_record = parse_zotero_metadata(pasted_metadata)
                st.markdown("#### Parse preview")
                st.json(parsed_record)

    with col_save:
        if st.button("Save Metadata Record", type="primary"):
            if not zotero_supervisor_id.strip():
                st.warning("Please enter a supervisor ID.")
            elif not pasted_metadata.strip():
                st.warning("Please paste metadata first.")
            else:
                result = ingest_zotero_metadata(
                    supervisor_id=zotero_supervisor_id,
                    raw_input=pasted_metadata,
                    save=True,
                )
                st.success(f"Zotero metadata saved to `{result['path']}`.")
                st.json(result["record"])

    st.divider()
    st.subheader("Zotero + External Codex Skills")
    st.write(
        "Use Zotero Skill to retrieve literature context. Use local Codex Skills "
        "to add domain knowledge without hardcoding it into this GitHub framework."
    )

    st.markdown(
        """
**Framework workflow**

1. Zotero provides literature metadata, abstracts, notes, or BibTeX.
2. AdvisorStyle Agent updates supervisor style memory.
3. Revision memory learns from edited drafts and feedback.
4. Local Codex Skills add discipline-specific knowledge when needed.
5. The public repository remains lightweight and general-purpose.
        """
    )

    st.markdown("#### Example discipline layers")
    st.table(
        [
            {"Discipline": "Biology", "Local skill layer": "experimental design, gene/protein terminology, reporting norms"},
            {"Discipline": "Geology", "Local skill layer": "stratigraphy, sedimentology, geochemistry conventions"},
            {"Discipline": "Chemistry", "Local skill layer": "reaction conditions, analytical methods, compound naming"},
            {"Discipline": "Medicine", "Local skill layer": "clinical evidence, reporting standards, ethics constraints"},
            {"Discipline": "Engineering", "Local skill layer": "design constraints, evaluation metrics, system architecture"},
        ]
    )

    st.markdown("#### Example Zotero Skill commands")
    st.code(
        """python3 <plugin-root>/skills/zotero/scripts/zotero.py status --json
python3 <plugin-root>/skills/zotero/scripts/zotero.py search "supervisor name" --json
python3 <plugin-root>/skills/zotero/scripts/zotero.py export-bibtex --out references.bib
python3 <plugin-root>/skills/zotero/scripts/zotero.py citations --style apa --json""",
        language="bash",
    )

    st.warning(
        "Do not upload unpublished data or private drafts to external services unless "
        "you have explicitly decided that the material can be shared."
    )
