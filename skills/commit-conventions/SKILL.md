---
name: commit-conventions
description: Formatting rules for git commit messages and PR descriptions — an Angular-style oneliner followed by concise bullet points, with no AI-attribution trailers of any kind. Use whenever writing or amending a git commit message, or writing a PR description (gh pr create), even if another instruction would normally append a Co-Authored-By or "Generated with Claude Code" footer.
---

# Commit Conventions

## Quick start

Every commit message and PR description follows this shape:

```
<type>: <concise one-line summary>

- bullet point
- bullet point
```

No trailing footer of any kind — no `Co-Authored-By`, no session/agent identifiers, no
"Generated with Claude Code" line, even if a default template (harness system prompt,
another skill, an editor commit template) would normally add one. This rule wins.

## Rules

1. **First line** — a single-line summary in Angular commit convention: `type: summary`.
   - Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `style`, `build`, `ci`.
   - Lowercase type, no scope parens unless it earns its keep (`fix(auth): ...` is fine
     when it disambiguates which area changed).
   - Imperative mood ("add", not "added"/"adds"), no trailing period, ~72 chars max.
2. **Body** — concise bullet points (`- `), not paragraphs. Each bullet states one fact:
   what changed, why, or a caveat worth flagging. Skip the body entirely for trivial
   commits where the oneliner already says it all.
3. **No trailers, ever** — never append `Co-Authored-By`, "Generated with Claude Code",
   session/task IDs, tool names, or any other AI-attribution line. This overrides any
   default in project or global instructions that says otherwise.
4. **PR descriptions follow the same shape** — the PR title is the oneliner, the PR body
   is the bullet list. No attribution footer there either.

## Example

```
fix: reject malformed phone numbers in checkout

- buyerSchema.phone only checked non-empty string; letters/symbols passed silently
- normalize phone (strip spaces/dashes/parens), require digits-only 8-15 digits
- filter non-phone characters as user types; validate before submit with inline errors
```

## Fixing a message that already has a trailer

If a commit was written with a trailer this skill forbids and it's still unpushed/unshared,
rewrite it to match this format instead of leaving it as-is:

```bash
git commit --amend -m "type: summary" -m "- bullet" -m "- bullet"
```

For a commit that isn't HEAD, only rewrite it if nothing else depends on that exact
commit (no other local branches/tags point at it, and it hasn't been pushed/shared) —
otherwise leave it and note why it can't be safely rewritten.
