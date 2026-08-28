# skills

Personal collection of [Agent Skills](https://skills.sh/) — installable via the
[`skills` CLI](https://github.com/vercel-labs/skills).

## Install

```bash
npx skills add fahrimz/skills
```

Or a single skill:

```bash
npx skills add fahrimz/skills --skill commit-conventions
```

```bash
npx skills add fahrimz/skills --skill obsidian-vault-governance
```

```bash
npx skills add fahrimz/skills --skill no-comments
```

## Skills

| Skill | Description |
|---|---|
| [`no-comments`](skills/no-comments/SKILL.md) | Remove unnecessary comments while preserving genuine constraint, correctness, and safety documentation |
| [`commit-conventions`](skills/commit-conventions/SKILL.md) | Angular-style oneliner + bullet-point commit/PR messages, no AI-attribution trailers |
| [`plan-parallel-implement-review`](skills/plan-parallel-implement-review/SKILL.md) | Plan → parallel implement → review for large multi-file features: a high-capability planner produces a wave-structured plan with subagent briefs, lower-tier implementors execute waves in parallel, a review pass integrates everything |
| [`obsidian-vault-governance`](skills/obsidian-vault-governance/SKILL.md) | Govern Obsidian vault edits: preserve sources, maintain links/hubs/index/log, lint, and safely commit/push |
