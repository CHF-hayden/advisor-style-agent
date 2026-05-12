from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from llm.profile_manager import PROFILE_DIR, slugify_profile_id


def zotero_sources_path(supervisor_id: str) -> Path:
    """Return the local JSON path for pasted Zotero-style source records."""
    return PROFILE_DIR / f"{slugify_profile_id(supervisor_id)}_zotero_sources.json"


def parse_zotero_metadata(raw_input: str) -> dict[str, Any]:
    """Parse pasted metadata, BibTeX, or RIS-like text without network access."""
    raw = raw_input.strip()
    source_type = _detect_source_type(raw)

    record = {
        "title": _first_nonempty(
            _bibtex_field(raw, "title"),
            _ris_field(raw, "TI"),
            _ris_field(raw, "T1"),
            _label_field(raw, ["title", "Title"]),
        ),
        "authors": _parse_authors(raw, source_type),
        "year": _first_nonempty(
            _bibtex_field(raw, "year"),
            _ris_field(raw, "PY"),
            _ris_field(raw, "Y1"),
            _label_field(raw, ["year", "Year", "date", "Date"]),
        ),
        "journal_or_venue": _first_nonempty(
            _bibtex_field(raw, "journal"),
            _bibtex_field(raw, "booktitle"),
            _ris_field(raw, "JO"),
            _ris_field(raw, "JF"),
            _ris_field(raw, "T2"),
            _label_field(raw, ["journal", "Journal", "venue", "Venue", "publication", "Publication"]),
        ),
        "doi": _first_nonempty(
            _bibtex_field(raw, "doi"),
            _ris_field(raw, "DO"),
            _label_field(raw, ["doi", "DOI"]),
            _doi_from_text(raw),
        ),
        "abstract": _first_nonempty(
            _bibtex_field(raw, "abstract"),
            _ris_field(raw, "AB"),
            _label_field(raw, ["abstract", "Abstract"]),
        ),
        "keywords": _parse_keywords(raw),
        "source_type": source_type,
        "raw_input": raw,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return record


def save_zotero_metadata(supervisor_id: str, record: dict[str, Any]) -> Path:
    """Append parsed metadata to profiles/{supervisor_id}_zotero_sources.json."""
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    path = zotero_sources_path(supervisor_id)
    records: list[dict[str, Any]] = []
    if path.exists():
        records = json.loads(path.read_text(encoding="utf-8"))
    records.append(record)
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def ingest_zotero_metadata(
    supervisor_id: str,
    raw_input: str,
    save: bool = True,
) -> dict[str, Any]:
    """Parse pasted Zotero-style metadata and optionally save it locally."""
    record = parse_zotero_metadata(raw_input)
    path = save_zotero_metadata(supervisor_id, record) if save else zotero_sources_path(supervisor_id)
    return {"record": record, "path": path}


def _detect_source_type(raw: str) -> str:
    if raw.lstrip().startswith("@"):
        return "bibtex"
    if re.search(r"^[A-Z][A-Z0-9]\s+-\s+", raw, flags=re.MULTILINE):
        return "ris-like"
    return "plain-text"


def _bibtex_field(raw: str, field: str) -> str:
    pattern = rf"{re.escape(field)}\s*=\s*"
    match = re.search(pattern, raw, flags=re.IGNORECASE)
    if not match:
        return ""

    index = match.end()
    while index < len(raw) and raw[index].isspace():
        index += 1
    if index >= len(raw):
        return ""

    opener = raw[index]
    if opener == "{":
        value, _ = _read_balanced_braces(raw, index)
        return _clean_value(value)
    if opener == '"':
        value, _ = _read_quoted(raw, index)
        return _clean_value(value)

    end = raw.find(",", index)
    if end == -1:
        end = len(raw)
    return _clean_value(raw[index:end])


def _read_balanced_braces(raw: str, start: int) -> tuple[str, int]:
    depth = 0
    chars: list[str] = []
    for index in range(start, len(raw)):
        char = raw[index]
        if char == "{":
            depth += 1
            if depth == 1:
                continue
        elif char == "}":
            depth -= 1
            if depth == 0:
                return "".join(chars), index + 1
        chars.append(char)
    return "".join(chars), len(raw)


def _read_quoted(raw: str, start: int) -> tuple[str, int]:
    chars: list[str] = []
    escaped = False
    for index in range(start + 1, len(raw)):
        char = raw[index]
        if char == '"' and not escaped:
            return "".join(chars), index + 1
        chars.append(char)
        escaped = char == "\\" and not escaped
    return "".join(chars), len(raw)


def _ris_field(raw: str, tag: str) -> str:
    values = []
    pattern = rf"^{re.escape(tag)}\s+-\s*(.+)$"
    for match in re.finditer(pattern, raw, flags=re.MULTILINE):
        values.append(_clean_value(match.group(1)))
    return "; ".join(value for value in values if value)


def _label_field(raw: str, labels: list[str]) -> str:
    for label in labels:
        pattern = rf"^{re.escape(label)}\s*:\s*(.+)$"
        match = re.search(pattern, raw, flags=re.MULTILINE)
        if match:
            return _clean_value(match.group(1))
    return ""


def _parse_authors(raw: str, source_type: str) -> list[str]:
    if source_type == "bibtex":
        author_text = _bibtex_field(raw, "author")
        if author_text:
            return [_clean_value(author) for author in re.split(r"\s+and\s+", author_text) if author.strip()]
    if source_type == "ris-like":
        authors = []
        for tag in ["AU", "A1"]:
            value = _ris_field(raw, tag)
            if value:
                authors.extend([item.strip() for item in value.split(";") if item.strip()])
        if authors:
            return authors
    author_text = _label_field(raw, ["authors", "Authors", "author", "Author"])
    if author_text:
        return [_clean_value(author) for author in re.split(r";|,\s+(?=[A-Z][a-z]+\\b)", author_text) if author.strip()]
    return []


def _parse_keywords(raw: str) -> list[str]:
    keywords = _first_nonempty(
        _bibtex_field(raw, "keywords"),
        _bibtex_field(raw, "keyword"),
        _ris_field(raw, "KW"),
        _label_field(raw, ["keywords", "Keywords", "tags", "Tags"]),
    )
    if not keywords:
        return []
    return [_clean_value(keyword) for keyword in re.split(r";|,", keywords) if keyword.strip()]


def _doi_from_text(raw: str) -> str:
    match = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", raw, flags=re.IGNORECASE)
    return match.group(0) if match else ""


def _first_nonempty(*values: str) -> str:
    for value in values:
        if value:
            return value
    return ""


def _clean_value(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().strip("{}").strip()).strip()
