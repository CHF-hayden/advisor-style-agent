from __future__ import annotations

from llm.prompt_loader import load_prompt_template, render_template


def build_style_profile(supervisor_text: str, field: str = "") -> dict:
    """Create a structured style-analysis prompt and lightweight local summary."""
    template = load_prompt_template("style_analyzer.md")
    prompt = render_template(
        template,
        field=field or "general academic research",
        supervisor_text=supervisor_text,
    )

    profile = {
        "module": "Supervisor Style Analyzer",
        "field": field or "general academic research",
        "input_length_characters": len(supervisor_text),
        "expected_output": [
            "tone and stance",
            "sentence and paragraph patterns",
            "argument structure",
            "citation and evidence habits",
            "style rules for rewriting",
        ],
        "integrity_rule": "Do not invent claims, citations, data, methods, or results.",
    }

    return {"profile": profile, "prompt": prompt}
