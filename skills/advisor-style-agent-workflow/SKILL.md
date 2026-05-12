---
name: advisor-style-agent-workflow
description: Use when working on the AdvisorStyle Agent repository, a domain-agnostic academic supervisor memory framework for persistent style memory, revision memory, workflow memory, Zotero-assisted literature input, external Codex Skill layers, and prompt templates for long-term academic writing agents.
---

# AdvisorStyle Agent Workflow

Use this skill for tasks involving the `advisor-style-agent` project and its
domain-agnostic academic supervisor memory workflow.

## Core Concept

The project does not "learn" by changing a model. It grows by updating local
profile files such as:

```text
profiles/professor_x_profile.json
```

Each batch of supervisor papers, Zotero metadata, abstracts, notes, or pasted
paper text should update a supervisor profile. Later draft rewriting should read
that saved profile and use it as style guidance only. Domain knowledge belongs
in external local Codex Skills, not in the public repository.

## Default Workflow

1. Identify the active repository root.
2. Inspect `app.py`, `llm/`, `prompts/`, `profiles/`, and `README.md`.
3. Preserve the simple Streamlit structure unless the user asks for a larger
   architecture.
4. For memory changes, keep the data path explicit:
   Zotero input -> profile update -> revision memory -> profile-aware rewrite.
5. Validate by importing the relevant helper functions with `python -B`.
6. If publishing changes, create a clear branch, commit only intended files, and
   push to GitHub.

## Academic Integrity Rules

- Do not invent literature, page numbers, data, methods, results, or conclusions.
- Use supervisor profiles for writing style guidance, not factual evidence.
- Separate observed writing features from inferred preferences.
- Mark uncertain profile observations as tentative.
- Do not upload unpublished data or private drafts unless the user explicitly
  says the material can be shared.

## Memory Design Rules

Supervisor profiles should stay JSON and beginner-readable. The architecture has
three memory layers:

- style memory: supervisor writing style and expression patterns
- revision memory: lessons from draft revisions and feedback
- workflow memory: reusable writing and Zotero-assisted workflow steps

Prefer fields like:

- `profile_id`
- `supervisor_name`
- `discipline`
- `writing_style_features`
- `common_expressions`
- `structure_preferences`
- `tone`
- `revision_rules`
- `revision_memory`
- `workflow_memory`
- `zotero_sources`
- `external_skill_layers`
- `notes`

When updating a profile, append source summaries and keep uncertain observations
clearly labeled. Do not overwrite useful profile content unless the user asks.

## Prompt Template Rules

Prompt files live in `prompts/`. Keep them reusable and explicit about evidence
boundaries. The important templates are:

- `profile_builder.md`
- `profile_updater.md`
- `draft_rewriter_with_profile.md`
- `style_analyzer.md`
- `draft_rewriter.md`
- `zotero_literature_input.md`

Prompts should ask the LLM to flag missing evidence instead of fabricating
citations or claims.

## External Skill Layers

Keep the GitHub repository lightweight and domain-agnostic. Examples:

- Biology rules should live in a local biology writing Skill.
- Geology rules should live in a local geology writing Skill.
- Chemistry rules should live in a local chemistry writing Skill.
- Medicine rules should live in a local medical writing Skill.
- Engineering rules should live in a local engineering writing Skill.

## Zotero Workflow

Use Zotero Skill or pasted Zotero output to prepare local literature context.
Typical flow:

```text
Zotero supervisor papers
-> Codex / Zotero Skill retrieves literature information
-> AdvisorStyle Agent analyzes writing style
-> profiles/professor_x_profile.json is updated
-> user draft is rewritten using the saved profile
```

Common Zotero Skill commands to mention when useful:

```bash
python3 <plugin-root>/skills/zotero/scripts/zotero.py status --json
python3 <plugin-root>/skills/zotero/scripts/zotero.py search "supervisor name" --json
python3 <plugin-root>/skills/zotero/scripts/zotero.py export-bibtex --out references.bib
python3 <plugin-root>/skills/zotero/scripts/zotero.py citations --style apa --json
```

## Validation Snippets

Use lightweight checks after edits:

```bash
python -B -c "from llm.profile_manager import load_profile; print(load_profile('example_supervisor')['profile_id'])"
```

```bash
python -B -c "from llm.rewrite_engine import build_rewrite_with_profile_result; print(build_rewrite_with_profile_result('Draft text', {'profile_id':'demo'})['revision_plan'][0])"
```

## Publishing Notes

When committing changes for this project:

- Stage only intended project files.
- Keep branch names descriptive, for example `supervisor-style-memory`.
- If `gh` is unavailable, push the branch and give the GitHub compare link.
