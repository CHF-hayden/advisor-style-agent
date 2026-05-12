from __future__ import annotations

import json
from typing import Any

from llm.prompt_loader import load_prompt_template, render_template


def build_rewrite_result(
    draft: str,
    style_profile: str = "",
    rewrite_goal: str = "Improve clarity and academic tone",
) -> dict:
    """Create a structured rewrite prompt without calling an external LLM."""
    template = load_prompt_template("draft_rewriter.md")
    prompt = render_template(
        template,
        draft=draft,
        style_profile=style_profile or "No custom style profile provided.",
        rewrite_goal=rewrite_goal,
    )

    revision_plan = [
        "Preserve the original scientific meaning and evidence boundaries.",
        "Improve academic tone, coherence, and paragraph logic.",
        "Apply the provided supervisor-style profile where available.",
        "Flag any missing citation or unsupported claim instead of inventing evidence.",
    ]

    return {"revision_plan": revision_plan, "prompt": prompt}


def build_rewrite_with_profile_result(
    draft: str,
    supervisor_profile: dict[str, Any],
    rewrite_goal: str = "Improve clarity and academic tone",
) -> dict:
    """Create a profile-aware rewrite prompt without calling an external LLM."""
    template = load_prompt_template("draft_rewriter_with_profile.md")
    prompt = render_template(
        template,
        draft=draft,
        supervisor_profile=json.dumps(supervisor_profile, indent=2, ensure_ascii=False),
        rewrite_goal=rewrite_goal,
    )

    revision_plan = [
        "Use the saved supervisor profile as style guidance, not as factual evidence.",
        "Preserve the author's scientific meaning and uncertainty level.",
        "Improve structure, tone, and expression according to the profile rules.",
        "Flag missing citations, weak claims, or places where Zotero evidence is needed.",
    ]

    return {"revision_plan": revision_plan, "prompt": prompt}
