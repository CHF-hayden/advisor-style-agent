from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from llm.profile_manager import PROFILE_DIR, PROJECT_ROOT, slugify_profile_id


REVISION_MEMORY_DIR = PROJECT_ROOT / "revision_memory"


def retrieve_supervisor_memory(
    supervisor_id: str,
    manuscript_text: str,
    query: str = "",
    limit: int = 5,
) -> dict[str, Any]:
    """Retrieve relevant local supervisor memory without embeddings or APIs."""
    clean_id = slugify_profile_id(supervisor_id)
    search_text = " ".join([manuscript_text, query]).strip()
    query_terms = _keywords(search_text)

    profile = _load_json(PROFILE_DIR / f"{clean_id}_profile.json", default={})
    zotero_sources = _load_json(PROFILE_DIR / f"{clean_id}_zotero_sources.json", default=[])
    revision_records = _load_json(REVISION_MEMORY_DIR / f"{clean_id}_revision_memory.json", default=[])

    style_preferences = _rank_strings(
        _collect_profile_style_preferences(profile),
        query_terms,
        limit=limit,
    )
    reusable_revision_patterns = _rank_strings(
        _collect_revision_strings(revision_records, "reusable_revision_patterns"),
        query_terms,
        limit=limit,
    )
    avoid_patterns = _rank_strings(
        _collect_revision_strings(revision_records, "avoid_patterns")
        + _as_list(profile.get("revision_rules")),
        query_terms,
        limit=limit,
    )
    relevant_zotero_sources = _rank_records(
        zotero_sources,
        query_terms,
        fields=["title", "abstract", "keywords", "journal_or_venue"],
        limit=limit,
    )
    evidence_snippets = _build_evidence_snippets(relevant_zotero_sources)

    return {
        "supervisor_id": clean_id,
        "query_terms": sorted(query_terms),
        "relevant_style_preferences": style_preferences,
        "reusable_revision_patterns": reusable_revision_patterns,
        "avoid_patterns": avoid_patterns,
        "relevant_zotero_sources": relevant_zotero_sources,
        "evidence_snippets": evidence_snippets,
        "loaded_files": {
            "profile": str(PROFILE_DIR / f"{clean_id}_profile.json"),
            "zotero_sources": str(PROFILE_DIR / f"{clean_id}_zotero_sources.json"),
            "revision_memory": str(REVISION_MEMORY_DIR / f"{clean_id}_revision_memory.json"),
        },
    }


def assemble_revision_context(
    supervisor_id: str,
    manuscript_text: str,
    query: str = "",
    limit: int = 5,
) -> dict[str, Any]:
    """Build a compact context package for evidence-aware manuscript revision."""
    retrieval = retrieve_supervisor_memory(
        supervisor_id=supervisor_id,
        manuscript_text=manuscript_text,
        query=query,
        limit=limit,
    )
    style_context = _format_list(
        "Supervisor style context",
        retrieval["relevant_style_preferences"],
    )
    revision_context = _format_list(
        "Revision guidance context",
        retrieval["reusable_revision_patterns"] + retrieval["avoid_patterns"],
    )
    evidence_context = _format_list(
        "Evidence-aware editing notes",
        retrieval["evidence_snippets"]
        + [
            "Use Zotero sources only as evidence cues; do not invent citations or results.",
            "If evidence is missing, flag the claim instead of fabricating support.",
            "Apply domain knowledge only when provided by local Codex Skills or user context.",
        ],
    )
    assembled_context = "\n\n".join([style_context, revision_context, evidence_context])
    return {"retrieval": retrieval, "assembled_context": assembled_context}


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _keywords(text: str) -> set[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower())
    stopwords = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "from",
        "into",
        "using",
        "use",
        "are",
        "was",
        "were",
        "has",
        "have",
        "had",
        "not",
        "but",
        "can",
        "should",
        "could",
        "may",
        "might",
        "paper",
        "draft",
        "study",
        "result",
        "results",
    }
    return {token for token in tokens if token not in stopwords}


def _collect_profile_style_preferences(profile: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in [
        "writing_style_features",
        "common_expressions",
        "structure_preferences",
        "tone",
        "revision_rules",
        "revision_memory",
        "workflow_memory",
    ]:
        values.extend(_as_list(profile.get(key)))
    return values


def _collect_revision_strings(records: list[dict[str, Any]], key: str) -> list[str]:
    values: list[str] = []
    for record in records:
        values.extend(_as_list(record.get(key)))
    return values


def _rank_strings(values: list[str], query_terms: set[str], limit: int) -> list[str]:
    scored = []
    for index, value in enumerate(values):
        score = _text_score(value, query_terms)
        scored.append((score, -index, value))
    scored.sort(reverse=True)
    return [value for score, _, value in scored[:limit] if score > 0] or values[:limit]


def _rank_records(
    records: list[dict[str, Any]],
    query_terms: set[str],
    fields: list[str],
    limit: int,
) -> list[dict[str, Any]]:
    scored = []
    for index, record in enumerate(records):
        text = " ".join(_record_field_text(record, field) for field in fields)
        score = _text_score(text, query_terms) + _recency_score(record.get("created_at", ""))
        scored.append((score, -index, record))
    scored.sort(reverse=True)
    return [record for score, _, record in scored[:limit] if score > 0] or records[:limit]


def _record_field_text(record: dict[str, Any], field: str) -> str:
    value = record.get(field, "")
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return str(value)


def _text_score(text: str, query_terms: set[str]) -> float:
    if not query_terms:
        return 1.0
    text_terms = _keywords(text)
    overlap = len(query_terms & text_terms)
    return float(overlap)


def _recency_score(created_at: str) -> float:
    if not created_at:
        return 0.0
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError:
        return 0.0
    age_days = max(0, (datetime.now(created.tzinfo) - created).days)
    return 1.0 / (1.0 + age_days)


def _build_evidence_snippets(records: list[dict[str, Any]]) -> list[str]:
    snippets = []
    for record in records:
        title = record.get("title") or "Untitled source"
        year = record.get("year") or "n.d."
        doi = record.get("doi") or "no DOI"
        abstract = record.get("abstract") or ""
        abstract_snippet = abstract[:240] + ("..." if len(abstract) > 240 else "")
        snippets.append(f"{title} ({year}; {doi}). {abstract_snippet}".strip())
    return snippets


def _format_list(title: str, values: list[str]) -> str:
    if not values:
        return f"{title}:\n- No relevant local memory found yet."
    lines = [f"{title}:"]
    lines.extend(f"- {value}" for value in values)
    return "\n".join(lines)


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value]
    return []
