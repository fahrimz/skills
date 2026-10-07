---
name: dump-session
description: Save a curated write-up of the current conversation — a summary plus the cleaned user/assistant dialogue — as a new note in the Obsidian vault, for reuse as context in future sessions. Use when the user asks to dump, save, or archive this conversation/session, wants a session write-up filed in Obsidian, or invokes /dump-session.
---

# Dump Session

Produces one new, immutable note under the vault's `sources/notes/<project>/` capturing this conversation, then wires it into the wiki (hub link, `index.md`, `log.md`) per `obsidian-vault-governance`.

## When to use

Only on explicit request, typically at the end of a conversation — this is a manual action, never run proactively or automatically.

## Process

1. **Load `obsidian-vault-governance`** first — it owns vault discovery, `CLAUDE.md`, frontmatter schema, hub/index/log bookkeeping, linting, and commit/push. This skill only decides *what* to write and *where*.
2. **Export the transcript before composing.** Run `scripts/export_transcript.py --provider auto --cwd "$PWD" --output /tmp/dump-session-conversation.md` (use `--input PATH` when the current session is not the newest matching JSONL file). The exporter keeps only user/assistant text, removes tool payloads and duplicate records, and produces the source for `## Conversation`. If no local transcript exists, use the current conversation directly.
3. **Identify the project.** Infer from the working directory / conversation topic against the vault's known `project/<slug>` tags in `CLAUDE.md`. If none match, ask once; don't invent a slug.
   - `## Summary` — context/goal, what was done and why, decisions made, artifacts touched (files, PRs, endpoints, commits), gotchas, open threads. Write this like the vault's existing tool notes (e.g. `tools/mitmproxy iOS Simulator Setup.md`) — dense and reusable, not a recap of tool calls.
   - `## Conversation` — paste the exported Markdown; it already contains natural-language user/assistant turns without tool payloads, base64/image blobs, or system-reminder blocks.
4. **Frontmatter**: `type: note`, `project: <slug>`, `tags: [project/<slug>]`, `created`/`updated`: today.
5. **Filename**: `<Topic> — YYYY-MM-DD HHmm.md` (24h local time, no colon — filesystem-safe), saved under `sources/notes/<project>/`. The time disambiguates multiple sessions on the same project in one day. Never edit a past session's file — each run creates a new one. Frontmatter `created`/`updated` stay date-only (`YYYY-MM-DD`) per the vault's schema; the time only lives in the filename. **`<Topic>` must not contain `#`, `|`, `[`, or `]`** (breaks wikilinks — see `obsidian-vault-governance`) — write issue/PR references as words: `Issue 177`, not `#177`.
6. **Wire it in**: add one line to the project hub (a "Sessions" list, one line per entry linking the new note) and one `log.md` line. Do not touch `index.md` beyond the required registration for a new page.
7. **Flag, don't auto-save, durable facts.** If something in the conversation looks like it belongs in the separate `~/.claude/.../memory` system (a preference, a recurring gotcha, project context that outlives this session), list it at the end of your reply and suggest `/remember` — do not write it there yourself.
8. Hand off per `obsidian-vault-governance`'s required format: file created, hub/log lines added, lint result, commit/push result.

## Notes

- Keep `## Conversation` legible — quote blocks (`> **User:**` / `> **Assistant:**`), not a raw JSON transcript.
- If the conversation is very long, prefer trimming low-signal back-and-forth (repeated tool retries, verbose debugging) over truncating the Summary.
- This skill only ever *creates* a new source file; it never edits a previous session's dump.
