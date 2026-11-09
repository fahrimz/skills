# Delivery profile schema

Saved per project at `.claude/delivery.md`. Facts only, no process. Omit any key that does not apply; the skill skips steps it has no entry for.

```yaml
sources:            # ordered, first wins on conflict
  - work item body (issue/PRD); its resolved decisions are final
  - spec system (e.g. a spec-system MCP: space id, feature keys)
  - design references attached to the item
  - AGENTS.md / CONVENTION.md / framework docs

delegate: { model: <model>, effort: <level> }

commits: <rules, e.g. subject <=64 chars, conventional prefix, bullet body, no trailers>
pr: <target branch, linking keyword, skill to use for format>

envs:
  local: <how to start/seed; env file>
  prod:  <how to switch (env file), warning notes>

surfaces:
  <name>:
    order: 1                 # lower runs first
    paths: [<globs>]         # for scope detection
    gates: [<commands>]
    local:  { run: <cmd>, platform: <e.g. ios simulator | browser | none> }
    prod:   { run: <cmd>, platform: <e.g. android emulator | browser | none> }
    prod_migrate: autonomous | ask | never   # default ask
    migrate: <cmd or none>
    verify: <how to prove it works>
    evidence: screenshots | query-output | logs
    release: [<commands>]    # only fires when this surface changed
    version: <file and bump convention>
```

Keep safety rules out of the profile. "Never wipe production" is global in the skill. `prod_migrate: autonomous` is an explicit per-project opt-in.
