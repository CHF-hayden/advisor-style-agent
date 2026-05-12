# Manuscript Revision Workflow

Use this workflow when revising a manuscript paragraph or section with
AdvisorStyle Agent.

## Steps

1. Identify the `supervisor_id`.
2. Paste the manuscript paragraph or section.
3. Retrieve supervisor memory:
   - style memory from `profiles/{supervisor_id}_profile.json`
   - Zotero source memory from `profiles/{supervisor_id}_zotero_sources.json`
   - revision memory from `revision_memory/{supervisor_id}_revision_memory.json`
4. Assemble revision context:
   - supervisor style context
   - revision guidance context
   - evidence-aware editing notes
5. Revise the manuscript using the assembled context.
6. Flag unsupported claims instead of inventing citations.
7. If the user confirms the revision is useful, save the before/after pair as
   revision memory.

## Boundaries

- Do not use embeddings, vector databases, or external APIs in the minimal workflow.
- Do not hardcode domain-specific rules into the public repository.
- Use local Codex Skills for private domain knowledge or supervisor-specific rules.
