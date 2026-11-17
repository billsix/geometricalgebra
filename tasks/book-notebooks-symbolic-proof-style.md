# Bring the book notebooks to the proof-projection model: symbolic, both sides shown, taught rotations only

**Status:** approved — open questions answered, not started
**Priority:** 3
**Difficulty:** 6
**Created:** 2026-11-17 (William Emerison Six <billsix@gmail.com>)
**Related:** `tasks/reference/book-notebook-teaching-style.md` (the standard this extends);
`tasks/reference/book-outline.md` ("Pedagogical principles");
`tasks/archive/2026/11/16/book-notebooks-teaching-style-sweep.md` (the previous sweep);
`tasks/proof-notebooks-student-math-notation-style.md` (the backfill of missing proof notebooks,
which should be written to this standard); `tasks/archive/2026/11/17/arrowheads-past-their-points.md` (the figures)

## BLUF

`book/docs/notebooks/proof-projection.py` was rewritten on 2026-11-17 with the maintainer, and it is
now the model for every book notebook. This task applies its rules to the other content notebooks,
draws a Graphviz graph of which proofs build on which and shows it on the book's first page, and writes
the "build only on what has been taught" rule into a reference doc and `CLAUDE.md`. Done means every
notebook listed below follows the rules, the graph renders in the HTML and PDF book, and the rule docs
are updated.

## Context

**Read first:** `book/docs/notebooks/proof-projection.py` (the model), then `book/docs/proof-projection.rst`
(its page), `tasks/reference/book-notebook-teaching-style.md` and `tasks/reference/book-outline.md`.

### The rules, as the maintainer set them on 2026-11-17

1. **Symbolic the whole time.** Every step is computed with symbolic coordinates, so each displayed
   result is a formula. Numbers appear in one cell, a list of pairs such as
   `values = [(a_1, 1), (a_2, 4), (b_1, 2), (b_2, 1)]` (a list, because `ty` rejects a `dict` passed
   to `subs`), and are used only to draw the figures.
2. **An "At the plot values:" cell follows a step result only when that result is drawn** in a figure.
   A substituted value nothing draws or uses has no purpose (the maintainer removed one for $R(e_1)$).
3. **Both sides before the difference.** Each check is three cells: the first formula, the second
   formula, then their difference, which shows $0$. With symbolic coordinates one check covers every
   value, so the separate "on these numbers" and "for any $a$" tiers collapse into one.
4. **One displayed value per cell.** A tuple as a cell's last expression does not render as math; end
   the cell on one value and put the next in its own cell (already in the teaching-style doc).
5. **Live ePiX figures for each step**, drawn from the symbolic results at the plot values (the
   `plot_point` helper in `proof-projection.py`; `book/figures/epix/_bootstrap_live.py` for the scene).
   Where arrows meet tip to tip, draw the result first and its parts after, so the parts' heads sit on
   top (`tasks/archive/2026/11/17/arrowheads-past-their-points.md`, decision 2).
6. **Rotations only through what the book has taught.** Use the rotation by an angle
   (`g2.Vector.rotate(θ)`, `book/docs/proof-rotate.rst`) or the rotation from one direction to another
   (`standardposition.rotation_from_to(from_vector, to_vector)`, `book/docs/proof-rotate-from-a-to-b.rst`,
   made public for this on 2026-11-17), with `inverse(R)` for the rotation back. Never define a new
   rotation taking a cosine and a sine unless it is unavoidable, and then say why in the notebook and
   report it to the maintainer.
7. **Build only on what the reader has already seen.** A construction uses results from earlier in the
   book, never later ones. `transforms.projection_rotation` is built from general projection (onto the
   plane $a \wedge b$) and the geometric product, so it cannot appear before both are taught;
   `versor_rotation` / `rotor_from_vectors` need the geometric product (`rotation-from-vectors`).

### The teaching order (from `book/docs/index.rst` and the pages' own toctrees)

Part I: `rotate` → its proofs `proof-rotate` (by an angle) then `proof-rotate-from-a-to-b` (direction
to direction, built from the first) → `geometric-product` → `projection` with `proof-projection` (built
on `proof-rotate-from-a-to-b`) → `product-from-projection` (the product from projection) →
`rotation-from-vectors` (the rotor from the product) → reflection, orthogonal, dual, …. Part II:
`three-dimensions`, `projection-rejection-3d` (+ `proof-projection-3d`, `proof-cross`), `frames-qr`
(+ `proof-reciprocal-frame`). Part III repeats the bootstrap: rotation → projection → rotation from
projection → product → projection from product → rotation from product. The graph deliverable below
makes this exact.

