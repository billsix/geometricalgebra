# 2D bootstrap: name proj/rej, and define dot and wedge as `a * proj_a(b)` and `a * rej_a(b)`

**Status:** proposed — needs go-ahead (Open questions below block implementation)
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)
**Related:** `tasks/bare-2d-bootstrap-pages.md` (the six Part III pages this edits; still open for
its next iteration), `tasks/notebook-dot-wedge-projection-demo.md` (blocked; the mirror-form
notebook demo), `tasks/reference/dot-wedge-projection-rejection.md` (the boxed theorem, mirror form)

## BLUF

The maintainer's request (2026-11-16): in the 2D bootstrap pages (book Part III), give the
projection and rejection formulas names, `proj_a(b)` and `rej_a(b)`, and define the dot product as
`a * proj_a(b)` (equally `b * proj_b(a)`) and the wedge as `a * rej_a(b)`. Done means: the
Part III pages use those names throughout. Step 4 states dot and wedge in those terms, and each
statement has a notebook check and a cited Lean theorem. `make lean`, `make format` and
`make docs` are green, and the changed PDF pages have been looked at.

## Context

### What already exists (research 2026-11-16)

- **Nothing in `tasks/` or `tasks/archive/` states dot and wedge as `a * proj_a(b)` and
  `a * rej_a(b)`.** The closest material is the **mirror form**, which multiplies the projection by
  the vector projected onto on the *right*:
  - `tasks/reference/dot-wedge-projection-rejection.md` boxes `proj_b(a) * b = a · b` and
    `rej_b(a) * b = a ∧ b`. It already uses the names `proj_b(a) = (a·b) b⁻¹` and
    `rej_b(a) = (a∧b) b⁻¹`. Its work record is
    `tasks/archive/2026/08/03/verify-dot-wedge-as-projection-rejection-products.md`, and the
    tests are in `tests/test_dot_wedge_projection_split.py`.
  - `notebooks/displayg2.py`, section "Dot and wedge are the parallel and perpendicular parts of
    the product", demonstrates that mirror form numerically/symbolically.
  - `tasks/notebook-dot-wedge-projection-demo.md` (blocked) wants the 3D counterpart. Its Q2 asks
    exactly the question this request answers ("projected onto **a**" vs the theorem's "onto
    **b**"); see Open question 4.
- **The 2D bootstrap pages** (`book/docs/bootstrap-*.rst`, built in
  `tasks/bare-2d-bootstrap-pages.md`) project `b` onto `a` everywhere:
  - **Step 2** (`bootstrap-projection.rst`) names the projection `P_{\vec{a}}` (definition
    `eq-bootstrap-projection-definition`, formula `eq-bootstrap-projection`) and `P_{e_1}`
    ("keep the x-coordinate"). **The rejection has no name**: it is "the same with keep the
    y-coordinate", and its formula `y * r(a; π/2) / |a|` appears only inline, in the check
    `P_a(b) + y * r(a; π/2)/|a| = b`.
  - **Step 4** (`bootstrap-product.rst`) defines `a * b = |a| * (x + y * e₁₂)` from Step 2's
    signed lengths `x` (along) and `y` (across), then *names* the scalar part the dot and the
    `e₁₂` part the wedge. `|a| * x` is already `a * proj_a(b)` and `|a| * y * e₁₂` is
    `a * rej_a(b)`, but the page never says so.
  - **Step 5** (`bootstrap-projection-from-product.rst`) has `P_a(b) = (b · a) * a⁻¹`
    (`eq-bootstrap-projection-product`) and an **unnamed, unlabelled** rejection
    `(b ∧ a) * a⁻¹ = (a₁ * b₂ − a₂ * b₁)/|a|² * r(a; π/2)`.
  - Steps 3 and 6 refer to "projection" and "rejection" in prose and use the coordinates `x`, `y`.
- **Lean already matches the naming.** `proofs/GacalcProofs/Projection2D.lean`:
  `proj a b := smul (dot b a / dot a a) a` (projection of `b` onto `a`, so `proj a b` is
  `proj_a(b)`), and `reject a b := mul (wedge b a) (inverse a)` (so `reject a b` is `rej_a(b)`).
  `Bootstrap2D.lean` has `proj_eq_dot_mul_inverse`; Step 2 cites `projectSP_eq_proj` and
  `rejectSP_eq_reject` in `StandardPosition2D.lean`. **No theorem states `a * proj a b = a · b`
  or `a * reject a b = a ∧ b`** (grep for `mul a (proj` / `mul a (reject` finds nothing).

### The math (for the implementer)

With `x`, `y` from `eq-bootstrap-projection-coordinates`:

- `proj_a(b) = x * a/|a| = (a₁ * b₁ + a₂ * b₂)/(a₁² + a₂²) * a`
- `rej_a(b) = y * r(a; π/2)/|a| = (a₁ * b₂ − a₂ * b₁)/(a₁² + a₂²) * r(a; π/2)`
- `a * proj_a(b) = |a| * x = a · b`: a vector times a vector along it is a plain number.
- `a * rej_a(b) = |a| * y * e₁₂ = a ∧ b`: a vector times a vector across it is pure area.
- `b * proj_b(a) = a · b` as well (the dot is symmetric), but
  `b * rej_b(a) = b ∧ a = −(a ∧ b)`. The wedge's mirror flips sign; the page should say so
  rather than let the reader assume the symmetry carries over.
- `a * b = a * (proj_a(b) + rej_a(b)) = a * proj_a(b) + a * rej_a(b)`, which is
  `a · b + a ∧ b` with no further work.

**Watch the circularity in Step 4.** Step 4 is where the product is *defined*, so "define dot as
`a * proj_a(b)`" needs the product of `a` with a vector *along* it and *across* it to be given
first, geometrically: along gives `|a|` times the signed length, across gives `|a|` times the
signed height times `e₁₂`. That is what the current `|a| * x` and `|a| * y` already are, so the
change is a restatement of the definition, not a new one.

## Plan (draft; depends on the Open questions)

1. **Step 2:** rename `P_{\vec{a}}` to `\operatorname{proj}_{\vec{a}}` (and `P_{e_1}`, per Q1).
   Give the rejection its own definition (`rej_{\vec{a}}`, "keep the y-coordinate", conjugated
   by the same rotation) and its formula as a labelled equation (`eq-bootstrap-rejection`). Keep
   the `proj + rej = b` check, written with the names.
2. **Step 4:** state the two halves as `a · b = a * proj_a(b)` and `a ∧ b = a * rej_a(b)` (where
   per Q2). Add the symmetric `b * proj_b(a)` line and the antisymmetric `b * rej_b(a)` line (per
   Q3), and show `a * b = a * proj_a(b) + a * rej_a(b)`.
3. **Step 5:** write the two results as `proj_a(b) = (b · a) * a⁻¹` and
   `rej_a(b) = (b ∧ a) * a⁻¹`, and label the rejection equation.
4. **Steps 3 and 6:** use the names wherever the prose says "the projection/rejection of `b` onto
   `a`". Steps 3 and 6 keep their `x`, `y` and rotation names `R_{\vec{a}}^{\vec{b}}`.
5. **Notebooks** (`book/docs/notebooks/bootstrap-projection.py`, `bootstrap-product.py`,
   `bootstrap-projection-from-product.py`): name the sympy bindings `proj_a_b` / `rej_a_b` and add
   zero-checks for each new identity in step 2, symbolically (`a * proj_a_b - a.dot(b) == 0`, and
   so on).
6. **Lean** (`proofs/GacalcProofs/Bootstrap2D.lean`): add and cite
   - `mul_proj_eq_dot`: `mul a (proj a b) = scalar (dot a b)`, for vectors with `dot a a ≠ 0`;
   - `mul_reject_eq_wedge`: `mul a (reject a b) = wedge a b`;
   - `mul_proj_symm` and `mul_reject_antisymm`, the `b * proj_b(a)` and `b * rej_b(a)` mirrors;
   - `mul_eq_mul_proj_add_mul_reject` (`a * b` splits into the two).
   Check that `Projection2D.lean` doesn't already hold an equivalent under another name before
   adding any of them.
7. **Figures:** check `boot_sp4`/`boot_sp5` and `boot_product` labels. Change any label that reads
   `P` to the new name. No new figure unless Q2's answer calls for one.
8. **Reference docs:** update `tasks/reference/reduction-to-standard-position.md` ("The 2D
   bootstrap in the book": the page → Lean table, the naming rules). Add a short "left-multiplied
   form" paragraph to `tasks/reference/dot-wedge-projection-rejection.md` relating
   `a * proj_a(b)` to the boxed `proj_b(a) * b`, so both forms are in one place.
9. **Gates:** `make lean` (no `sorry`, axioms gate), `make format`, run each changed notebook cell
   by cell, `make docs`; then look at the Step 2, 4 and 5 PDF pages. No `CHANGELOG.md` entry
   (book and proofs only, no library change).

## Open questions

1. **Notation:** replace `P_{\vec{a}}` with `\operatorname{proj}_{\vec{a}}` everywhere in Part III
   (including `P_{e_1}` → `\operatorname{proj}_{e_1}`), rather than introduce `proj` alongside
   `P`? *(Recommend: replace, so there is one name; Part I's pages are out of scope, see Q5.)*
2. **Where the dot/wedge statement lives in Step 4:** make it *the* definition (rewrite
   "The definition" so `a · b := a * proj_a(b)` and `a ∧ b := a * rej_a(b)` come first and
   `a * b = |a| * (x + y * e₁₂)` follows), rather than add a short section after the current
   definition that reads the two parts that way? *(Recommend: make it the definition, as you
   phrased it, with the along/across products stated first to avoid the circularity above.)*
3. **The mirror lines:** show both `b * proj_b(a) = a · b` and `b * rej_b(a) = −(a ∧ b)` on the
   Step 4 page? *(Recommend: yes, one line each. The sign flip is the wedge's antisymmetry, and
   showing it keeps a reader from assuming the dot's symmetry carries over.)*
4. **The blocked `tasks/notebook-dot-wedge-projection-demo.md`, its Q2** ("onto a" or "onto b"):
   should I record your phrasing here, `a * proj_a(b)` (project onto `a`, multiply by `a` on the
   left), as that task's answer? *(Recommend: yes. Its 3D demo would then show the left-multiplied
   form, cited to this task's new Lean theorems.)*
5. **Scope:** Part III only, leaving Part I's `proof-projection.rst` and
   `product-from-projection.rst` as they are? *(Recommend: Part III only. Part I's naming can be a
   separate decision.)*
