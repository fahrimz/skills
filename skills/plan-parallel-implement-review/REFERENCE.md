# Reference: briefs and the reviewer checklist

## Subagent brief template (planner fills this in per task)

```
## Task: <short name>

**Wave:** <N>
**Owns (create/modify):** <exact file paths — nothing outside this list>
**Do not touch:** <files owned by sibling tasks in this wave, or anything
  the plan explicitly reserves for a later wave>

**Context you can assume (no need to verify, no need to read in-flight
sibling code):**
- <interface/contract from an earlier wave, e.g. "professionals.ts exports
  `getMyProfessional(): Promise<Professional | null>`">
- <a convention from the codebase the planner already confirmed, so the
  implementor doesn't have to re-derive it>

**What to build:**
<concrete instructions — exact function signatures, exact SQL, exact
component props, exact copy/strings where the source spec has them>

**Explicitly out of scope:**
<things adjacent to this task that belong to a different brief, so the
implementor doesn't "helpfully" duplicate another task's work>

**Self-check before returning:**
- [ ] Type-checks / lints clean for the files you touched
- [ ] Matches the exact exports/signatures this brief specified
- [ ] Didn't touch any file outside "Owns"
- [ ] <task-specific check, e.g. "RLS policy tested against both the
      approved and pending status">
```

Keep briefs self-contained. An implementor should never need to ask "what did the
other agent in my wave do" — if it does, the wave split was wrong and two tasks
should have been merged into one, or reordered into different waves.

## Generic reviewer checklist

Extend this with task-specific items from the plan's own callouts; don't replace it.

- **Compiles/lints/type-checks** across the whole diff, not per-file — cross-file
  contract mismatches (implementor A assumed a signature implementor B changed) are
  exactly what parallel work risks, and only show up once everything's together.
- **Every brief's contract was honored** — spot check the actual exports/signatures
  against what the brief promised downstream tasks would get.
- **No duplicated logic** — parallel agents solving adjacent problems sometimes both
  write the same helper; consolidate.
- **Seams, not just units** — trace at least one full path end-to-end (e.g. UI
  action → store → data layer → schema) rather than trusting each layer's own
  self-check.
- **Follows existing repo conventions**, not just "valid code" — naming, error
  handling, styling approach, file organization matching what was already there
  before this task started.
- **Risk callouts from the plan are actually resolved**, not just noted.
- **No leftover scaffolding** — dead code, TODO stubs, or debug logging an
  implementor left behind while iterating.
- **The diff reads like it was written by one person with full context** — that's
  the actual bar for "PR-worthy," not "each piece works in isolation."

## Wave sizing

A wave with one task is fine — it just means that step had no parallel sibling this
round. Don't force artificial parallelism; split only where files are genuinely
disjoint. A plan with 2-4 tasks per wave across 2-4 waves is typical for a
medium-large feature; more than that usually means the plan should be split into two
separate runs of this whole workflow instead of one giant one.
