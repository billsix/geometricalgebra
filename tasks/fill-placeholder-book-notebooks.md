# Fill five placeholder book notebooks: defining-g2, dual, one-dimension, reflection, relative-graph-paper

**Status:** open — questions answered 2026-11-19; ready to implement
**Priority:** 4
**Difficulty:** 7
**Created:** 2026-11-19 (William Emerison Six <billsix@gmail.com>)
**Related:** `tasks/notebook-dot-wedge-projection-demo.md` (blocked; it names the `projection` and
`projection-rejection-3d` stubs), `tasks/unify-demo-and-book-notebooks.md` (parked; demo vs book
notebooks), `tasks/proof-notebooks-student-math-notation-style.md`

## BLUF

Ten book notebooks under `book/docs/notebooks/` are 16-line stubs whose one code cell is `1 + 1`, and
each is pulled into the book by its page's toctree. This task writes real content for five of them:
`defining-g2`, `dual`, `one-dimension`, `reflection` and `relative-graph-paper`. It also drafts the
prose of their `.rst` pages, which today say "Placeholder — content to come". The other five stubs get
a follow-up task (see "Follow-up for the other five stubs"). The task is done when the five notebooks
follow the book's notebook style, `make docs` executes them without error, the five pages have Draft
prose, and the follow-up task exists.

## Context

Read first:
- `tasks/reference/book-notebook-teaching-style.md`: the cell-by-cell style every notebook follows.
  Its model is `notebooks/displaymv.py`, and its rule 6 says book notebooks stay symbolic, with numbers
  only in the plot-values cell, the figures and the plot-values `show_mult` tables.
- `tasks/reference/book-outline.md`: "Structural conventions", plus sections B (1D), D (graph paper),
  F (reflection), G (dual) and H (defining the algebra).
- `tasks/reference/teaching-order-and-dependencies.md`: each construction may use only results taught
  before it. Every step below is checked against the page order in `book/docs/index.rst`:
  hook, canonical-form, **one-dimension**, multiplication, trigonometry, sets, vectors-as-number-lines,
  **relative-graph-paper**, vector-addition, rotate, geometric-product, rotation-graph-paper,
  projection, product-from-projection, **reflection**, orthogonal, **dual**, **defining-g2**, …,
  then Part II (three-dimensions, blade-square-sign, projection-rejection-3d, frames-qr).
- `CLAUDE.md` ("Math notation for readers").
- `tasks/reference/contraction-and-dot-definitions.md`: how gacalc defines the dot product.
- `tasks/reference/book-and-docs-pipeline.md`: myst-nb executes book notebooks and fails the build on
  an error.

Current state, checked 2026-11-19:
- Every one of the five notebooks is the jupytext stub: a markdown title, the line "Placeholder
  notebook — content to come…", and the cell `1 + 1`.
- Each `.rst` page holds one placeholder sentence and the toctree. The exception is
  `relative-graph-paper.rst`, which already has a drafted "How we write coordinates" section and a
  TODO for the rest.
- The library pieces exist:
  - `gacalc.transforms.translate`, `uniform_scale`, `compose_intermediate_fns`, and
    `gacalc.functions.compose`;
  - `MultiVectorBase.dual(n)`, which computes `A * I⁻¹`;
  - `MultiVectorBase.reflect(across=…)` and `reflected_across`, which compute P_B(A) − P_B^⊥(A) for a
    blade B;
  - the graded 𝒢₂ types in `src/gacalc/g2.py`: `G`, `Scalar`, `Vector`, `Bivector`, `Versor`.
- Figures are live ePiX scenes built from `book/figures/epix/_scene2d.py` and `_scene3d.py`, imported
  in the notebook through `sys.path` (see `book/docs/notebooks/three-dimensions.py` for the pattern).
- Existing content that overlaps:
  - `notebooks/displaymv.py` covers the multiplication rules, "The basis blades", the grade parts
    and "A bivector and its dual" (in 𝒢₃).
  - `book/docs/notebooks/proof-cross.py` builds the cross product by standard position.

**Lean twins.** `CLAUDE.md` ("Every piece of math comes in three forms") expects Lean, symbolic
Python and prose for each result. Most of the Lean side already exists, so cite these theorems
(`twin:` comments) rather than re-proving them:
- 2D dual: `dual_perp_dot` (`proofs/GacalcProofs/Predicates2D.lean`) and the cosine form `dual_perp`
  (`StudentTrigForms.lean`).
- 3D: `dual_wedge_perp_left_dot` / `dual_wedge_perp_right_dot` (`Projection3D.lean`) and
  `cross_perp_left_dot` / `cross_perp_right_dot` (`Cross.lean`).
- Reflection: `reflectVec_eq` (`Reflect.lean`).

The one result likely to be new in Lean is the mirror in the plane B = −(reflection across B's
normal). Add it to `Reflect.lean`, checking first that no existing theorem already states it.

## Per-notebook spec

The maintainer's direction (William Emerison Six <billsix@gmail.com>, 2026-11-19) is given first for
each notebook. Where the math needed a correction, the correction follows.

