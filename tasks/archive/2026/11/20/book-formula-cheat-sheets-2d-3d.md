# Formula cheat sheets for 𝒢₂ and 𝒢₃ at the front of the book

**Created:** 2026-11-20 (William Emerison Six <billsix@gmail.com>) · **Done:** 2026-11-20

Two reference cards, `book/docs/cheat-sheet-2d.rst` ("Reference Card: The Plane") and
`book/docs/cheat-sheet-3d.rst` ("Reference Card: Space"). They sit in an unnumbered "Reference
cards" toctree before Part I in `book/docs/index.rst`, and the opening paragraph of the index
says they are for looking things up. Each operation is a chain of partial bindings:
1. the 𝒢ₙ form;
2. by the kinds of argument (vectors, a bivector, a trivector, a versor);
3. named components;
4. coordinates.

There are as many steps as the operation needs. Each chain ends with "Taught in" links to its
pages and labelled equations. How the cards fit the book: `tasks/reference/book-outline.md`
("Current reading order").

## The request (2026-11-20, paraphrased)

The maintainer asked for two cheat sheets at the beginning of the book, one each for 2D and 3D.
Each formula would go from coordinate-free and most general, to specific for its types, to
coordinates. The example was the dot product: grade projection of the geometric product, then
vector · vector as `⟨a * b⟩₀` (the product of two vectors has grades 0 and 2 only), then
`a₁ * b₁ + a₂ * b₂`. The steps are a sequence of partial bindings, not always three. The
geometric product opens each sheet, generic for 𝒢ₙ and then specific to 𝒢₂ / 𝒢₃ with named
components.

## Decisions

William Emerison Six <billsix@gmail.com>, 2026-11-20:

1. **Placement:** the very front, before Part I, as reference cards linking to the teaching pages.
2. **Scope:** the operations named in the request, plus the repo-scan candidates gacalc implements:
   - the scalar product, magnitude, contractions and reflect;
   - even/odd parts, cosine and sine, and exp, rotors and the sandwich;
   - rotation by an angle, the measures, translate and non-uniform scale;
   - the 𝒢₂ quarter turn and `rotate(θ)`, the 𝒢₃ cross product, and the unit bivector.
3. **The reciprocal frame:** on both sheets.
4. **Not in this task:** Hestenes operations gacalc does not implement (the commutator product,
   the general multivector inverse). They stay open for a future task.
5. **Sources:** each step cites the book's existing equation. There are no new Lean theorems or
   notebooks, an exception to the "three forms" default, since the sheet adds no new math. The
   coordinate steps were checked against gacalc.
6. **Standalone sheets:** each sheet repeats the generic steps.

## What was done

- **Operations on both cards**, in this order:
  - the geometric product (the 𝒢ₙ rules, the basis products, `a * b = a · b + a ∧ b`, coordinates);
  - grade projection, the reverse and magnitude;
  - the inverse, by type only, with no general formula (Decision 4);
  - the dot product (Hestenes' `Σ ⟨⟨A⟩_r * ⟨B⟩_s⟩_{|r−s|}`, vector · vector, vector · bivector);
  - the wedge product;
  - angle, area and the unit bivector `i(a, b)`;
  - projection and rejection, then reflection;
  - rotation: by an angle, and from `a` to `b` with the versor `R = b * a + |a| * |b|`;
  - the dual;
  - scaling (uniform and per axis) and translation;
  - the reciprocal frame.
- **3D only:** the cross product, volume and the signed volume (`det`), a vector ∧ a bivector, the
  plane forms of projection, rejection and reflection (`ref_B(v) = −B * v * B⁻¹`), and the rotor
  `R = cos(θ/2) − sin(θ/2) * i` with `v ↦ R * v * R̃`.
- **Where the chain stops short of coordinates:** projection onto a general plane, because the
  general-`B` coordinates fill several lines. The card gives the `(v · B) * B⁻¹` form, then the
  coordinate plane `e₁₂`. A general 3D multivector is written by grade parts, `A = A₀ + a + B + T`,
  instead of eight coefficients.
- **Not taught in the book:** even/odd parts, `exp`, the scalar product and the left and right
  contractions. They are in a last "Also in gacalc" section on each card, linked to their API
  entries (`:py:meth:`), so they are listed without implying a teaching page. Nothing from
  Decision 2 was dropped.
- **Notation:** the scalar product is written `⟨A * B⟩₀` with no `∗` symbol of its own. In
  print, `\ast` looks like the `*` that means the geometric product everywhere else
  (`CLAUDE.md` "Math notation for readers"). Equation citations read "page, equation (N)", not
  "((N))".
- **Verification harness:** `tasks/adhoc/book-formula-cheat-sheets-2d-3d/verify_cheat_sheets.py`
  ran 67 checks, one per formula on the cards, each comparing gacalc (`Gn`, `g2`) against the form
  as written. It started at 65/67: the two `exp` checks need a positive angle, since `exp`
  computes `cos(|A|) + sin(|A|) * A/|A|`. After that change, 0 failed. The script was one-shot
  and was removed in the archive commit; get it back with
  `git log --all -- tasks/adhoc/book-formula-cheat-sheets-2d-3d/verify_cheat_sheets.py`.
- **Book build:** `make docs` (the `docs.sh` run) reported 0 too wide and 0 too tall. Every
  `:doc:` and `:eq:` target was checked to exist before the build. Looked at the card pages
  (9–16 of the PDF).
- **Layout:** in the PDF the cards are sections 2.1 and 2.2, inside the index page's "How the
  results build on each other" chapter. That is the book's existing LaTeX structure (Part I's
  pages are also numbered 2.x), not something the cards introduced.
- **Font warnings:** the build's U+007F "Missing character" lines went from about 41 to 48. They
  are the same harmless skew-character lookup for vector accents
  (`tasks/archive/2026/11/17/notebook-text-vector-notation-matches-output.md`); the cards add
  more `\vec{\mathbf{…}}`.
