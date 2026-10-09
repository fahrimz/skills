---
name: project-activity
description: Report what changed across Fahri's active projects since a cutoff — pulling each remote, diffing commits, and flagging uncommitted work. The active set is read from the `status` frontmatter field (value `active`) on each Obsidian project hub, never inferred from git. Use when the user asks to summarize latest activities, catch up on projects, see what changed since yesterday or last week, or check for uncommitted work across projects.
---

# Project Activity

Read-only sweep across every project marked active in the vault: pull, diff, report. Never mutates a repo.

## When to use

On request, when the user wants a cross-project catch-up — "summarize latest activities from active projects", "what changed since yesterday", "anything uncommitted". Typically at the start of a session.

## Process

1. **Load `obsidian-vault-governance`** for vault discovery and `CLAUDE.md` reading. This skill is read-only against the vault: report only, no edits, no `log.md` line (governance says read-only work does not log).

2. **Determine the active set from vault frontmatter — this is the single source of truth.** For each folder under `projects/`, read `00 - <Name> Hub.md` and keep it if `status:` is exactly `active`. Do not infer activity from commit dates, and do not include a repo just because it was recently touched. If the active set and reality look badly out of sync, say so in the report rather than quietly widening the net.

   Parse the `repo:` frontmatter value for the checkout path. It comes in four shapes — handle each:
   - a local path: `/Users/fahrimz/dev/fitvybe`, `~/dev/pup`
   - a bare GitHub URL: `https://github.com/fahrimz/mimir` → map to `~/dev/<repo-name>`
   - a multi-repo string: `"kaptrain-app: <url> · kaptrain-cms: <url>"` → local checkout is `~/dev/kaptrain`
   - absent → **skip and report**. Active projects with no `repo:` are invisible to this sweep; list them so the gap stays visible instead of vanishing.

   Also scan `~/dev/*/` for git checkouts that no active project claims. Report these as untracked, so a repo doing real work isn't invisible for lack of a pack.

3. **Pull each repo, read-only.** Run `git pull --ff-only` per repo. Capture stdout/stderr.

   **Never rebase, merge, stash, checkout, reset, or otherwise mutate a repo.** A failed pull is reported with its reason and the sweep continues:
   - `Repository not found` / auth failure → credentials or org access, not a code problem
   - `Not possible to fast-forward` → local and remote have diverged; needs a merge or rebase decision
   - `local changes would be overwritten` → uncommitted work is blocking; report the files

   These are judgment calls that can lose uncommitted work. Report and let the user decide.

4. **Collect activity since the cutoff.** Default cutoff is midnight the previous day; honor an explicit date or duration if given. For each successfully pulled repo:
   - `git log --since=<cutoff> --pretty=format:"%h %ad %s" --date=format:"%m-%d %H:%M" --all`
   - **Filter out `t3 checkpoint` commits.** T3 orchestration writes a checkpoint commit per ordinal and they bury real work — in one repo they were 15 of 24 commits in a day. Report the real count separately from the checkpoint count so the volume isn't misread.
   - For each repo with commits, `git diff --stat <oldest>^..<newest>` for the size of the change.

5. **Check uncommitted work everywhere, not just active repos.** `git status --porcelain` per repo. Group by repo, show filenames. Untracked files count — a new `plugins/mimo/` directory is more interesting than a modified lockfile. Note worktrees: `~/dev/worktrees/` and `~/dev/rb/*/` may hold repos too.

6. **Check the vault for what it already recorded.** `git log --since=<cutoff>` in the vault repo, and the tail of `log.md`. The vault's own log lines are often the best narrative summary — prefer them over reconstructing history from commits. Vault commits also contain `t3 checkpoint` noise; filter the same way.

7. **Report shape.** Lead with the one-line picture: which projects moved, and what the dominant thread was. Then per project — commits with times, what shipped, and open/unblocked items. Then a table of uncommitted work. Then pull failures with reasons. Then sync problems and stale/flagged state.

   **Distinguish your commits from other people's.** Compare against `git config user.name`. An upstream fast-forward (e.g. a vendored repo you don't own) is not your work — say whose it is.

## Notes

- Timestamps: 24h local, `MM-DD HH:MM`.
- Do not commit or push anything. This skill reports; `obsidian-vault-governance` owns writes.
- If a project is marked `active` but has had no commits in weeks, call it out under stale signals rather than omitting it. Silence is a finding.
- Order projects by most recent activity, not alphabetically.