### defining-g2 — the formal algebra, like `displaymv.py`

- Model it on `notebooks/displaymv.py`. Repeating its content here is wanted, not a defect.
- Cover the basis blades as constants; addition, subtraction and multiplication; the rules (R1)/(R2);
  and how `e₁ * e₂` resolves when it is plotted. That last item comes from the outline's §H.
- Name every type and show one example of each: `Scalar` (grade 0), `Vector` (grade 1), `Bivector`
  (grade 2), `Versor` (scalar + bivector), and the general `G`. Show which type each product has, for
  example: vector * vector is a `Versor`, and bivector * bivector is a `Scalar`.
- **Venn diagram at the top level.** The whole of 𝒢₂ is the outer region. Inside it are `Scalar`,
  `Vector` and `Bivector` as subsets, and `Versor` is a region that contains both `Scalar` and
  `Bivector`. `Vector` sits outside `Versor`.
  - Draw it in ePiX. That is the book's existing text-based figure pipeline, it renders to both HTML
    and the PDF, and `_scene2d.py` already draws circles. Graphviz cannot nest regions this way.
  - Make the outer region visibly larger than the union of the subsets, and label one element in the
    gap, such as `1 + e₁`. A general multivector belongs to none of the named types.
  - Caption detail: `0` lies in every one of these subspaces, and the types share only `0`.
  - Before using the word "versor", check how gacalc's `Versor` defines it (`src/gacalc/g2.py`). In
    the literature a versor is a product of invertible vectors. In 𝒢₂ every nonzero scalar-plus-
    bivector element is such a product, so the two meanings agree except at 0. Say this in one
    sentence.

### dual — the vector and its dual are perpendicular, by algebra

**2D, as the maintainer proposed, with one added step.** The proof works through associativity and
grades:

    a · (a I⁻¹) = ⟨a (a I⁻¹)⟩₀            — dot of two vectors is the grade-0 part of their product
                = ⟨(a a) I⁻¹⟩₀            — associativity
                = ⟨|a|² I⁻¹⟩₀             — a vector times itself is a scalar
                = |a|² ⟨I⁻¹⟩₀ = 0          — I⁻¹ is pure grade 2

So cos θ = 0 and θ = 90°. The added step goes **before** this chain. The angle formula, and the
definition of the dot as ⟨ab⟩₀, apply only to two vectors. So first show that `a I⁻¹` is a vector
(in coordinates it is a₂ * e₁ − a₁ * e₂, up to the sign convention). Then show it is nonzero whenever
`a` is, so that the cosine's denominator |a| * |a I⁻¹| is not 0. Use `dual(2)`, so the book and the
library share the convention `A * I⁻¹`.

**3D: the dual of a ∧ rej_a(b) is perpendicular to both a and b.**
- Correction to the framing: in 3D the dual of a *vector* is a bivector, not a vector, so "the angle
  between a vector and its dual" has no meaning there. The 3D claim is about the dual of a bivector,
  which is a vector.
- Let r = rej_a(b). Then a ⟂ r, so a ∧ r = a r, which gives a r = −r a. Let d = (a r) I⁻¹. It is a
  vector, because a bivector times the 3D pseudoscalar is grade 1. Show that first, as in 2D.
- Perpendicular to a:

      a · d = ⟨a a r I⁻¹⟩₀ = |a|² ⟨r I⁻¹⟩₀ = 0                  — r I⁻¹ is a bivector

- Perpendicular to r:

      r · d = ⟨r a r I⁻¹⟩₀ = −⟨a r r I⁻¹⟩₀ = −|r|² ⟨a I⁻¹⟩₀ = 0     — swap r a = −a r; a I⁻¹ is a bivector

- Perpendicular to b: b = proj_a(b) + r = λ a + r, so b · d = λ (a · d) + r · d = 0 by linearity.
- Also show that a ∧ b = a ∧ r. Then d is the dual of a ∧ b, which is the cross product. Link to
  `proof-cross` (which builds the same vector by standard position) rather than re-deriving it.
- Each line of the chains above becomes a markdown step with its reason, followed by a symbolic sympy
  cell that confirms it.

### one-dimension — y = m * x + b, first as high-school graphs, then along one direction

1. **The familiar graphs.** Build f = translate(b * e₁) ∘ uniform_scale(m) as a gacalc composed
   function, using `compose`. Plot several (m, b) pairs on ordinary x–y axes, the way students drew
   them in high school. Plot subsets: b = 0 with different slopes; m = 1 with different intercepts;
   then both varied. Draw one figure per idea.
   - The x–y plot draws input against output. The function itself acts on one direction, so say in
     the prose that the second axis is only how we draw it.
2. **Along one direction.** For x = −5, −4, …, 5, make one subplot each. The left side shows the input
   x * e₁ on a number line. The right side shows the output f(x * e₁) on a number line pointing the
   same way. The direction never changes; only the length and the sign do.
   - Lay the eleven panels out so that a student who turns their head sideways sees the output tips
     trace the familiar line from step 1. Say so in the notebook, and pose it as a prediction prompt
     before the reveal.
