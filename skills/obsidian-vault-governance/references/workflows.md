# Vault workflow reference

Use the local vault's `CLAUDE.md` for the authoritative schema and detailed ingest, sync, journal, query, and lint workflows. This reference only records the invariants the governance skill must preserve.

## Required invariants

- `sources/` is immutable and append-only.
- Wiki pages changed in content receive a current `updated` date.
- Every created, renamed, or deleted page is reflected in `index.md`.
- Every write operation gets one append-only `log.md` entry.
- Hubs named `00 - <Name> Hub.md` map the pages in their folder.
- Ambiguous duplicate filenames use folder-qualified wikilinks with aliases.
- Contradictions and stale snapshots are surfaced, not papered over.

## Safe stop conditions

Stop before mutation or commit when the vault root is ambiguous, a source file would need editing, a link target has multiple plausible meanings, an entity merge is uncertain, overlapping files changed during the operation, or unrelated work would be staged.

