# Formula cheat sheets for 𝒢₂ and 𝒢₃ at the front of the book

**Status:** ready — decisions recorded
**Priority:** 4
**Difficulty:** 5
**Created:** 2026-11-20 (William Emerison Six <billsix@gmail.com>)

## BLUF

Add two reference pages near the front of the book, one for 𝒢₂ and one for 𝒢₃. Each lists
the book's important operations, and each operation is a **chain of partial bindings**: start
coordinate-free in the most general form, then specialise one step at a time by the grades of the
arguments, then by the algebra's named components, and end in coordinates. The number of steps
varies per operation; three is typical, not required. Done means both pages build in
`make docs` (HTML + PDF, no overflow), each step is an equation that cites where the book teaches
it, and the page passes the notation rules in `CLAUDE.md` ("Math notation for readers").

## Context

- **The maintainer's request (2026-11-20, paraphrased).** A cheat sheet at the beginning, two of
  them (2D, 3D). Each formula comes coordinate-free and most generic first, then specific to its
  types, then in coordinates. Worked example, the dot product:
  1. Generic: from the geometric product by grade projection, `A · B = ⟨A * B⟩_{|r−s|}` for grades
     r and s (H&S p. 6, eqs. 1.21a–c; `MultiVectorBase.inner_product`).
  2. Vector · vector: `a * b` has grades 0 and 2 only, so `a · b = ⟨a * b⟩₀`.
  3. Coordinates: `a · b = a₁b₁ + a₂b₂` (+ `a₃b₃` in 𝒢₃).

  Think of the steps as partial bindings toward coordinates per type, not a fixed three. The
  geometric product itself opens each sheet: defined generically for 𝒢ₙ, then for 𝒢₂ / 𝒢₃ with
  each vector bound to its named components (`a = a₁e₁ + a₂e₂`), then the full product table in
  coordinates.
- **The operations the maintainer named:** grade projection, geometric product, reverse,
  inverse (by type only: vector, versor, bivector, …; there is no generic 𝒢₂ inverse in the
  library, see `CLAUDE.md` "Assessment / known issues" item 2), dot product, wedge product,
  project, reject, rotate from/to, uniform scale, dual.
- **Candidates found by scanning the repo** (which are in scope: Decisions 2–4):
  - in `MultiVectorBase` (`src/gacalc/base.py`): `scalar_product` (`A ∗ B = ⟨A * B⟩`),
    `magnitude` / `normalize`, `left_contraction` / `right_contraction`, `reflect`,
    `even_part` / `odd_part` (the grade involution split), `cosine` / `abs_sin` between vectors,
    `exp` (a bivector's exponential is a rotor), `versor_from_vectors` / `rotor_from_vectors` and
    the sandwich `R * v * R̃`, `angle` / `plane_of_rotation`, `conjugate`, `i(a, b)` (the unit
    bivector)
  - the measures in `src/gacalc/measure.py`: `area`, `volume`, `signed_area` (𝒢₂), `signed_volume`
    (𝒢₃)
  - the transforms in `src/gacalc/transforms.py`: `translate`, `scale_non_uniform`,
    `plane_rotation` (rotation by an angle in a plane)
  - per algebra: the quarter turn `v * e₁₂` and `Vector.rotate(θ)` (𝒢₂); `cross` (𝒢₃,
    `src/gacalc/vectorcalc.py`)
  - frames (`src/gacalc/frame.py`): `reciprocal_frame` (H&S p. 28, eq. 3.5)
  - Hestenes but **not in gacalc**: the commutator product `A × B = ½ * (A * B − B * A)` (H&S
    ch. 1; page not checked), and the general 𝒢₂/𝒢₃ inverse (proved only in
    `proofs/GacalcProofs/GeneralInverse.lean`)
- **Teaching order** (`tasks/reference/teaching-order-and-dependencies.md`): every page uses only
  results taught before it. A cheat sheet at the front shows results before they are taught, so
  it is a reference page, not a lesson (Decision 1).
- **Book conventions** (`CLAUDE.md` "Book: one name per operation…", and
  `tasks/reference/book-outline.md`): one name per operation across all its versions, every
  version a labelled equation, uses cite the version with ``:eq:`label` ``. Typeset vectors as
  `\vec{\mathbf{a}}`, blades as `\mathbf{e}_{12}`, explicit `*` for every product, parentheses
  only for application. Long `.. math::` blocks need `\\` and `&` at line breaks (the PDF overflow
  check fails `make docs` otherwise; `tasks/reference/book-and-docs-pipeline.md`).
- **Where the book starts:** `book/docs/index.rst` lists Part I starting at `hook`,
  `canonical-form`, `one-dimension`, ….

## Plan

1. Placement and scope are settled (Decisions).
2. For each operation, collect the equations the book already labels (grep `.. math::` labels in
   `book/docs/*.rst`) and the library definition (`src/gacalc/*.py`), and write its chain of
   bindings for 𝒢₂ and for 𝒢₃. Where a step has no labelled equation in the book, note it.
3. Write `book/docs/cheat-sheet-2d.rst` and `book/docs/cheat-sheet-3d.rst` (names to taste), add
   them to `index.rst`, and check every coordinate step against gacalc in a scratch run (the
   coordinates should be what `g2` / `g3` print for symbolic vectors).
4. `make docs`; look at both pages in the PDF; update `tasks/reference/book-outline.md`.

## Decisions

William Emerison Six <billsix@gmail.com>, 2026-11-20:

1. **Placement:** the very front of the book, before Part I, titled as reference cards. Each step
   links to the page that teaches it, so the sheet does not read as a lesson out of order.
2. **Scope:** include the repo-scan candidates gacalc implements and the book uses: the scalar
   product, magnitude and normalize, contractions, reflect, even/odd parts, cosine and sine
   between vectors, exp and rotors with the sandwich, rotation by an angle, area / volume /
   signed measures, translate and non-uniform scale, the 𝒢₂ quarter turn and `rotate(θ)`, the 𝒢₃
   cross product, and the unit bivector `i`. Drop any that clutter a sheet, and say which in the
   done-record.
3. **Reciprocal frame:** on both sheets.
4. **Hestenes operations gacalc does not implement** (the commutator product, the general
   multivector inverse): not in this task. They stay open for a future task.
5. **Forms:** each step cites the book's existing equation (and its Lean `twin:` where one
   exists). No new Lean theorems or notebooks, an exception to the "three forms" default because
   the sheet adds no new math. The coordinate steps are checked against gacalc in a scratch run.
6. **Each sheet stands alone**, repeating the generic (𝒢ₙ) steps, so either page prints by itself.
