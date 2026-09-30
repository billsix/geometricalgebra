# Reduction to standard position (frame reduction) — a construction theme

*Durable knowledge. States what the theme IS and why it's sound; the work that introduced it is
tracked in `tasks/reduce-to-standard-position.md`.*

## What it is

**Reduction to standard position** (synonym: *frame reduction*) computes or justifies a hard
operation by three steps:

1. **Rotate** the figure into a convenient ("standard") frame — typically so one vector lands on a
   coordinate axis (`e₁`) or in a coordinate plane (`e₁₂`).
2. **Do the easy version** there, using only operations already trusted in that frame (a 2D
   projection, a known 90° rotation, reading off a coordinate).
3. **Rotate the result back** by the inverse rotation.

It is the geometric-algebra form of the classic "place it in standard position, WLOG" move a
student meets for angles and conics. The primary/canonical definitions in gacalc stay the
Hestenes-derived ones (`project = (A·B)B⁻¹`, etc.); the standard-position versions are **deliberate
duplicates** that build understanding and cross-check the canonical formula.

## The rotations are ELEMENTARY plane rotations — NOT versors (this is the whole point)

The rotate-to-standard-position step uses **elementary coordinate-plane rotations** — the
high-school 2D rotation `(x, y) ↦ (x cosθ − y sinθ, x sinθ + y cosθ)` applied to one coordinate
plane at a time, leaving the perpendicular component alone ("break the vector into its components,
rotate the plane, add the axis component back"). It does **not** use versors or the geometric-product
sandwich `R x R⁻¹`.

This matters: a versor **is** a geometric product, so rotating with a versor and then "bootstrapping"
the geometric product from projection/rejection would be **circular**. An elementary plane rotation is
trusted from precalculus, independently of the GA product, so the bootstrap is genuinely non-circular.
(An earlier draft used versors because that machinery already existed in the Lean tree; the maintainer
corrected it — 2026-09-30.)

## Naming and the prime convention

The theme is "reduction to standard position." The derived-operation variants are marked with a
**prime**: in Lean the plane rotations are `rotXY` / `rotXZ` and the derived operations carry the
theme; in Python a `_sp` suffix stands in (`project_sp` / `reject_sp`), since `'` is not a legal
identifier character. The prime echoes how the matrix-math proof
`multivariate-math/proofs/crossproduct.tex` already primes the successively transformed vectors
(`a'`, `a''`, `b''`, …): a prime means "the same object, reached by the derived route." (The theme was
informally called "bootstrapping" during design; that term was dropped.)

## The archetype (the pattern to imitate)

`multivariate-math/proofs/crossproduct.tex` (hand-written LaTeX, not code) derives the cross product
exactly this way: rotate `a` onto the x-axis by composing plane rotations (`:70-173`), apply the
**same** rotation to `b` (`:177-182`), compute with trusted 2D steps in the aligned frame
(`:228-332`), compose the **inverse** rotations to bring the result back (`:335-417`), and rescale
(`:419-434`). The 2D/3D building blocks (`Rotate2D90`, `Rotate3DToXY`, …) are in
`multivariatebasics.tex`.

## Why it is sound (and not circular)

The method is valid because **projection and rejection commute with a plane rotation** (are
rotation-equivariant). This is machine-checked in `proofs/GacalcProofs/StandardPosition.lean`:

- `proj_rotXY_equivariant` / `proj_rotXZ_equivariant`: `proj (R a) (R b) = R (proj a b)` for a plane
  rotation `R` (`rotXY`/`rotXZ`, when `cos² + sin² = 1`, proved via `rotXY_preserves_dot`).
- `vecReject_rotXY_equivariant`: the same for the vector rejection `b − proj_a b`.

Equivariance is exactly the statement "doing it in the rotated frame and rotating back = doing it in
place," so you may **WLOG** rotate `b` to a coordinate axis, compute, and rotate back. The explicit
alignment `rotate_b_to_e1` composes `rotXY` (zeroing `b_y`) then `rotXZ` (zeroing `b_z`) to send `b`
to `|b|·e₁` — the standard position — with the `(cos, sin)` read off `b`'s coordinates.

**Non-circular:** the rotations are elementary (precalculus), not the GA product. So one may then
*define* the dot and wedge — and hence the vector geometric product `ab = a·b + a∧b` — from
`project`/`reject`, because `a = a∥ + a⊥` with `a∥` ∥ `b` (⟹ `a∥b = a·b`, scalar) and `a⊥` ⊥ `b`
(⟹ `a⊥b = a∧b`, bivector). The canonical Hestenes formula is proven to agree, so the derived route is
trusted for matching it, not assumed. This yields the grade-1×grade-1 product; the
arbitrary-multivector product needs bilinear extension.

## What is proven vs. still open (as of 2026-09-30)

All in `proofs/GacalcProofs/StandardPosition.lean` (gate-verified, `sorry`-free):

- **Elementary plane rotations:** `rotXY`/`rotXZ` (procedures on the components), their linearity
  (`rotXY_smul`/`rotXY_sub`/`rotXZ_smul`) and orthogonality (`rotXY_preserves_dot`/`rotXZ_preserves_dot`,
  when `cos²+sin²=1`).
- **Equivariance (the justification):** `proj_rotXY_equivariant`, `proj_rotXZ_equivariant`,
  `vecReject_rotXY_equivariant`.
- **Explicit alignment:** `rotXY_aligns_xy` (`b ↦ (k,0,b₃)`), `rotXZ_aligns_xz` (`(k,0,b₃) ↦ (m,0,0)`),
  `rotate_b_to_e1` (the composite `b ↦ |b|·e₁`), with `k`,`m` supplied via their squares.
- **Product from projection/rejection:** `mul_proj_eq_dot` (`a (proj_a b) = (b·a)·1`) and
  `mul_eq_proj_dot_add_reject_wedge` (`a b = (a·b)·1 + a∧b`) — the maintainer's "project+reject build
  the product" claim, machine-checked. Versor-free.
- The Python twin (`src/gacalc/standardposition.py`, `project_sp`/`reject_sp`) implements the same
  elementary rotations and is asserted equal to canonical `projected_onto`/`rejected_away_from` in
  `tests/test_standardposition.py`.
- Supporting lemmas in their homes: `AlgebraLaws.mul_sub`, `Sandwich.sandwich_sub`.

- **Still open (follow-up):** a `√`-wrapper instantiating `k = √(b₁²+b₂²)`, `m = |b|` in
  `rotate_b_to_e1`; and the book + notebook presentations (the Sphinx book is the intended best home —
  see the task's ideas list, items B*/N*).

## Where it belongs

Lean first (it certifies the equivalence), then the "Geometry 2" book (`book/docs/`, the reduce-to-
coordinates exemplar — proof pages in separate `.rst`, calculations in the companion notebooks), then
optionally duplicate primed definitions in the code. See `tasks/reduce-to-standard-position.md` for the
per-subsystem ideas list and the decision log.

## See also

- `tasks/reference/lean-ga-proof-architecture.md` — the sandwich/projection lemmas this builds on.
- `tasks/notebook-dot-wedge-projection-demo.md`, `tasks/reference/dot-wedge-projection-rejection.md`
  — the related "dot = projected product, wedge = rejected" result.
- `tasks/lean-proof-rotation-from-scratch.md` — the other reduce-3D-to-2D thread (via the versor
  sandwich + `a∧b` plane), complementary to this coordinate-frame reduction.
