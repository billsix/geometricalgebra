# Umbrella: ePiX figures for the book's vector-addition, projection and 3D-projection sections

**Status:** DONE 2026-10-07 (overnight autonomous run) — all three steps built, gate green, full html+PDF clean. Archived with its steps.
**Priority:** 4
**Difficulty:** 5 (the 3D step carries most of it)
**Created:** 2026-10-07 (William Emerison Six <billsix@gmail.com>: "make a umbrella task for the following …")

## BLUF

Extend what the rotation sequence established — book figures authored in **Python with the `epix`
package** (`book/figures/epix/*.py`, a shared scene helper, rendered by `make docs` to PDF for LaTeX and a
dark-mode-safe PNG for HTML) — to three more sections of "Geometry 2": **vector addition and
subtraction**, **projection and rejection in 2D** (the result we want *and* the precalculus derivation),
and **projection and rejection in 3D** onto the three coordinate planes. Done = each step's figures render
in the book build, the section pages reference them, and this umbrella's checklist is complete.

## Context

- **The pattern to copy:** `book/figures/epix/rotate_goal.py` and `rotate1.py`–`rotate8.py` with
  `_rotation_scene.py` (constants + `unit_circle_scene`/`vector`/`wedge`/`right_angle_marker`/`leg`),
  `tools/render_epix_figures.py`, and the "ePiX figures" section of
  `tasks/reference/book-and-docs-pipeline.md` (how rendering, referencing, `BACKGROUND` flattening and
  the radians gotcha work). Record: `tasks/archive/2026/10/07/epix-plot-integration.md` (the image integration + the
  rotation port).
- **The three sections today:** `book/docs/vector-addition.rst`, `projection.rst`,
  `projection-rejection-3d.rst` are placeholders ("content to come") with placeholder notebooks
  (`1 + 1`); `proof-projection.rst` is an agent-drafted derivation page with two `.. TODO figure`
  markers (lines 37 and 57) — the pre-calc derivation this umbrella's step 2 illustrates. Outline and
  spine: `tasks/reference/book-outline.md` (rotate → geometric product → projection → reflection; 2D
  first, 3D second).
- **The math behind the derivations:** `src/gacalc/standardposition.py` (`project_sp`/`reject_sp`:
  rotate `b` onto the x-axis with `rotate_in_xy_plane`/`rotate_in_xz_plane`, project there, rotate back),
  machine-checked in `proofs/GacalcProofs/StandardPosition.lean`, `Projection2D.lean`,
  `Projection3D.lean`. Reference: `tasks/reference/reduction-to-standard-position.md`.
- **ePiX in 3D:** the Python package exposes `Point(x=, y=, z=)`, `epix.camera.at(Point)`,
  `epix.viewpoint(...)`, `epix.Plane`, `epix.E_1/E_2/E_3`, `clip_box`; epix-mirror's `notebooks/planes.py`,
  `cube.py`, `sphere.py`, `polyhedra.py` show the camera + plane idioms.

## Steps (the index; each is its own task doc)

1. [x] `tasks/archive/2026/10/07/book-epix-figures-step-1-vector-addition.md` — addition + subtraction figures (2D); also
   promotes the generic 2D helpers out of `_rotation_scene.py` into a shared `_scene2d.py`.
   **DONE 2026-10-07** (archived → `tasks/archive/2026/10/07/`).
2. [x] `tasks/archive/2026/10/07/book-epix-figures-step-2-projection-2d.md` — projection + rejection: the result, then the
   rotate-to-standard-position derivation (fills `proof-projection.rst`'s TODO figures).
   **DONE 2026-10-07** (archived → `tasks/archive/2026/10/07/`).
3. [x] `tasks/archive/2026/10/07/book-epix-figures-step-3-projection-3d.md` — projection + rejection in 3D onto the
   `e_12`, `e_23`, `e_31` planes; first 3D figures, new `_scene3d.py`.
   **DONE 2026-10-07** (archived → `tasks/archive/2026/10/07/`).

Ordering is expressed by Priority + `Depends on` in the step docs (steps 2 and 3 reuse step 1's shared
helper); none is `blocked` — all within our control.

## Cross-step decisions

- Same conventions as the rotation sequence: one `.py` per figure, percent-format, module-level `fig`,
  `BACKGROUND = "#f2f2f2"` for the HTML PNG, LaTeX labels matching the prose (`\vec{a}`, `\vec{b}`),
  colours: black vectors, purple angles, blue/green for the two legs/components.
- **Every argument by keyword** (maintainer, 2026-10-07) — `tools/check_epix_keywords.py` is the check;
  add any new helper or epix call to its table.
- Figures illustrate; the prose on each page is the maintainer's to write (the steps add the figures
  and minimal captions/alt text, and may leave `.. TODO prose` markers).
- The 3D plane names in figure labels follow the book's wording (`e_12`, `e_23`, `e_31`); gacalc's
  blade constant for the third is `Bivector.e_13` (= −`e_31`) — see step 3's open question 1.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-07)

- Projection figures reuse the rotation sequence's `a` (length 1.25 at 66°), `b` at 20°, length 1.
- The third plane is labelled `e_31` (cyclic) in the figures, with a one-line page note that gacalc
  spells the blade `e_13 = -e_31`.
- 3D: one figure per plane showing projection *and* rejection, plus an overview with all three planes.
- `proof-projection.rst` gets the **2D** derivation figures in step 2; the 3D "one plane at a time"
  pictures wait for step 3 and the maintainer's 2D-then-3D restructuring of that page.
- Every argument by keyword, every binding typed; `tools/check_epix_keywords.py` is a `make format`
  gate step.

## Open questions

None.
