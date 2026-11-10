---
name: project-deliver
description: >-
  Deliver a work item (GitHub issue/PRD, spec-system features) end to end across the project's surfaces (backend, backoffice, mobile, etc.): plan, delegate edits to cheap subagents, verify locally, verify against the production-like env, release, and open a PR with evidence. Use when the user says "deliver", "work on issue #N", or wants the full autonomous build-test-PR cycle.
---

# project-deliver

Run one work item to completion with minimal check-ins. Process lives here; project facts live in the project profile.

## Quick start

`/project-deliver #46` or `/project-deliver #46 --surfaces mobile,backend`

1. Load `.claude/delivery.md` (the profile). If missing, inspect the repo, draft it using [PROFILE.md](PROFILE.md), show it to the user once, save it, continue.
2. Read the work item and its sources of truth (profile `sources`). Resolved decisions in the item are final.
3. Detect surfaces touched (from the item, cross-checked against planned diff paths; `--surfaces` overrides). Record the call in the decisions log.
4. Build a run plan: the phases below, expanded only for touched surfaces, in profile `order` (backend before clients). Skip steps a surface does not define.
5. Execute without stopping. Output the plan once, then continue.

## Phases

**1. Plan.** Break the item into work packages with dependencies. Delegate edits to subagents using the profile's `delegate` model/effort. Each brief names exact files, symbols, the acceptance criterion, and what not to touch. Review every diff yourself.

**2. Verify (local).** For each touched surface, run its `local` env and `verify` method. Check every acceptance criterion functionally. For UI surfaces also check alignment, spacing, colour, type and touch targets against the design reference. Fix before moving on. Capture before/after evidence per the surface's `evidence` type; note what cannot be captured (e.g. toasts).

**3. Verify (prod-like).** Stop local servers, switch env to the profile's `prod` env, run migrations only per the surface's `prod_migrate` setting (`autonomous` | `ask` | `never`; default `ask`), then verify on the surface's prod platform. Fix bugs here; do not switch back unless required.

**4. Release.** Only for touched surfaces with a `release` entry: bump version, run release commands (in parallel when independent), record results and errors. Open a PR to the default branch with `Refs #N`, evidence attached, decisions log, migration record, build results, token usage. Link the PR.

## Rules

- Run profile `gates` before every commit. Small commits following profile `commits`.
- Trivial choices: decide, log under "Decisions taken". Ask only for a blocker the sources do not answer.
- Never reset/wipe a production database, regardless of profile.
- Record migration state (list before, row counts for destructive data changes, list after).
- Record tokens per phase: subagent usage figures from each delegated task, plus an estimate for your own work, marked as an estimate.
- Clean up devices/servers you started at the end; leave ones the user started.

## Stop conditions

Stop early only for a crucial blocker (unclear spec, data at risk, failed migration, unrecoverable build failure). Then open a **draft** PR with progress, the blocker and evidence, and report. Never force through.

## Finish

Report: PR link, surfaces covered, decisions taken, phase token usage, anything skipped and why.
