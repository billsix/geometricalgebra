# The 2D quarter turn as a named base case, with its product version

**Created:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)
**Done:** 2026-11-16, on branch `quarter-turn-and-bootstrap-notebooks`
**Related:** `tasks/archive/2026/11/16/bootstrap-dot-wedge-from-proj-rej.md` (applied the same
rules to projection and rejection); `tasks/bare-2d-bootstrap-pages.md` (the Part III pages; open)

## What was done

The maintainer asked whether rotation by 90° in 2D should follow the rules just applied to
projection: one name for the operation, the base case stated first under that name, every version
a labelled equation that each use cites. Their first thought was yes, since the quarter turn is
also a product with `e₁₂`. It was done for Part III:

- **Step 1** (`book/docs/bootstrap-rotation.rst`) now opens with "A vector by its length and
  angle", then "The base case: the quarter turn". That section states
  `r(v; π/2) = (−v₂, v₁)` directly from `cos(β + π/2) = −sin(β)` and `sin(β + π/2) = cos(β)`, with
  its own label `eq-bootstrap-quarter-turn`. "The rotation by an angle" then derives `r(v; θ)` and
  cites the base case. Before this, the quarter turn was read off the general derivation and
  shared the `eq-bootstrap-rotation` label with it.
- **Step 4** (`book/docs/bootstrap-product.rst`) has a new section, "The quarter turn is a
  product": `r(v; π/2) = v * e₁₂` (`eq-bootstrap-quarter-turn-product`), with the remark that
  `e₁₂` is the unit bivector, also called `i`. Step 4's own derivation of `a * rej_a(b)` now uses
  it for `a * r(a; π/2) = |a|² * e₁₂`.
- **Step 5** (`e₁₂ * a = −r(a; π/2)`) and **Step 6** (the one-sided rotation) cite the product
  version instead of multiplying it out again.
- **Lean:** `rot90_eq_mul_e12` (`IsVector v → rot90 v = mul v e_12`) in
  `proofs/GacalcProofs/StandardPosition2D.lean`. `rot90`'s doc comment now calls it the base
  case and points to the theorem; it used to contrast the swap with the product. Step 1 cites
  `rot90`, Step 4 cites the theorem.
- **Notebooks:** `bootstrap-rotation.py` checks the base case from the polar form;
  `bootstrap-product.py` checks `b * e₁₂` against `b.rotate_90_degrees()`.
- **Reference:** `tasks/reference/reduction-to-standard-position.md` has the two labels in the
  Part III naming rules, the rotation row of the base-case table, and the Step 1 row of the
  page → Lean table. Its note that Step 1 didn't yet follow the base-case rule was removed.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-16)

1. **Scope:** Part III only. Part I's `proof-rotate.rst` and `geometric-product.rst` were left as
   they are.
2. **Name in the product version:** `v * e₁₂`, with a one-line remark that `e₁₂` is also called
   `i`. `I₂` was not introduced.
3. **Placement:** the product version first appears in Step 4, where `e₁₂` is introduced.

The ordering constraint behind decision 3: the product doesn't exist until Step 4, so the
coordinate form has to be Step 1's base case and `v * e₁₂` a later version, just as Step 5's
`(b · a) * a⁻¹` is a later version of `proj_a(b)`.

## Verification

- `make lean` (run as its `podman run` line against the existing image): green. The axioms gate
  passed on 1072 declarations. No new warnings.
- `make format`: green.
- Both changed notebooks run with every single-line check an `assert`: 7 and 9 checks, all pass.
- `make docs` (its `podman run` line): green. No undefined references in the final LaTeX log and no
  Sphinx warnings for Part III. The Step 1 and Step 4 PDF pages were checked visually.
- No `CHANGELOG.md` entry: book and proofs only.
