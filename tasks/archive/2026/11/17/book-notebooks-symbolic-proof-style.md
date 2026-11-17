# Bring the book notebooks to the proof-projection model: symbolic, both sides shown, taught rotations only

**Created:** 2026-11-17 (William Emerison Six <billsix@gmail.com>)
**Done:** 2026-11-17, on branch `book-notebooks-symbolic-proof-style`
**Related:** `tasks/reference/book-notebook-teaching-style.md` ("Symbolic notebooks", the standard);
`tasks/reference/teaching-order-and-dependencies.md` (the build-on-what-came-before rule and the
graph); `tasks/archive/2026/11/17/arrowheads-past-their-points.md` (the figures' arrowheads);
`tasks/proof-notebooks-student-math-notation-style.md` (the backfill of missing proof notebooks,
to be written to this standard)

## What was done

`book/docs/notebooks/proof-projection.py` was rewritten with the maintainer on 2026-11-17 into the
model for every book notebook. This task applied its rules to the other 19 content notebooks, drew
the graph of which results build on which on the book's first page, and wrote the rules down.

### The rules (William Emerison Six <billsix@gmail.com>, 2026-11-17)

1. Symbolic the whole time; numbers live in one plot-values cell and reach only the figures.
2. An "At the plot values:" cell follows a step only when a figure draws it.
3. Each check shows both sides, then their difference.
4. One displayed value per cell.
5. A live ePiX figure per step; where arrows meet tip to tip, the result first and its parts on top.
6. Rotations only through what the book taught (`Vector.rotate`, `rotation_from_to` with
   `inverse(R)`), never a local cosine/sine rotation unless the chapter builds one.
7. Every construction uses only results taught before it.

### Library additions

- `nbdisplay.at_values(value, values)`: a number or multivector with `(symbol, number)` pairs
  substituted, keeping the multivector's type. Every notebook's figures use it.
- `standardposition.in_plane(rotation, first, second, v)`: a 2D rotation applied in the plane of two
  basis vectors. It replaced two private copies inside `project_sp` and one in `proof-cross.py`.
- `_frame_scene.line(tail, head, color, width)`: a plain line for graph-paper figures (book figure
  helpers, not the library).

### The notebooks (`book/docs/notebooks/`)

- **Proof companions:** `proof-projection.py` (switched to `at_values`), `proof-rotate-from-a-to-b.py`
  (`b` symbolic, figures for the commuting turns and the three turns), `proof-cross.py` (`a`
  symbolic; the three coordinate-plane turns are `rotation_from_to` via `in_plane`),
  `proof-projection-3d.py` (the construction in cells instead of a `project_sp` call),
  `proof-reciprocal-frame.py` (both sides everywhere, three figures).
- **Part III:** all six `bootstrap-*.py` merged their worked-example and symbolic sections. Step 2's
  projection and its reuses rotate with Step 1's `Vector.rotate(-atan2(a_2, a_1))`, since Part III
  starts from scratch. Step 6 is now fully symbolic: its old note that a symbolic `R^{-1}` was slow no
  longer held (0.3 s).
- **Part I/II:**
  - `vector-addition.py` gained three figures; its lattice listing became a graph-paper figure.
  - `rotate.py` used `versor_rotation` and `plane_rotation`, which are built on the geometric product,
    a later chapter. It now uses `rotation_from_to` and `Vector.rotate`, which the chapter's own
    proofs build.
  - `geometric-product.py` compares with `Vector.rotate` instead of `plane_rotation`.
  - `product-from-projection.py` uses `rotation_from_to(b, e_1)` instead of a hand-written rotation.
  - `rotation-from-vectors.py` makes its vectors symbolic and adds `rotation_from_to` as a third
    route.
  - `levels-of-abstraction.py` shows every rung, and its sines use symbolic vectors.
  - `three-dimensions.py` gained a 3D figure.
- **Frames:**
  - `frame-qr-2d.py` made both frames and the target symbolic. Its figure labels' numbers are
    computed at the plot values instead of typed.
  - `frame-qr-3d.py` made the target symbolic, with computed labels.

### Exceptions, each with its reason in the notebook

- `proof-rotate-from-a-to-b.py` keeps `rotate_cs` (decision 2): the chapter builds
  `rotation_from_to`, so it cannot use it.
- `bootstrap-rotation-from-projection.py`'s second triangle writes the cosine/sine blend out: Step 3
  builds the rotation from the measured cosine and sine without an angle.
- The 3D frames in `proof-reciprocal-frame.py` and `frame-qr-3d.py` keep numbers: with nine symbolic
  coordinates each check takes minutes (`tasks/reference/frames-qr-and-reciprocal-frames.md`).
- `bootstrap-rotation-from-product.py` leaves out the term-by-term table of `(R * v) * R^{-1}`:
  symbolically it is about 4,400 characters of nested square roots.
- Judgment call: the bootstrap notebooks' `show_mult` tables are the symbolic ones only. The
  2026-11-16 answer put a concrete table first; the 2026-11-17 rule keeps numbers to the figures.

### The graph and the rule docs

- `book/docs/proof-dependencies.dot` is a hand-written graph with one node per named result. It is
  drawn on the first page (`book/docs/index.rst`, "How the results build on each other") with
  `sphinx.ext.graphviz`. `graphviz` was added to `entrypoint/04-install-docs.sh`.
- `tasks/reference/teaching-order-and-dependencies.md` (new) holds the rule, when each library
  rotation becomes available, the teaching order, and how to keep the graph true.
- `CLAUDE.md`, `tasks/reference/book-outline.md` and `tasks/reference/book-notebook-teaching-style.md`
  replace "values first, then symbolic" with these rules.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-17)

1. One task for all 19 notebooks, worked proof companions → Part III → Part I/II → frames, with a
   commit per notebook.
2. `proof-rotate-from-a-to-b.py` keeps `rotate_cs`, with a sentence saying why.
3. The graph is a hand-written `.dot` file.
4. One node per named result.

## Verification

- Each notebook was checked by itself:
  - ruff, ruff format and ty pass, and the annotation report shows no rows for it;
  - every cell runs with `tools/run_notebook_cells.py`, and every check's difference is 0;
  - its figures were rendered and looked at; collisions and hidden arrows found that way were fixed
    before each commit.
- The image was rebuilt with Graphviz. `make docs` (HTML and PDF) builds, every notebook executes,
  and the graph is drawn. Two problems predate this work: the `frame.py` "more than one target"
  warning and a `base.py` `MultiVectorBase.exp` "Undefined substitution |A|" docstring error.
- `make format` passes; it caught one long line in `rotate.py`, which was fixed.
- `make test`: 1367 passed. `make check-notebooks`: 0 errors.