### Notebooks in scope (`book/docs/notebooks/`)

- Proof companions: `proof-rotate-from-a-to-b.py`, `proof-cross.py`, `proof-projection-3d.py`,
  `proof-reciprocal-frame.py`. (`proof-rotate.rst` has no notebook; the backfill task owns that.)
- Part I/II: `vector-addition.py`, `rotate.py`, `geometric-product.py`, `product-from-projection.py`,
  `rotation-from-vectors.py`, `levels-of-abstraction.py`, `three-dimensions.py`.
- Part III: the six `bootstrap-*.py`.
- Frames: `frame-qr-2d.py`, `frame-qr-3d.py`.
- Out of scope: the ten 16-line placeholders, and `notebooks/` (the demo notebooks).

Known violations found while writing this task:

- **Locally defined rotation functions** (`rg -n 'def rotate' book/docs/notebooks`): `rotate_cs` and a
  `rotate(v, theta)` wrapper around `v.rotate` in `proof-rotate-from-a-to-b.py`, and a `rotate`
  helper in `proof-cross.py` and all six `bootstrap-*.py`. Each is replaced by a taught rotation
  unless it is the construction the page itself builds. `proof-rotate-from-a-to-b.py` may be the one place
  where a cosine/sine rotation is unavoidable, since that chapter builds the direction-to-direction
  rotation without computing an angle (open question 2).
- **Tuples as a cell's last expression:** `bootstrap-product.py`, `bootstrap-projection.py`,
  `bootstrap-rotation.py`, `bootstrap-rotation-from-product.py`,
  `bootstrap-rotation-from-projection.py`, `proof-cross.py`, `proof-projection-3d.py`,
  `proof-rotate-from-a-to-b.py`, `frame-qr-2d.py`, `frame-qr-3d.py`
  (`rg -n '^\(.*, .*\)$' book/docs/notebooks`).
- **Bare subtractions without both sides:** every notebook in scope except `proof-projection.py`.

## Deliverables

1. **Each notebook** brought to rules 1–7, one commit per notebook or small group.
2. **The proof dependency graph:** a Graphviz `.dot` file in `book/docs/` with one node per proof /
   construction (rotation by an angle, rotation from a to b, projection, rejection, geometric product,
   rotor from vectors, cross product, reciprocal frame, the Part III steps, …) and an edge from each
   result to every result it uses, matching what the notebooks and pages actually call. Shown on the
   first page (`book/docs/index.rst`) for now. Rendering needs `sphinx.ext.graphviz` in
   `book/docs/conf.py` and the `graphviz` package (`dot`) in `entrypoint/04-install-docs.sh`; the image
   does not have it today (the sandbox does: graphviz 15.1.1). The PDF build needs the same.
3. **The rule docs:**
   - `tasks/reference/book-notebook-teaching-style.md`: rules 1–7.
   - `tasks/reference/book-outline.md` and `CLAUDE.md` ("Book: one name per operation…"): replace "checks
     … first on the values and then with symbolic coordinates" with the symbolic-throughout rule, and
     add rule 7 with a pointer to the graph.
   - A new or updated reference doc holding the teaching order and the graph's source of truth, so a
     later construction can be checked against what precedes it.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-17)

1. **One task** for all 19 notebooks, worked proof companions → Part III → Part I/II → frames, with a
   commit per notebook.
2. **`proof-rotate-from-a-to-b.py` keeps `rotate_cs`** as the one documented exception, with a
   sentence in the notebook saying why: the page builds the direction-to-direction rotation from a
   cosine and sine without computing an angle.
3. **The graph is a hand-written `.dot` file.**
4. **One node per named result** (projection and rejection separately), not one per page.

## Progress

- Shared helpers added: `nbdisplay.at_values(value, values)` (substitute plot values into a number or
  multivector) and `standardposition.in_plane(rotation, first, second, v)` (one coordinate-plane turn,
  now also used inside `project_sp`).
- Proof companions done: `proof-projection.py` (switched to `at_values`), `proof-rotate-from-a-to-b.py`,
  `proof-cross.py`, `proof-projection-3d.py`, `proof-reciprocal-frame.py`.
- Exceptions kept, each with its reason in the notebook: `proof-rotate-from-a-to-b.py`'s `rotate_cs`
  (decision 2); `proof-reciprocal-frame.py`'s space frame stays numeric (fully symbolic 3D round trips
  take minutes each).
