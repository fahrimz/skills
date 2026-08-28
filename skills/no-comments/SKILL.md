---
name: no-comments
description: "Keep code free of unnecessary comments by removing redundant, stale, workaround, and speculative explanations while preserving comments that document genuine external constraints, correctness requirements, or safety decisions. Use when reviewing or changing source code."
---

# No comments

Keep comments only when they communicate information the code cannot express clearly.
Prefer making the code self-explanatory over adding or preserving explanatory comments.

## Scope

Use the caller's files or diff when provided. Otherwise inspect the current working-tree
diff against the base branch, defaulting to `main` when the base is not specified.

## Review

Inspect every comment in scope and classify it before changing it:

- Remove comments that restate the code, narrate obvious steps, preserve historical
  context that no longer affects the code, speculate about intent, or defend a
  workaround that can be removed.
- Keep a comment only when it explains a genuine constraint outside the code's control,
  a non-obvious correctness or safety requirement, or an intentional behavior that
  cannot be made clear through names, structure, or tests.
- Treat lint, TypeScript, and similar suppressions as actionable findings. Prefer fixing
  the underlying issue; correctness and safety suppressions require particular care and
  must not be deleted without preserving the protection they provide.
- Do not widen the requested scope or edit application code merely to justify deleting a
  comment. If a small root-cause fix makes a comment unnecessary, make that fix only when
  it is in scope.

Comments saying `do not remove`, `do not change wording`, or `talk to X before changing`
are not automatically valid. Verify the claimed constraint when possible. If it is
real, preserve the smallest useful comment and report the constraint. If encoding the
constraint in a type, runtime check, test, or CI lint would be cheaper and in scope,
propose that change and wait for approval before making it.

## Completion

Make the smallest safe changes, then recheck the scoped diff for missed comments,
changed behavior, and newly dead parameters or paths. Report:

- comments deleted and any comments intentionally retained;
- root-cause fixes made;
- constraints that remain unenforced or require follow-up; and
- ambiguous findings left open.
