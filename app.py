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
from llm.rewrite_engine import build_rewrite_with_profile_result


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
    selected = st.selectbox(label, profiles)
    return selected


st.title("AdvisorStyle Agent")
st.caption(
    "A long-term supervisor-style academic writing assistant for Codex, "
    "Zotero-based literature input, and reusable style memory."
)

with st.sidebar:
    st.header("Style Memory")
    st.write("The agent grows by updating local JSON files in `profiles/`.")
    st.code("profiles/professor_x_profile.json", language="text")
    st.info(
        "The model does not become smarter by itself. Each new batch of "
        "supervisor papers should update the saved profile, and draft rewriting "
        "should read that profile."
    )


tab_build, tab_view, tab_rewrite, tab_zotero = st.tabs(
    [
        "Build / Update Supervisor Profile",
        "View Supervisor Profile",
        "Rewrite My Draft",
        "Zotero Workflow Guide",
    ]
)


with tab_build:
    st.subheader("Build / Update Supervisor Profile")
    st.write(
        "Paste Zotero metadata, abstracts, notes, or paper text from one supervisor. "
        "The app will update a local JSON profile, which acts as the supervisor "
        "style memory."
    )

    col_a, col_b = st.columns([1, 1])
    with col_a:
        supervisor_id = st.text_input(
            "Supervisor profile ID",
            value="example_supervisor",
            help="Use a short file-safe name, such as wang_lab or advisor_chen.",
        )
        discipline = st.text_input(
            "Discipline or writing context",
            value="academic research",
            placeholder="Example: geology, sedimentology, environmental science",
        )
    with col_b:
        source_type = st.selectbox(
            "Input source",
            [
                "Pasted paper text",
                "Zotero metadata",
                "Zotero notes",
                "Abstracts",
                "Mixed literature context",
            ],
        )
        save_json = st.checkbox("Save updated local profile", value=True)

    literature_input = st.text_area(
        "Supervisor literature input",
        height=260,
        placeholder=(
            "Paste one supervisor's abstracts, Zotero item summaries, notes, "
            "or representative paper excerpts here..."
        ),
    )

    if st.button("Update Supervisor Profile", type="primary"):
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

            st.markdown("#### Updated profile preview")
            st.json(result["profile"])
            show_prompt_block("Profile-builder prompt", result["builder_prompt"])
            show_prompt_block("Profile-updater prompt", result["updater_prompt"])


with tab_view:
    st.subheader("View Supervisor Profile")
    selected_profile = profile_selector("Choose a saved profile")

    if selected_profile:
        profile = load_profile(selected_profile)
        st.markdown(f"#### `{selected_profile}`")
        st.json(profile)

        with st.expander("Copyable profile JSON", expanded=False):
            st.code(json.dumps(profile, indent=2, ensure_ascii=False), language="json")
    else:
        st.warning("No profiles found. Create one in the first tab.")


with tab_rewrite:
    st.subheader("Rewrite My Draft")
    st.write(
        "Select a saved supervisor profile, paste your draft, and generate a "
        "profile-aware academic rewriting prompt. The saved profile is the memory "
        "used during revision."
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


with tab_zotero:
    st.subheader("Zotero Workflow Guide")
    st.write(
        "Use Zotero Skill or Zotero exports to collect literature from one supervisor, "
        "then paste the cleaned output into the profile builder."
    )

    st.markdown(
        """
1. Search the supervisor's papers in Zotero.
2. Export metadata, abstracts, notes, or BibTeX.
3. Paste that material into **Build / Update Supervisor Profile**.
4. Save the profile in `profiles/`.
5. Use the saved profile in **Rewrite My Draft**.
        """
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