3. **Teaching order.** This page comes before vectors-as-number-lines, so here e₁ is "the direction
   of the number line". The outline's §B calls for vectors "showing implicitly what's happening".
   Keep the vector vocabulary light, and point forward to the vectors-as-number-lines page.

### reflection — 2D across a vector; 3D across a vector and across a plane

- **2D.** Reflect a vector across another vector with `reflected_across`. Draw the reflected vector,
  and show the projection and rejection parts. The `.rst` says "the same treatment as projection", so
  mirror the structure of `projection.py`'s sibling page, `proof-projection.py`.
- **3D.** First reflect across a vector. Then reflect across a plane B, given as a bivector.
- **Plane versus its dual: a correction.** "Reflect relative to the plane, or relative to the dual of
  the plane, and they are equal" is true only once the sign is accounted for:
  - With n = B I⁻¹ (B's normal), reflecting across n keeps n's component and flips the in-plane part.
    That is the reflection across the *line* n.
  - The mirror in the plane B does the reverse. So the mirror in B = −(reflection across n).
  - In sandwich form: B v B⁻¹ = n v n⁻¹, because I commutes with everything in 𝒢₃. The mirror in B
    is −n v n⁻¹ = −B v B⁻¹.
  - The notebook shows that P_B(v) − P_B^⊥(v), computed from the plane, equals −(P_n(v) − P_n^⊥(v)),
    computed from the normal. That makes the two different routes agree, which is the maintainer's
    teaching goal. It also shows the sign that a careless student would miss.
- The 3D parts go on the new Part II page `reflection-3d` (Decision 1); the same applies to `dual`, whose 3D part goes on `dual-3d`.

### relative-graph-paper — the order of transformations, read both ways

- Model this notebook on modelviewprojection's (github.com/billsix/modelviewprojection) sequence
  plots. Its `src/modelviewprojection/notebooksrc/plot2d.py` draws one figure per intermediate
  function, using `compose_intermediate_fns`. Its sections are "Composed functions, read bottom up"
  and "…read top down". The idea is explained in its book's `book/docs/ch09.rst` ("Reading
  transformations top-down" / "…bottom-up").
- Here, gacalc's own `gacalc.transforms.compose_intermediate_fns` exists for this purpose.
- Content: compose translate with another transform. For each composition, show two sequences of
  plots:
  - read one way, each step is relative to the standard (natural) basis;
  - read the other way, each step is relative to the relative graph paper that the earlier steps left
    behind.
- Both sequences end in the same final picture. The difference is only what each step is measured
  against.
- Keep the drafted "How we write coordinates" section of the `.rst`, and write the rest of the page.
- Rotation is taught later than this page, so the translate+rotate sequences go on `rotation-graph-paper` (Decision 2).

## Follow-up for the other five stubs

The maintainer's direction (William Emerison Six <billsix@gmail.com>, 2026-11-19): make a separate
follow-up task for the remaining placeholder notebooks. **Scaffold it before this task is archived**,
as `proposed — needs go-ahead`, and cross-link it from here. The stubs are:
- `canonical-form.py`
- `hook.py`
- `projection.py` (the page also includes the real `proof-projection.py`, so decide whether to fill
  this stub or drop it from the toctree)
- `projection-rejection-3d.py` (coordinate with the blocked `tasks/notebook-dot-wedge-projection-demo.md`)
- `vectors-as-number-lines.py`

## Plan

1. Answer the open questions, and record the decisions here with their rationale.
2. Write one notebook at a time, in this order: dual (pure algebra, no new figures), reflection,
   defining-g2 (the Venn figure), one-dimension, relative-graph-paper.
   - For each: run `tools/check_notebook_prose_width.py` and `ty`, and execute the notebook in the
     book build.
3. Draft each `.rst` page's prose with the "Draft. … maintainer's voice pass pending" note used on the
   other agent-drafted pages.
4. Run the gate: `make docs` (myst-nb executes every notebook) and `entrypoint/format.sh`.
5. Scaffold the follow-up task, rewrite this doc as a done-record, and archive.

## Decisions

Both made by William Emerison Six <billsix@gmail.com>, 2026-11-19. Each was the recommended option.
The reason for both is that the book's first page (`book/docs/index.rst`) promises every result uses
only results taught before it.

1. **The 3D halves of `dual` and `reflection` go on new Part II pages**, `dual-3d` and
   `reflection-3d`, each with its own companion notebook. Add them to the Part II toctree in
   `book/docs/index.rst` after `projection-rejection-3d`, and to the dependency graph on that page.
   The Part I pages `dual` and `reflection` stay in the plane and end with a link forward to these
   pages. (Rejected alternative: a "Looking ahead: space" section inside each Part I page, which would
   break that promise.)
2. **`relative-graph-paper` uses translate + uniform_scale only**, and shows both reading orders with
   those transforms. The modelviewprojection-style translate+rotate sequences go on
   `rotation-graph-paper` (and its notebook), which comes after `rotate`. (Rejected alternative: using
   rotate early as a picture only, ahead of its definition.)

## Open questions

None.
