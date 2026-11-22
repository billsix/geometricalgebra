# Reference cards: a separate 𝒢ₙ section, named values by kind, grade projections for parts

**Status:** done 2026-11-22
**Created:** 2026-11-22 (William Emerison Six <billsix@gmail.com>)

## What this did

The request (the maintainer's words): the 𝒢ₙ formulas should not be mixed in with 𝒢₂; the card should name its
scalars, vectors, bivector and versor instead of implying them; and the parts of a multivector should be
written with the grade-projection symbols, not subscripts.

- **`book/docs/cheat-sheet-gn.rst`** (new, first in the "Reference cards" toctree of `book/docs/index.rst`)
  holds each formula that is true in every dimension once: the product rules, grade projection, reverse,
  magnitude, inverse, dot, wedge, projection and rejection onto a blade, reflection, dual, and the
  scalar product and contractions that used to close each card's "Also in gacalc".
- **`cheat-sheet-2d.rst` and `cheat-sheet-3d.rst`** cite it and start each chain at "by kind". Each opens with
  its names by kind, every one defined even where no formula uses it: scalars, vectors built from the
  coordinates, the unit of area or volume `I = 1 * e_1 * e_2` (`* e_3`), a bivector
  `B = a ∧ b = a * rej_a(b)`, a versor `R = a * b = ⟨R⟩_0 + ⟨R⟩_2`, any multivector `A = ⟨A⟩_0 + …`, and in
  space the trivector `V = a ∧ b ∧ c = det(a, b, c) * e_1 * e_2 * e_3`.
- **Parts by grade projection.** `A_0`, `A_{12}`, `B_{12}`, `r_0`, `r_{12}` are gone; a part is `⟨A⟩_r`, and a
  vector keeps its coordinates `a_1`, `a_2` (decision 2). The grade-projection sections now give each part
  through the named vectors.
- **Unit planes are spelled as products** (`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2`, not `\mathbf{e}_{12}`),
  the form `tasks/spell-out-basis-blades-as-vector-products.md` settles on, so that task skips both cards.
- **Name clashes removed:** the space card's trivector is `V` (the reciprocal frame's `V` was the same thing),
  not `T`, which was also the translation `T_b`. The 𝒢ₙ page's `A`, `B` are any multivectors; the cards' `B`
  is the bivector.
- Where a row used components of `B`, it now uses `B = a ∧ b`: `v · B = (v · a) * b − (v · b) * a` and
  `v ∧ B = det(v, a, b) * e_1 * e_2 * e_3` in space, `|B| = |a_1 * b_2 − a_2 * b_1|`, `B^{-1} = −B / |B|²`,
  `B^* = a × b` (space), `B^* = a_1 * b_2 − a_2 * b_1` (plane), `V^* = det(a, b, c)`.
- `tasks/reference/book-outline.md` ("Reference cards") and the opening text of `book/docs/index.rst` describe
  the three cards.

## Decisions

William Emerison Six <billsix@gmail.com>, 2026-11-22: (1) the 𝒢ₙ formulas get their own page, first in the
toctree and cited by both cards; (2) a vector's coordinates keep their subscripts; (3) the space card gets the
same treatment in this task.

## Verification

The rewritten rows were checked in the container against gacalc's `g3` on a numeric example: `v · B` and
`v ∧ B` against the identities above, `B^{-1}`, `V^*` against `a ∧ b ∧ c`, and `B^*` against `a.cross(b)`. The
rest follow from the old rows by the substitutions listed. `make docs` built the HTML and PDF (exit 0; no
equation or table over 10 pt too wide), and the three cards were read in the rendered PDF.
