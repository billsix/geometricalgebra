# 2D bootstrap: proj/rej named, base cases stated, dot and wedge as `a * proj_a(b)` and `a * rej_a(b)`

**Created:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)
**Done:** 2026-11-16
**Related:** `tasks/bare-2d-bootstrap-pages.md` (the Part III pages; still open);
`tasks/archive/2026/11/16/quarter-turn-as-named-base-case.md` (the same rules applied to the quarter turn; done);
`tasks/archive/2026/11/19/notebook-dot-wedge-projection-demo.md` (its Q2 was answered here);
`tasks/archive/2026/11/16/bootstrap-notebooks-show-derivations.md` (the follow-on for the Part III
notebooks; done)

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
4. **`tasks/archive/2026/11/19/notebook-dot-wedge-projection-demo.md`, its Q2:** answered with the left-multiplied form.
5. **Scope:** Part III only. Part I's projection pages are unchanged.
6. **The base case keeps the operation's name.** `P_{e₁}` is the base case of projection, as
   `r(v; π/2)` is the base case of rotation. The general projection can't be defined without it,
   so it is `proj_{e₁}`, stated directly as its own equation.

## How it went, in order

All on 2026-11-16, on branch `bootstrap-dot-wedge-from-proj-rej`.

1. **Research.** No open or archived task stated dot and wedge as `a * proj_a(b)` and
   `a * rej_a(b)`. The closest material was the mirror form `proj_b(a) * b = a · b` in
   `tasks/reference/dot-wedge-projection-rejection.md`, demonstrated in `notebooks/displayg2.py`.
   The Part III pages called the projection `P_a(b)` and never named the rejection. Lean's
   `proj a b` and `reject a b` already matched the wanted names. No Lean theorem stated
   `a * proj a b = a · b`.
2. **First draft and review.** The draft proposed replacing `P` with `proj` everywhere and making
   `a · b := a * proj_a(b)` Step 4's definition. The maintainer rejected both:
   - name every projection formula, and cite each version by equation number;
   - projection is defined for multivectors, so the vector forms are simple versions, and the
     identities are results, not definitions.
   These became the book rule in `tasks/reference/book-outline.md` and `CLAUDE.md`.
3. **The base-case question.** Asked whether Step 2's `P_{e₁}` should be renamed too, the
   maintainer answered that it is the base case of projection, as `r(v; π/2)` is of rotation, so
   it keeps the operation's name. This became the "Base case, then general case" section of
   `tasks/reference/reduction-to-standard-position.md`.
4. **Lean** (commit "Lean: a*proj_a(b) = a·b …"). Six theorems were added. The first two runs
   failed because `field_simp` did not find the nonzero denominator. That was fixed by stating the
   hypothesis in `ring_nf`'s normal form (see Verification).
5. **Mid-task request: the quarter turn.** The maintainer asked for a task to re-evaluate
   `r(v; π/2)` under the same rules, noting that it is also `v * e₁₂`. Filed as
   `tasks/archive/2026/11/16/quarter-turn-as-named-base-case.md`; its questions were answered the same day.
6. **Book and notebooks** (commit "Book Part III: name proj/rej …"). Steps 2, 4 and 5 and two
   notebooks were changed as listed under "What was done". Steps 3 and 6 needed nothing.
7. **Reference docs** (commit "reference: Part III names …"). The page → Lean table and the naming
   rules were added to `reduction-to-standard-position.md`, and the left-multiplied form to
   `dot-wedge-projection-rejection.md`.
8. **Mid-task request: the notebook style.** The maintainer pointed at "subtract and check zero"
   notebooks as the style they don't want. This was first misread as the Part I projection and
   rotation notebooks, and a task was filed for those (commit "tasks: add
   part-i-notebooks-derivation-check-style"). The maintainer then clarified, over several
   messages, that they meant the Part III "calculations" notebooks, including the cells this task
   added. Those should become notebooks with set values and live ePiX plots that a reader can
   change and rerun, with each check one subtraction and one result per cell. The task was renamed
   and rescoped to `tasks/archive/2026/11/16/bootstrap-notebooks-show-derivations.md`. Its questions were answered
   the same day.

## Noticed, not done

- Step 1 reads its base case `r(v; π/2)` off the general derivation and shares a label with
  `r(v; θ)`. Whether to reorder it is part of `tasks/archive/2026/11/16/quarter-turn-as-named-base-case.md`.
- The `[0, 0]` notebook cells this task added to `bootstrap-projection.py` and
  `bootstrap-product.py` use the style the maintainer later said they don't want. They are
  converted by `tasks/archive/2026/11/16/bootstrap-notebooks-show-derivations.md`.

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
