from __future__ import annotations

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
