---
name: obsidian-vault-governance
description: "Govern reads and writes to an Obsidian personal wiki: load its local rules, preserve source immutability, maintain links/hubs/index/log, lint changes, and safely commit and push. Use whenever an agent touches an Obsidian vault or is asked to file, connect, reorganize, journal, sync, or audit vault content."
---

# Obsidian Vault Governance

Use this skill whenever an Obsidian vault is in scope. Treat the vault's local `CLAUDE.md` as authoritative for schema, folders, naming, and workflows.

## Operating modes

- **Read-only:** inspect and answer without changing files. This is the default for summaries, queries, and diagnosis.
- **Write:** only when the user explicitly asks to create, edit, file, connect, reorganize, journal, sync, or lint/fix. Run the full safety and bookkeeping workflow below.
- **Journal:** enter only when the user is processing journal material; preserve append-only journal history and promote durable facts deliberately.

## Write workflow

1. Discover the vault from `OBSIDIAN_VAULT_ROOT`, or walk upward until `CLAUDE.md`, `index.md`, and the expected folders are found. Stop if multiple candidates exist.
2. Read `CLAUDE.md` completely. Inspect `git status` and hash the files in the requested scope before editing.
3. Never edit `sources/`. Link to raw material from wiki pages instead.
4. Preserve the schema: validate frontmatter on touched wiki pages and repair mechanical drift, but do not mass-normalize or invent uncertain metadata.
5. Maintain graph structure: exact filename links first; bare links only for vault-wide unique names; qualify duplicates with folder paths and aliases. Never guess ambiguous targets. **Never put `#`, `|`, `[`, or `]` in a new filename/title** — Obsidian parses these inside `[[target]]` (`#` = heading anchor, `|` = alias separator, `[`/`]` = link terminators), so a page named with one can never be wikilinked to correctly. Write out issue/PR references as words instead (`Issue 177`, not `#177`). The lint helper below flags any existing offenders as `UNSAFE-NAME`.
6. New pages require a durable, clearly requested entity/document. Add frontmatter, hub and `index.md` registration, cross-links, and one `log.md` entry.
7. Append exactly one concise `log.md` line per write operation. Read-only work does not log.
8. Run the bundled mechanical lint helper, then review semantic findings (contradictions, stale claims, identity merges, deletion, or uncertain relationships) without silently changing them.
9. Re-check overlapping file hashes and `git status`. Stop if another agent changed an overlapping file, conflicts exist, or unrelated changes would be included.
10. When the operation is scoped, lint-clean, and conflict-free, commit and push automatically. Use the repository's `commit-conventions` skill for the message; never force-push or add AI-attribution trailers. If no upstream exists, commit locally and report it.

## Autonomy boundary

Automatically fix mechanical link, hub/index, frontmatter, metadata-date, and log issues when intent is unambiguous. Ask before changing factual meaning, resolving contradictions, merging entities, deleting notes, or making broad rewrites. Keep pre-existing unrelated work untouched.

## Journal mode

Format raw entries in the existing monthly journal, retain activity/todo semantics, check off rather than delete todos, add relevant wikilinks, and promote durable facts to entity pages. Keep ephemeral detail in the journal. Follow the journal grammar in `CLAUDE.md`.

## Lint helper

Run:

```sh
python3 <skill-dir>/scripts/lint_vault.py --root <vault-root>
```

It reports broken links, orphan pages, missing project-hub references, missing required frontmatter, and unsafe filenames (`#`/`|`/`[`/`]`). Default mode reports findings without failing, so inherited vault debt does not block an operation; compare against the pre-edit scan and use `--strict` when a clean baseline is required. Treat source orphans as review candidates—not permission to edit them. It does not detect contradictions or determine whether a claim is stale; those require reading the relevant pages.

## Handoff

End every write with: operation, files changed, links/registrations repaired, lint result, unresolved judgment calls, commit/push result, and untouched pre-existing changes.
