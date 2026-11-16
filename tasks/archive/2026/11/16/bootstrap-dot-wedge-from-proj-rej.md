# 2D bootstrap: proj/rej named, base cases stated, dot and wedge as `a * proj_a(b)` and `a * rej_a(b)`

**Created:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)
**Done:** 2026-11-16
**Related:** `tasks/bare-2d-bootstrap-pages.md` (the Part III pages; still open);
`tasks/quarter-turn-as-named-base-case.md` (the same rules applied to the quarter turn; proposed);
`tasks/notebook-dot-wedge-projection-demo.md` (its Q2 was answered here)

## What was done

The maintainer asked for three things in the Part III pages. The projection and rejection formulas
should be named `proj_a(b)` and `rej_a(b)`. The dot product should be shown as `a * proj_a(b)`
(equally `b * proj_b(a)`), and the wedge as `a * rej_a(b)`. These were done as follows.

- **Step 2** (`book/docs/bootstrap-projection.rst`):
  - A new section states the base cases `proj_{e₁}(b) = b₁ * e₁` and `rej_{e₁}(b) = b₂ * e₂`
    (`eq-bootstrap-projection-base`).
  - The definition became `proj_a = (R_a^{e₁})⁻¹ ∘ proj_{e₁} ∘ R_a^{e₁}`, with `rej_a` written the
    same way, citing the base cases. A remark notes that it gives the base cases back when `a`
    lies along `e₁`.
  - The rejection formula got its own label (`eq-bootstrap-rejection`).
  - `P` is gone from Part III.
- **Step 4** (`book/docs/bootstrap-product.rst`): the product's definition is unchanged. A new
  section, "Dot and wedge through projection and rejection", derives two results from Step 2's
  formulas, each cited by label:
  - `a · b = a * proj_a(b)`, `a ∧ b = a * rej_a(b)` and
    `a * b = a * proj_a(b) + a * rej_a(b)` (`eq-bootstrap-dot-wedge-proj-rej`);
  - the mirrors `b * proj_b(a) = a · b` and `b * rej_b(a) = −(a ∧ b)`
    (`eq-bootstrap-dot-wedge-mirror`).
- **Step 5** (`book/docs/bootstrap-projection-from-product.rst`): "The definition" became "The
  projection through the product". Both formulas are named, `proj_a(b) = (b · a) * a⁻¹` and a newly
  labelled `rej_a(b) = (b ∧ a) * a⁻¹` (`eq-bootstrap-rejection-product`), and each cites the Step 2
  version it equals.
- **Steps 3 and 6** needed no change: they use the coordinates `x`, `y` and already cite
  `eq-bootstrap-projection-coordinates`.
- **Lean:**
  - `proofs/GacalcProofs/Bootstrap2D.lean` gained `mul_proj_eq_dot`, `mul_reject_eq_wedge`,
    `mul_proj_symm`, `mul_reject_antisymm` and `mul_eq_mul_proj_add_mul_reject`.
  - `StandardPosition2D.lean` gained `reject_onto_x_axis`, the rejection twin of
    `proj_onto_x_axis`.
  - Each page cites the theorems it uses.
- **Notebooks:**
  - `bootstrap-projection.py` checks the base cases and the rejection formula.
  - `bootstrap-product.py` checks the three results and the two mirrors, using gacalc's
    `projected_onto` / `rejected_away_from`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-16)

The general rules are in `tasks/reference/book-outline.md` ("Pedagogical principles") and
`tasks/reference/reduction-to-standard-position.md` ("Base case, then general case"), with a pointer
section in `CLAUDE.md`.

1. **One name for every version.** Every projection formula is `proj_a(b)`, and every rejection
   formula `rej_a(b)`. Each version is a labelled equation, and each use cites it. A blanket
   rename of every `P` was declined as the framing; naming every formula covers it.
2. **Not definitions.** Projection and rejection are defined for multivectors onto blades
   (`MultiVectorBase.project` / `reject`, `P_B(A) = (A · B) * B⁻¹`). The vector forms are simple
   versions that later chapters replace. So Step 4 keeps its definition of the product and states
   the dot and wedge identities as results. A first draft that made them Step 4's definition was
   rejected.
3. **Mirror lines** are shown as named results.
4. **`tasks/notebook-dot-wedge-projection-demo.md`, its Q2:** answered with the left-multiplied form.
5. **Scope:** Part III only. Part I's projection pages are unchanged.
6. **The base case keeps the operation's name.** `P_{e₁}` is the base case of projection, as
   `r(v; π/2)` is the base case of rotation. The general projection can't be defined without it,
   so it is `proj_{e₁}`, stated directly as its own equation.

## Noticed, not done

- Step 1 reads its base case `r(v; π/2)` off the general derivation and shares a label with
  `r(v; θ)`. Whether to reorder it is part of `tasks/quarter-turn-as-named-base-case.md`.

## Verification

- `make lean` (run as its `podman run` line against the existing image): green. The axioms gate
  passed on 1071 declarations. There are four new `unnecessarySeqFocus` linter warnings on the
  `ext <;> …` lines of the two new coordinate proofs, the same style as the file's existing
  proofs.
  - The first attempt failed because `field_simp` did not see the denominator as nonzero.
    `ring_nf` writes it as `a.c1 ^ 2 + a.c2 ^ 2`, so a hypothesis of exactly that form is added
    before `field_simp`.
- `make format`: green (ruff, ty over `book/docs/notebooks`, the changelog guard).
- Every zero-check in the three changed notebooks was run as an `assert` in the container (9, 8
  and 7 single-line checks); all passed.
- `make docs` (run as its `podman run` line): green.
  - Sphinx reported no warnings for Part III.
  - The final LaTeX pass had no undefined references. First-pass "Reference … undefined" lines for
    the new labels resolved on the rerun.
  - No literal `:math:`/`:eq:` appears in the rendered Part III HTML.
  - The Step 2, Step 4 and Step 5 PDF pages were checked visually: `proj`/`rej` render as
    operator names and the equation links resolve.
- No `CHANGELOG.md` entry: no library change.
