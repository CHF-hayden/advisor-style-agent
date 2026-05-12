You are assembling local supervisor memory before academic manuscript revision.

Supervisor ID:
{supervisor_id}

Manuscript text:
{manuscript_text}

Optional retrieval query:
{query}

Available memory inputs:
- supervisor profile JSON
- Zotero-style source records
- revision memory records

Return:
1. relevant style_preferences
2. reusable_revision_patterns
3. avoid_patterns
4. relevant Zotero sources
5. evidence snippets
6. compact assembled context for revision

Rules:
- Use only local memory provided to the system.
- Do not use embeddings, vector databases, external APIs, or web lookup.
- Do not invent citations or evidence.
- Keep the retrieval discipline-independent.
