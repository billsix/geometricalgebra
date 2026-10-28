# Audit where each Lean declaration is defined and in what order; move each to its logical home, then reorder

**Status:** done — 2026-10-28. Both axes complete and `make lean`-verified (8958 jobs; completeness
gate OK). The durable within-file rubric now lives in `tasks/reference/lean-ga-proof-architecture.md`
("Within-file order of the algebra-core files"); this doc is the work record.
**Priority:** 7
**Difficulty:** 7
**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

## BLUF

Reorganized the from-scratch Lean proofs (`proofs/GacalcProofs/*.lean`) along two axes: (1) each
declaration's **logical home** (which file), and (2) the **order within** each file. A
**content-preserving** change — `make lean` stayed green and only relocations + `/-! ### -/` section
headers changed, no proof/statement/def body touched. Outcome: `dot`/`wedge` were consolidated into
`G2.lean` (Axis 1), and `G1`/`G2`/`G3` were normalized to one basis-first within-file shape (Axis 2);
the ~28 concept files were audited and already conformed, so were left unchanged.

## What was done

**Axis 1 — logical home.** `G2.dot` (from `Versor2D.lean`) and `G2.wedge` with its bilinearity
lemmas, the split `mul_eq_dot_add_wedge`/`mul_eq_wedge_of_perp`, `normSq_wedge_vec`, and the grade
lemmas `isBivector_wedge_of_isVector`/`wedge_isVector_isBivector_eq_zero` (from `Projection2D.lean`)
were moved into `G2.lean`, alongside `mul`/`reverse` — matching `G3`/`G1`, which always defined
`dot`/`wedge` in-file. Both are pure coordinate formulas depending only on `mul`/fields, so the move
kept `G2.lean`'s Mathlib-only import discipline and added no import. `Versor2D.lean` now holds only the
versor-from-vectors construction; `Projection2D.lean` only `proj`/`reject`/`reject_perp_dot` and the
sandwich-wedge lemmas.

**Axis 2 — within-file order.** `G1.lean`, `G2.lean`, and `G3.lean` were normalized to one top-to-bottom
shape: basis blades & grade constructors (right after the inner `namespace`) → elementary operations →
magnitude → dot/dual → the multiplication table (kept packed as a visual table) → dot leaf lemmas →
wedge leaf lemmas → coordinate-vector leaves → the split `a b = a·b + a∧b` → grade predicates with
their bridges → object-form facts — each under a `/-! ### -/` header. This put the basis constants
*before* the operations (they had been after, in both G2 and G3), reflecting the module docstring's
basis-first introduction. The full rubric is recorded in the architecture doc.

**The reorder tool.** The G1/G3 reorder was done by
`tasks/adhoc/study-and-reorder-lean-file-structure/reorder_lean.py`, not by hand: it splits a file into
declaration blocks, reassembles them per a per-file PLAN with fresh section headers, and **asserts the
multiset of declaration-block texts is unchanged** — the mechanical content-preservation proof.
Verified additionally by: identical declaration-name set before/after, identical non-header lines as a
multiset, idempotent re-run, and `make lean` green. (G2 had been reordered earlier, by hand, with the
same before/after declaration-set check.)

**Concept files — audited, unchanged.** All ~28 concept files were checked structurally and already
read docstring → def(s) → concept-grouped lemmas, dependency-correct (the "both-dimensions" files —
`AlgebraLaws`, `Trig`, `GradeProjection`, `Measures`, `Exp` — are parallel `namespace G2` /
`namespace G3` blocks, each itself def-then-lemma). None defines basis constants, so none had the
basis-after-operations problem the core files had. Reordering a coherent 300–700-line concept file
(`Sandwich` 734, `ProjectionRotation3D` 515, `CrossStandardPosition` 387) would be churn with real
breakage risk, so they were left as-is — the "don't manufacture churn / stop when the goal is met"
discretion, not a deferral.

## Decisions & judgment calls

- **Fold G1 into the same normalization** (maintainer's go-ahead): done — all three algebra-core files
  now share the one shape.
- **Section headers are a deliberate content addition** (new comment lines), the mechanism that makes
  the order legible; the diff is otherwise relocations only.
- **Two *content* improvements the maintainer surfaced while reviewing G2 were split out, not done here**
  (deferred by the maintainer): the basis constants' positional `⟨…⟩` literals → self-documenting
  `{ zero with … }` form (`tasks/lean-basis-constants-self-documenting.md`), and lifting G2's
  coordinate-leaking theorem conclusions (`dot_is_sym_part`/`wedge_is_antisym_part`) to G3's object-out
  form (`tasks/lean-g2-object-out-parity.md`). Both change def/statement bodies, so they are out of scope
  for a content-*preserving* reorder.

**Axis-1 residual (logged, not moved):** `Versor2D.magnitude_sq_vec` is a general magnitude *leaf*
(the arch-doc leaf index lists it under Magnitude leaves) whose home is arguably `G2.lean`; left in
place as a single debatable leaf used only by `Versor2D`.

## Files touched

- `proofs/GacalcProofs/G2.lean` — Axis 1 (dot/wedge moved in) + Axis 2 (basis-first, headers).
- `proofs/GacalcProofs/G1.lean`, `proofs/GacalcProofs/G3.lean` — Axis 2 (basis-first, headers).
- `proofs/GacalcProofs/Versor2D.lean`, `proofs/GacalcProofs/Projection2D.lean` — Axis 1 (dot/wedge moved out).
- `tasks/reference/lean-ga-proof-architecture.md` — the within-file-order rubric + the `dot`/`wedge` home note.
- `tasks/adhoc/study-and-reorder-lean-file-structure/reorder_lean.py` — the reorder tool; one-shot,
  `git rm`'d in this archive commit (recoverable from git history if a future reorder wants it; it is a
  generic block-reassembler + per-file PLANs, so it could be promoted to `tools/` instead).

## Follow-ups

- `tasks/add-section-headers-to-headerless-lean-files.md` — add `/-! ### -/` navigation headers to the
  four concept files that have none (`Rotation2D`/`Rotation3D`/`StudentTrigForms`/`PlaneRotation3D`);
  additive, no reorder.
- `tasks/lean-basis-constants-self-documenting.md` and `tasks/lean-g2-object-out-parity.md` — the two
  deferred content improvements above.
