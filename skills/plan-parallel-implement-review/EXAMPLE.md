# Worked example: partner self-service profile

Illustrative only — a feature that added self-service profile editing for approved
partners in an Expo/React Native app backed by Supabase. Shown to demonstrate wave
shape, not as a template to copy verbatim (real column names, RLS policies, and file
paths belong in that project, not here).

The task spanned schema, backend wiring, and two frontend surfaces — a natural
disjoint-file split:

**Wave 1 — foundation (parallel, no shared files):**
- *Task A:* new DB migration — a `user_id` link column, a `description` column, new
  RLS policies scoping a partner to their own row, a trigger restricting which
  columns a self-update may touch, and a storage policy for self-uploaded photos.
- *Task B:* admin-side change to invite a partner's login on approval, idempotent
  against re-approval after a suspension.

Both touch entirely separate files (a new migration file vs. an existing admin
action file) — genuinely parallel, and wave 2 only needs to know the *shapes* Task A
produces (column names, policy names), not read its SQL mid-flight.

**Wave 2 — depends on Task A's schema shape (parallel):**
- *Task C:* the data-access layer — read-my-profile / update-my-profile functions
  against the new column and policies.
- *Task D:* the auth deep-link handling for the invite flow from Task B — a
  different file, same wave, because it depends on Task B's *shape* (an invite link
  exists to land on) rather than Task B's code.

**Wave 3 — depends on Task C's function signatures:**
- *Task E:* a store wrapping Task C's functions.
- *Task F:* the router/guard change that routes a partner session to the new screen
  instead of the normal app flow — depends on knowing *that* a "is this a partner"
  check exists (Task E's shape), not on the screen itself.

**Wave 4 — depends on Task E's store shape:**
- *Task G:* the profile screen itself (form, validation, save, access-denied state
  for non-approved partners).

**Review:** one pass reading the full diff — confirmed the screen's save path
actually round-tripped through the store → data layer → RLS-scoped update, checked
that the self-update trigger really blocked the fields it was supposed to (not just
that it existed), and caught that two waves had each written a near-identical
"format phone number" helper — consolidated to one.

The point isn't the specific waves above — it's that each wave's boundary lined up
with a real interface handoff (a schema shape, a function signature, a "does this
kind of session exist" check), not an arbitrary file count.
