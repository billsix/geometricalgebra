# Add `/-! ### -/` navigation section headers to the four header-less Lean proof files

**Status:** done — 2026-10-28. `make lean` green (8958 jobs; completeness gate OK). 10 section headers
added across four files; purely additive (25 insertions, 0 deletions — no declaration moved).
**Priority:** 8
**Difficulty:** 2
**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

## BLUF

Four proof files had no `/-! ### … -/` navigation waypoints despite being 100–275 lines. Added headers
grouping the existing declarations by phase — a **purely additive** change (new comment lines only, no
reorder, no body touched); `git diff` is 25 inserted lines, 0 deletions, and `make lean` stayed green.

## Audit correction

The originating sweep flagged these four by grepping for `### ` headers only. On inspection
**`Rotation2D.lean` already had two `/-! ## … -/` section headers** (the "from a to b" and "rotor
sandwich" sections) — only its top ~100 lines (the `rot`/`fullAngleRotor`/`uvec` material) lacked one.
So Rotation2D got a single `## ` header matching its own style; the other three were genuinely
header-less and got `### ` headers matching `G2`/`G3`/`Projection3D`.

## What was added

- **`Rotation3D.lean`** (3 `### `): "The bisector and the from-vectors versor"; "Supporting leaves";
  "The versor–vector identities `R*a = |a|*h` and `b*R = |b|*h`".
- **`StudentTrigForms.lean`** (3 `### `): "𝒢₂ student forms"; "𝒢₃ student forms: perpendicularity,
  parallelism, area"; "𝒢₃: recovering dot/wedge from the trig form, and the triple product". (Headed by
  namespace + one natural G3 boundary — the topics are interleaved in source order, so a finer split
  would have required reordering, which was out of scope.)
- **`PlaneRotation3D.lean`** (3 `### `): "The plane rotor, and that it is a rotor"; "The angle theorem
  `R*v*R̃ = v⊥ + cos(θ)*v∥ + sin(θ)*(v ⌋ i)`"; "Corollaries: rotates by θ in-plane, and fixes the normal".
- **`Rotation2D.lean`** (1 `## `, matching its existing section style): "Rotation `rot θ`, the
  full-angle rotor, and the geometric product from rotation" over the previously un-headed top group.

## Deliverables

- The four files sectioned; `make lean` green; diff = additive header lines only. ✓

See also: `tasks/archive/2026/10/28/study-and-reorder-lean-file-structure.md`, `tasks/reference/lean-ga-proof-architecture.md`.
