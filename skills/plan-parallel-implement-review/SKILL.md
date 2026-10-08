---
name: plan-parallel-implement-review
description: Orchestrate a large multi-file feature as plan → parallel implement → review, using a mid-tier model at a middle reasoning level to produce a wave-structured plan with ready-to-paste subagent briefs, the same family at a low level to execute waves concurrently, and one step up to integrate and clean up. Use when a task spans multiple files/layers (schema + backend + frontend, a migration plus its call sites, a feature that touches disjoint areas of a codebase) and would benefit from parallel subagents — not for single-file changes or tightly coupled logic that can't be split into independent tracks.
---

# Plan → Parallel Implement → Review

Three roles, three levels of the same model family, one integrated result. The
planner produces a plan
detailed enough that implementors never need to talk to each other; the reviewer is
the only one who reads everyone's diff at once.

## When to use this

Use it when the work **decomposes into disjoint-file tracks** — e.g. a DB migration +
RLS policies, a backend sync/data layer, a new store, a new screen/component, and a
wiring change to an existing router/guard, where each track mostly touches its own
files and only depends on *interfaces* (function signatures, column names, route
paths) from earlier tracks, not their code.

Don't use it for a single-file fix, a small tightly-coupled change, or logic that
can't be cleanly split without agents fighting over the same file — just implement it
directly, or use a lighter fan-out for a couple of independent files.

## Roles and model levels

| Role | Job | Level within one family |
|---|---|---|
| **Planner** | Turns the task into a file-level plan, dependency graph, and exact subagent briefs | middle |
| **Implementor** | Executes one brief inside one wave | low |
| **Reviewer** | Integrates all diffs, fixes seams, confirms PR-worthy | high (Anthropic) / middle (GPT) |

Every role runs on the *same* model family — three roles, three reasoning levels of
one family, not three vendors. Which models those levels resolve to is a per-family
lookup, below.

## Pick the table for your family

Use the table matching the family of the model **you** are running as, so every
agent in the run is in the same family and reasoning levels are comparable.

### Anthropic family

| Role | Model | Level |
|---|---|---|
| **Planner** | `claude-sonnet-5.5` | `medium` |
| **Implementor** | `claude-haiku-5.5` | `low` |
| **Reviewer** | `claude-haiku-5.5` | `high` |

### GPT-5.6 family

| Role | Model | Level |
|---|---|---|
| **Planner** | `gpt-5.6-luna` | `medium` |
| **Implementor** | `gpt-5.6-luna` | `low` |
| **Reviewer** | `gpt-5.6-luna` | `medium` |

**If a model or level above is not available in your runtime, stop and tell the
user exactly which one is missing** rather than silently substituting — ask before
substituting, and never cross families mid-run. Cross-family swaps change what one
agent's self-report means to the reviewer, which is the thing this whole workflow
depends on.

### Other families

If your model isn't Anthropic or GPT-5.6 (DeepSeek, Gemini, Grok, a local model,
a free-tier provider, …), map the same three roles onto what that family offers:
the planner and reviewer on the most capable model in the family, the implementors
on the cheapest model that still follows a written brief exactly. Free tiers rarely
have levels, so use separate models instead. State the mapping in your first
message so the user can correct it before any subagent spawns.

## The three steps

### 1. Plan (planner model, middle level)

Hand the planner everything already known about the codebase (don't make it
re-derive research you already have) and ask for a single document containing:

- A full file-level task list — every file to create/modify, in 2-4 sentences each,
  with exact new/changed exports, signatures, or SQL where non-obvious.
- A **wave-structured dependency graph**: wave *N* tasks touch disjoint files and run
  fully concurrently; wave *N+1* may depend only on wave *N*'s **interfaces** (a
  function signature, a column name, a route path) — never on reading wave *N*'s
  in-flight, possibly-uncommitted code.
- One ready-to-paste **subagent brief per task** (template below) — concrete enough
  that an implementor with no other context can execute it correctly.
- Any schema/migration/config text written out in full, not described.
- Risk/edge-case callouts the reviewer must specifically check.
- A **final review checklist** tailored to this task (see REFERENCE.md for the
  generic base to extend).

See [REFERENCE.md](REFERENCE.md) for the brief template and full reviewer checklist,
and [EXAMPLE.md](EXAMPLE.md) for a worked example.

### 2. Implement (implementor model, low level, per wave)

For each wave, spawn one implementor subagent per brief, all in parallel — the
point of the wave split is that they don't need to coordinate. Only start wave *N+1*
once wave *N*'s interfaces are stable (its briefs actually done, not just started —
code doesn't have to be reviewed/merged yet, just the contract it exposes). If a
runtime can't literally run subagents concurrently, run them sequentially in wave
order; the plan is still correct, just slower.

Whatever spawning mechanism the executing agent has — background tasks, a
multi-agent tool, separate sessions, or literally doing each brief in turn — apply
the same rule: one brief, one file set, no two agents own the same file in the same
wave.

### 3. Review (reviewer model, high/middle level)

One pass, one model, full picture. Read every changed file, not just each
implementor's self-report. Check the plan's per-task callouts plus the generic
checklist in REFERENCE.md. Fix cross-agent seams directly rather than sending work
back for another round, unless a fix is large enough to need its own brief.

## Choosing the reviewer model

The reviewer model is already fixed one step above the implementors, so the only
judgment left is the level within it. Stay at the baseline level for small or
low-risk features where "does everything compile and match the brief" is the bulk
of the check. For a large, security-sensitive, or data-model change (migrations,
auth, RLS, money), step the reviewer model's level up one notch rather than
switching to the planner model — same family, same model, more deliberation.
