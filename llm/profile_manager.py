from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from llm.prompt_loader import load_prompt_template, render_template


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = PROJECT_ROOT / "profiles"


def slugify_profile_id(profile_id: str) -> str:
    """Create a simple file-safe profile id."""
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", profile_id.strip()).strip("_")
    return value or "example_supervisor"


def default_profile_path(profile_id: str) -> Path:
    return PROFILE_DIR / f"{slugify_profile_id(profile_id)}_profile.json"


def list_profiles() -> list[str]:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(path.stem.replace("_profile", "") for path in PROFILE_DIR.glob("*_profile.json"))


def load_profile(profile_id: str) -> dict[str, Any]:
    path = default_profile_path(profile_id)
    if not path.exists():
        return create_empty_profile(profile_id)
    return json.loads(path.read_text(encoding="utf-8"))


def save_profile(profile_id: str, profile: dict[str, Any]) -> Path:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    path = default_profile_path(profile_id)
    path.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def create_empty_profile(profile_id: str, discipline: str = "academic research") -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    clean_id = slugify_profile_id(profile_id)
    return {
        "profile_id": clean_id,
        "supervisor_name": "",
        "discipline": discipline,
        "created_at": now,
        "updated_at": now,
        "source_count": 0,
        "writing_style_features": [],
        "common_expressions": [],
        "structure_preferences": [],
        "tone": [],
        "revision_rules": [
            "Preserve scientific meaning and evidence boundaries.",
            "Do not invent literature, data, methods, results, or conclusions.",
            "Flag unsupported claims instead of fabricating citations.",
        ],
        "zotero_sources": [],
        "notes": "This is a local style-memory profile. Update it with supervisor papers over time.",
    }


def build_profile_update(
    supervisor_id: str,
    discipline: str,
    source_type: str,
    literature_input: str,
    current_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Update a local profile skeleton and prepare profile-building prompts."""
    profile = current_profile or create_empty_profile(supervisor_id, discipline)
    now = datetime.now(timezone.utc).isoformat()
    profile["profile_id"] = slugify_profile_id(supervisor_id)
    profile["discipline"] = discipline or profile.get("discipline", "academic research")
    profile["updated_at"] = now
    profile["source_count"] = int(profile.get("source_count", 0)) + 1

    source_summary = {
        "source_type": source_type,
        "added_at": now,
        "character_count": len(literature_input),
        "summary": "User-provided local literature input. Review with an LLM before treating inferences as stable.",
    }
    profile.setdefault("zotero_sources", []).append(source_summary)

    _append_unique(profile, "writing_style_features", f"New {source_type.lower()} input added for style analysis.")
    _append_unique(profile, "structure_preferences", "Use the profile-builder prompt to extract durable section and paragraph preferences.")
    _append_unique(profile, "tone", "Keep claims cautious, evidence-based, and discipline-appropriate.")

    builder_template = load_prompt_template("profile_builder.md")
    updater_template = load_prompt_template("profile_updater.md")

    builder_prompt = render_template(
        builder_template,
        supervisor_id=profile["profile_id"],
        discipline=profile["discipline"],
        source_type=source_type,
        literature_input=literature_input,
    )
    updater_prompt = render_template(
        updater_template,
        current_profile=json.dumps(profile, indent=2, ensure_ascii=False),
        source_type=source_type,
        literature_input=literature_input,
    )

    return {
        "profile": profile,
        "builder_prompt": builder_prompt,
        "updater_prompt": updater_prompt,
    }


def _append_unique(profile: dict[str, Any], key: str, value: str) -> None:
    items = profile.setdefault(key, [])
    if value not in items:
        items.append(value)
