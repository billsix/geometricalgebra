# Lean proof files: keep topic-oriented, unify the 2D/3D filing rule, fix asymmetric names

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-10-03 (William Emerison Six <billsix@gmail.com>, from a "do these topic files
deserve to exist, or should they fold into G2/G3?" question).
**Part of:** the Lean proof initiative, `tasks/investigate-lean-proofs-for-ga.md`.
**See also:** `tasks/reference/lean-ga-proof-architecture.md` (the leaf-vs-structural layering this
preserves); sibling `tasks/lean-lift-theorem-statements-to-objects.md` (SEQUENCING: that task
heavily edits `G2.lean`; do not run both at once — see "Sequencing").

## BLUF

The `proofs/GacalcProofs/*.lean` corpus (26 source files) is organized **by topic** (one concept
per file: projection, rotation, sandwich, cross, measures, …). The decision here is to **keep that
topic organization** — explicitly NOT to fold the topic files into `G2.lean`/`G3.lean` — and instead
fix two real inconsistencies: (1) some concepts keep their 2D and 3D proofs together in one file
(`Measures`, `Trig`, `AlgebraLaws`, `Exp`, `GradeProjection`, `Sandwich`) while others split them
into sibling files (`Projection2D`/`Projection`, `Rotation`/`Rotation3D`, …), with no rule; (2) the
bare file name means a **different dimension** depending on topic — `Rotation.lean` is 2D but
`Projection.lean` is 3D — which is actively confusing. This task picks one filing rule and one
naming convention and applies them. It is a **pure reorganization**: no proof statement or tactic
changes, so correctness = `make lean` green + `sorry`-free and a git diff that is only moves/renames
+ `import` updates. "Done" = the rule is applied, names are unambiguous, `make lean` passes.

## Context — how to read this cold (why topic-oriented wins; the current state)

The question that spawned this was whether the topic files should exist at all or be folded into the
two per-algebra files. **They should exist.** Topic organization mirrors the Python library (which is
deliberately one-concept-per-file: `measure.py`, `vectorcalc.py`, `standardposition.py`,
`transforms.py`, `frame.py` — by concept, never by dimension) and the "Geometry 2" book, which the
proofs are an oracle *for*; it co-locates the 2D and 3D forms of one idea (the pedagogy — compare
dimensions side by side); and it keeps `G2.lean`/`G3.lean` as the from-scratch definition + leaf
layer rather than ~2000-line monoliths. Folding by dimension would scatter a single concept (e.g.
`lagrange_2d`/`lagrange_3d`) across two files and blur the leaf-vs-structural layering. So: **reject
the fold; keep topic files.**

Current inventory (lines; G2/G3 presence):

- **Per-algebra core / leaf:** `G2.lean` (235), `G3.lean` (354) — struct defs, mul/dot/wedge, basis,
  foundational leaf theorems. Stay as-is (they are the leaf layer).
- **Pure ℝ:** `Lagrange.lean` (28) — stays (dimension-independent identities).
- **One file, both dimensions:** `AlgebraLaws` (119), `Exp` (76), `GradeProjection` (78),
  `Measures` (79), `Trig` (132), `Sandwich` (420).
- **Split 2D vs 3D:** `Projection2D` (144) / `Projection` (200, **3D**); `Rotation` (208, **2D**) /
  `Rotation3D` (132); `Projection2DRotation` (208) / `ProjectionRotation` (388); `Versor2D` (109)
  (its 3D counterpart is folded into `Rotation3D`). Plus 3D-only `Cross`, `CrossStandardPosition`,
  `Contractions`, `Normalize`, `Predicates`, `Reflect`, `RotateComponents`, `StandardPosition`.

## Proposed rule (for maintainer sign-off — see Open questions)

1. **Filing rule:** a concept lives in ONE `Concept.lean` holding both dimensions **unless** a single
   dimension's proof is large enough to stand alone (soft threshold ~150–200 lines), in which case
   split into `Concept2D.lean` / `Concept3D.lean`. Under this rule the big ones legitimately stay
   split (`ProjectionRotation` 388, `Projection` 200, `Rotation` 208); the small/mixed ones stay
   unified.
2. **Naming convention:** a dimension-specific file is **always** suffixed `2D`/`3D`; a bare
   `Concept.lean` means "both dimensions." This fixes the asymmetry directly:
   - `Rotation.lean` (2D) → **`Rotation2D.lean`** (pairs with existing `Rotation3D.lean`).
   - `Projection.lean` (3D) → **`Projection3D.lean`** (pairs with existing `Projection2D.lean`).
   - `ProjectionRotation.lean` (3D) → **`ProjectionRotation3D.lean`** (pairs with
     `Projection2DRotation.lean`, which should become **`ProjectionRotation2D.lean`** for parallel
     ordering of the words).
   - Consider folding `Versor2D.lean` into a `Versor2D`/`Versor3D` pair, or leaving it (its 3D twin
     currently lives in `Rotation3D`) — a judgment call (Open question 2).

## Method (mechanical, verify-by-build)

1. `git mv` each file to its new name.
2. Update the root import list `proofs/GacalcProofs.lean` (all 25 topic imports are listed there) and
   every cross-file `import GacalcProofs.X` in siblings. Blast radius is small and known:
   `Projection` (→3D) has **5** dependents (`CrossStandardPosition`, `ProjectionRotation`, `Reflect`,
   `RotateComponents`, `StandardPosition`); `Rotation` (→2D) has **1** (`TrigEquiv`);
   `ProjectionRotation`/`Projection2DRotation` have none importing them. `lakefile`/`check.sh` do
   **not** hardcode module names, so no build-script edits.
3. If any concepts are to be *merged* (unify a split pair back into one file), move the theorems and
   reconcile `namespace`/`import` blocks; keep theorem names unchanged so nothing downstream breaks.
4. `make lean` green + `sorry`-free. The diff must be renames/moves + import-line changes only — no
   change to any theorem statement or tactic (that would be a different task).

## Sequencing

`tasks/lean-lift-theorem-statements-to-objects.md` rewrites many `G2.lean` statements. This task does
**not** touch `G2.lean`/`G3.lean` contents (they stay as the core files), so the two don't directly
collide — but if any topic *file* is both renamed here and edited there, do this reorg **first** (a
pure rename is cheap to rebase onto), then the lift. Note it when starting either.

## Decisions (resolved 2026-10-03, William Emerison Six <billsix@gmail.com>)

1. **Filing rule APPROVED:** one file per concept holding both dimensions, split into
   `Concept2D`/`Concept3D` **only** when a single dimension's proof is large enough to stand alone
   (~150–200-line soft threshold). (Not "always split", not "always unify".)
2. **`Versor2D.lean` stays as-is** — leave its 3D counterpart folded inside `Rotation3D.lean`; do
   NOT extract a separate `Versor3D.lean`.
3. **No merges of currently-split pairs** — the large split files (`ProjectionRotation` 388,
   `Projection` 200, `Rotation` 208, `Projection2DRotation` 208) stay split under the size rule; the
   work is renaming for naming consistency, not merging.

## Open questions

None blocking — ready to start on go-ahead (reorg sequenced before the G2 object-lift).
