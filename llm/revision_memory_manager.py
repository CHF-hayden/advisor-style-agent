from __future__ import annotations

import difflib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from llm.profile_manager import PROJECT_ROOT, slugify_profile_id
from llm.prompt_loader import load_prompt_template, render_template


REVISION_MEMORY_DIR = PROJECT_ROOT / "revision_memory"


def revision_memory_path(supervisor_id: str) -> Path:
    """Return the local JSON path for a supervisor's revision memory."""
    return REVISION_MEMORY_DIR / f"{slugify_profile_id(supervisor_id)}_revision_memory.json"


def build_revision_memory_record(
    original_text: str,
    revised_text: str,
    supervisor_id: str,
    notes: str = "",
) -> dict[str, Any]:
    """Create a structured, discipline-independent revision memory record."""
    original = original_text.strip()
    revised = revised_text.strip()
    clean_id = slugify_profile_id(supervisor_id)
    now = datetime.now(timezone.utc).isoformat()

    observed_changes = _summarize_observed_changes(original, revised)

    return {
        "supervisor_id": clean_id,
        "original_text": original,
        "revised_text": revised,
        "observed_changes": observed_changes,
        "reusable_revision_patterns": [
            "Compare the original and revised text before turning any change into a stable rule.",
            "Prefer reusable writing-process patterns over domain-specific claims.",
            "Keep changes that improve clarity, logical flow, tone, or evidence boundaries.",
        ],
        "style_preferences": [
            "Preserve the author's intended meaning while improving academic clarity.",
            "Use cautious, evidence-aware academic phrasing.",
            "Make paragraph logic and sentence transitions explicit when the revision supports it.",
        ],
        "avoid_patterns": [
            "Do not invent citations, data, methods, results, or conclusions.",
            "Do not treat a single revision pair as a universal supervisor preference.",
            "Do not hardcode discipline-specific rules into the public framework.",
        ],
        "evidence_boundary_notes": [
            "Revision memory is writing guidance, not factual evidence.",
            "Claims needing sources should be flagged for Zotero-backed support.",
            "Domain interpretation should come from local Codex Skills or user-provided context.",
        ],
        "notes": notes.strip(),
        "created_at": now,
    }


def build_revision_learning_prompt(record: dict[str, Any]) -> str:
    """Render an LLM-ready prompt for deeper revision-pattern extraction."""
    template = load_prompt_template("revision_memory_updater.md")
    return render_template(
        template,
        profile_id=record["supervisor_id"],
        original_draft=record["original_text"],
        revised_draft=record["revised_text"],
        feedback_notes=record.get("notes") or "No feedback notes provided.",
    )


def append_revision_memory(record: dict[str, Any]) -> Path:
    """Append a revision memory record to the supervisor's JSON memory file."""
    REVISION_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    path = revision_memory_path(record["supervisor_id"])
    records: list[dict[str, Any]] = []
    if path.exists():
        records = json.loads(path.read_text(encoding="utf-8"))
    records.append(record)
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def learn_from_revision_pair(
    original_text: str,
    revised_text: str,
    supervisor_id: str,
    notes: str = "",
    save: bool = True,
) -> dict[str, Any]:
    """Build a structured revision memory record and optionally save it."""
    record = build_revision_memory_record(
        original_text=original_text,
        revised_text=revised_text,
        supervisor_id=supervisor_id,
        notes=notes,
    )
    prompt = build_revision_learning_prompt(record)
    path = append_revision_memory(record) if save else revision_memory_path(supervisor_id)
    return {"record": record, "prompt": prompt, "path": path}


def _summarize_observed_changes(original: str, revised: str) -> list[str]:
    changes: list[str] = []
    if len(revised) < len(original):
        changes.append("Revised text is shorter, suggesting condensation or removal of redundancy.")
    elif len(revised) > len(original):
        changes.append("Revised text is longer, suggesting added clarification, transitions, or qualification.")
    else:
        changes.append("Revised text has similar length, suggesting local phrasing or structure changes.")

    original_sentences = _sentence_count(original)
    revised_sentences = _sentence_count(revised)
    if revised_sentences != original_sentences:
        changes.append(
            f"Sentence count changed from {original_sentences} to {revised_sentences}."
        )

    diff = list(difflib.SequenceMatcher(None, original, revised).get_opcodes())
    replace_count = sum(1 for tag, *_ in diff if tag == "replace")
    insert_count = sum(1 for tag, *_ in diff if tag == "insert")
    delete_count = sum(1 for tag, *_ in diff if tag == "delete")
    changes.append(
        f"Text diff summary: {replace_count} replacements, {insert_count} insertions, {delete_count} deletions."
    )

    if _contains_cautious_language(revised) and not _contains_cautious_language(original):
        changes.append("Revised text adds more cautious academic phrasing.")

    return changes


def _sentence_count(text: str) -> int:
    marks = [".", "?", "!", "。", "？", "！"]
    count = sum(text.count(mark) for mark in marks)
    return max(1, count)


def _contains_cautious_language(text: str) -> bool:
    lowered = text.lower()
    cues = [
        "may",
        "might",
        "suggest",
        "indicate",
        "potential",
        "likely",
        "可能",
        "表明",
        "暗示",
    ]
    return any(cue in lowered for cue in cues)
