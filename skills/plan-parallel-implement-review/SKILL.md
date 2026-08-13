---
name: plan-parallel-implement-review
description: Orchestrate a large multi-file feature as plan → parallel implement → review, using a high-capability model to produce a wave-structured plan with ready-to-paste subagent briefs, lower-tier models to execute waves concurrently, and a review pass to integrate and clean up. Use when a task spans multiple files/layers (schema + backend + frontend, a migration plus its call sites, a feature that touches disjoint areas of a codebase) and would benefit from parallel subagents — not for single-file changes or tightly coupled logic that can't be split into independent tracks.
---

# Plan → Parallel Implement → Review

Three roles, three model tiers, one integrated result. The planner produces a plan
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

## Roles and model tiers

| Role | Job | Model tier | Example models |
|---|---|---|---|
| **Planner** | Turns the task into a file-level plan, dependency graph, and exact subagent briefs | Expensive, high-capability | Claude Opus family, GPT-5.6 Sol, DeepSeek V4 Pro |
| **Implementor** | Executes one brief inside one wave | Cheaper, faster | Claude Sonnet family, GPT-5.6 Luna, DeepSeek V4 Flash |
| **Reviewer** | Integrates all diffs, fixes seams, confirms PR-worthy | Whatever the change warrants — not fixed to either tier above | Judgment call: planner-tier for large/risky changes, implementor-tier for small ones |

These are role labels, not vendor lock-in — substitute whatever planner/implementor/
reviewer models the runtime has available; keep the *tier* the fixed part, not the
brand.

## The three steps

### 1. Plan (planner tier)

Hand the planner tier everything already known about the codebase (don't make it
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

### 2. Implement (implementor tier, per wave)

For each wave, spawn one implementor-tier subagent per brief, all in parallel — the
point of the wave split is that they don't need to coordinate. Only start wave *N+1*
once wave *N*'s interfaces are stable (its briefs actually done, not just started —
code doesn't have to be reviewed/merged yet, just the contract it exposes). If a
runtime can't literally run subagents concurrently, run them sequentially in wave
order; the plan is still correct, just slower.

Whatever spawning mechanism the executing agent has — background tasks, a
multi-agent tool, separate sessions, or literally doing each brief in turn — apply
the same rule: one brief, one file set, no two agents own the same file in the same
wave.

### 3. Review (whichever tier fits)

One pass, one model, full picture. Read every changed file, not just each
implementor's self-report. Check the plan's per-task callouts plus the generic
checklist in REFERENCE.md. Fix cross-agent seams directly rather than sending work
back for another round, unless a fix is large enough to need its own brief.

## Choosing the reviewer tier

Default to matching the planner's tier when the change is large, security-sensitive,
or touches a data model (migrations, auth, RLS, money). Drop to implementor tier for
small or low-risk features where "does everything compile and match the brief" is
the bulk of the check.
