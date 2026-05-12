from __future__ import annotations

from llm.prompt_loader import load_prompt_template, render_template


def build_literature_context(citation_notes: str, draft_context: str = "") -> dict:
    """Create a Zotero-ready literature organization prompt."""
    template = load_prompt_template("zotero_literature_input.md")
    prompt = render_template(
        template,
        citation_notes=citation_notes,
        draft_context=draft_context or "No draft context provided.",
    )

    literature_map = {
        "module": "Zotero-assisted Literature Input",
        "status": "manual input now; Zotero API integration later",
        "expected_fields": [
            "citation key",
            "main claim or finding",
            "method or evidence type",
            "relevance to draft",
            "caution or limitation",
        ],
        "future_integration": "Replace pasted notes with Zotero Skill or Zotero API records.",
    }

    return {"literature_map": literature_map, "prompt": prompt}
