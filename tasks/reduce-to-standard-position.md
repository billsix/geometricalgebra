# Reduction to standard position: define project/reject from trusted simpler ops via change-of-frame

**Status:** in progress — Lean + Python + book draft done; the book still needs the maintainer's voice pass
**Priority:** 6
**Difficulty:** 7
**Created:** 2026-09-30 **Updated:** 2026-09-30 (William Emerison Six <billsix@gmail.com>)

> **Naming:** "bootstrap" was rejected; the theme is **reduction to standard position** (synonym:
> *frame reduction*). Derived-operation variants carry a **prime** — Lean would write `proj'`/`reject'`
> alongside canonical `proj`/`reject`, Python uses a `_sp` suffix (`'` is not a legal identifier
> character). The prime echoes `crossproduct.tex`, which already primes the transformed vectors
> (`a'`, `a''`, `b''`…): a prime means "the same object, reached by the derived route."

## BLUF

This established **reduction to standard position** — defining or justifying a hard operation from
already-trusted simpler ones by a change-of-frame (rotate the figure into a standard frame, do the
easy version, rotate back) — as a named theme of the project. Scope for this first pass was
**`project` and `reject` only**: once you have those you can split any vector `a = a∥ + a⊥` relative
to `b`, whence `ab = a·b + a∧b` (the geometric product of two vectors) and thence rotation. The
rotations are **elementary coordinate-plane rotations, not versors** — using a versor would be
circular, since a versor is itself a geometric product and the point is to bootstrap the product
from operations trusted independently of it. Delivered in Lean (the justification + explicit
alignment), Python (`project_sp`/`reject_sp`), a reference doc, a `CLAUDE.md` pointer, and a drafted
book page + notebook. What remains is the maintainer's voice pass on the book draft.

## Decisions (2026-09-30, William Emerison Six <billsix@gmail.com>)

1. **Lean first** — the definitions and justification were proven in Lean before the book or code,
   so Lean certifies the equivalence to the Hestenes formula.
2. **Scope = `project` and `reject` only.** They suffice: `a∥ = project(a onto b)` is parallel to `b`
   (so `a∥ b = a·b`, a scalar), `a⊥ = reject(a from b)` is perpendicular (so `a⊥ b = a∧b`, a
   bivector), hence `ab = a·b + a∧b` — the grade-1×grade-1 product; the arbitrary-multivector product
   would need bilinear extension on top.
3. **Name = "reduction to standard position"**; derived variants carry a prime (see the naming note).
4. **Scan everything** (Lean, book, code, notebooks); the Sphinx book is the exemplar of the
   reduce-to-coordinates style.
5. **Elementary plane rotations, not versors** (maintainer correction — see History). The rotate step
   uses the high-school 2D rotation applied to one coordinate plane at a time, so the bootstrap of the
   geometric product from projection/rejection stays non-circular.

## The archetype — multivariate-math/proofs (read-only inspiration)

`/foo/opt/multivariate-math/proofs/crossproduct.tex` (hand-written LaTeX) derives the cross product
by change-of-frame: rotate `a` onto the x-axis by composing plane rotations (`:70-173`), apply the
same maps to `b` (`:177-182`), compute with trusted 2D steps in the aligned frame (`:228-332`),
compose the inverse rotations to bring the result back (`:335-417`), and rescale (`:419-434`). The
2D/3D building blocks (`Rotate2D90`, `Rotate3DToXY`, …) are in `multivariatebasics.tex`.

## What was delivered

**Lean** (`proofs/GacalcProofs/StandardPosition.lean`, gate-verified `sorry`-free):
- `rotXY`/`rotXZ` — elementary plane rotations as procedures on a vector's components (rotate the two
  in-plane components, leave the perpendicular one); their linearity (`rotXY_smul`/`rotXY_sub`/
  `rotXZ_smul`) and orthogonality (`rotXY_preserves_dot`/`rotXZ_preserves_dot`, when `cos²+sin²=1`).
- The justification: `proj_rotXY_equivariant`/`proj_rotXZ_equivariant`/`vecReject_rotXY_equivariant`
  — projection and rejection commute with a plane rotation.
- The explicit alignment: `rotXY_aligns_xy` (`b ↦ (k,0,b₃)`), `rotXZ_aligns_xz` (`(k,0,b₃) ↦ (m,0,0)`),
  `rotate_b_to_e1` (the composite `b ↦ |b|·e₁`), and `rotate_b_to_e1_magnitude`, which states it in
  terms of the actual magnitudes (`k = magnitude (vec b₁ b₂ 0)`, `m = magnitude (vec b₁ b₂ b₃)`) via
  `magnitude² = normSq` — no raw `√` or coordinate sums; the abstract-square `rotate_b_to_e1` is the
  algebra engine underneath.
- The payoff (versor-free): `mul_proj_eq_dot` (`a (proj_a b) = (b·a)·1`) and
  `mul_eq_proj_dot_add_reject_wedge` (`a b = (a·b)·1 + a∧b`), the wedge half reusing `plane_eq_wedge`.
- Supporting general lemmas `AlgebraLaws.mul_sub` and `Sandwich.sandwich_sub`.

**Python** (`src/gacalc/standardposition.py`): `project_sp`/`reject_sp` implement the same elementary
rotations; `tests/test_standardposition.py` (5 tests, passing) assert they equal the canonical
`projected_onto`/`rejected_away_from`, numerically and symbolically.

**Docs:** the reference doc `tasks/reference/reduction-to-standard-position.md` (the theme, the
`crossproduct.tex` archetype, the non-circularity argument, the naming convention); a `CLAUDE.md`
bullet accepting primed standard-position duplicates alongside the canonical Hestenes definitions;
and the repo scan `tasks/adhoc/reduce-to-standard-position/` (`ideas.md` + the raw `data/scan.txt`).

**Book (DRAFT, for the maintainer to refine):** `book/docs/proof-projection.rst` (the proof page, in
the maintainer's voice, modelled on `proof-rotate.rst`) + `book/docs/notebooks/proof-projection.py`
(the calculation notebook, which runs `project_sp` and was verified to execute), both registered in
`projection.rst`'s toctree. Figure spots are left as `.. TODO`; not built with `make docs`.

## History — the versor detour (why the correction)

The first Lean cut justified standard position with the **versor sandwich** (reusing the existing
`Sandwich`/`versorFromVectors` machinery): equivariance under a sandwich, primed `proj'`/`reject'`
via a conjugate-back round-trip. The maintainer flagged this as circular for the bootstrap goal — a
versor is a geometric product, so it cannot be used to *build* the geometric product — and asked for
elementary coordinate-plane rotations instead. The versor version was replaced with the
`rotXY`/`rotXZ` construction above, and the versor-specific round-trip lemmas were removed
(`sandwich_sub` and `mul_sub` were kept as generally-useful lemmas).

## Overlap (cross-referenced, not duplicated)

- `tasks/lean-proof-rotation-from-scratch.md` — reduces 3D to 2D via the versor sandwich, a
  complementary approach.
- `tasks/notebook-dot-wedge-projection-demo.md` — dot = projected product, wedge = rejected (proved
  in `tasks/reference/dot-wedge-projection-rejection.md`); a related display task.

## Remaining

- The maintainer's voice pass on the book draft (and real figures, and a `make docs` build check).
- Optional follow-ons from the ideas list: a 3D projection-rejection book page (B2), cross-links to
  `rotate.rst` (B3). No decisions block them.
