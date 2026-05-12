from __future__ import annotations

from pathlib import Path


PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt_template(name: str) -> str:
    """Load a prompt template from the prompts folder."""
    path = PROMPT_DIR / name
    return path.read_text(encoding="utf-8")


def render_template(template: str, **values: str) -> str:
    """Render a small named-placeholder template."""
    safe_values = {key: value.strip() for key, value in values.items()}
    return template.format(**safe_values)
