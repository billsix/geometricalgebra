# Voice pass + figures for the "Proof: Projection by Rotating to Standard Position" book page

**Status:** proposed — maintainer's own voice pass (not agent-blocked)
**Priority:** 7
**Difficulty:** 3
**Created:** 2026-10-04 (William Emerison Six <billsix@gmail.com>), spun off at the archive of
`tasks/archive/2026/10/04/reduce-to-standard-position.md`

## BLUF

The `proof-projection` book page and its notebook were drafted as part of the
reduction-to-standard-position work. This task is now a **pure voice pass** — the prose is in the
agent's voice and the maintainer will rewrite it in his teaching voice. The structural work is
**done** (`tasks/archive/2026/10/08/projection-standard-position-make-2d.md`): the page was
restructured 2D-first (it had been written in 3D), the figures `sp1`–`sp5` are rendered and embedded,
the DRAFT/TODO banners are removed, and `make docs` builds the page + PDF. "Done" = the maintainer has
revised the `.rst`/notebook prose to his voice.

## What exists (drafted 2026-09-30; restructured 2D-first 2026-10-08)

- `book/docs/proof-projection.rst` — the narrative proof, now **2D-lead**: rotate `b` onto the x-axis
  with a single 2D rotation (`proof-rotate.rst`), keep the x-coordinate, rotate back; why that is
  allowed (projection commutes with rotation); a "Stepping up to three dimensions" section (the
  salvaged xy/xz two-plane material); the payoff (no product used, so project/reject can later build
  the product). Cites `proj_rotPlane_equivariant` / `projectSP_eq_proj` in
  `proofs/GacalcProofs/StandardPosition2D.lean` (2D) and `StandardPosition.lean` (3D section). The
  figures `sp1`–`sp5` are in; the DRAFT/TODO banners are gone.
- `book/docs/notebooks/proof-projection.py` — the companion notebook (jupytext percent format;
  `.ipynb` is a build artifact), now **2D-primary**: an explicit `g2` single-rotation construction vs
  `projected_onto` (concrete + symbolic, `b = 3e₁ + 4e₂`), projection + rejection rebuild `a`, then a
  3D step-up with `project_sp` (`b = 3e₁ + 4e₂ + 12e₃`). Executes clean under `make docs`.
- Both registered in `book/docs/projection.rst`'s toctree.

## Remaining (maintainer)

- Voice pass over the `.rst` + notebook markdown (teaching voice, per `tasks/reference/book-outline.md`).
  Everything else (2D-first restructure, figures, build-check, banner removal) is done.

## Follow-on ideas (from the archived task's scan; no decisions block them)

- **B2** — a 3D projection-rejection page (`projection-rejection-3d.rst` exists as a notebook page)
  showing the literal e₁-alignment chain: project onto a plane, 2D-rotate, rotate back.
- **B3** — cross-link `rotate.rst` from the proof page as the trusted 2D building block the chain
  reduces to.
- **N1** — a `notebooks/`-side demo pairing `show_mult` with the standard-position projection, so a
  student watches `a` rotate to standard position, the projection happen trivially, and rotate back;
  tied to `tasks/reference-doc-lean-workflow-and-proof-notebooks.md`.

## Context / cross-refs

- The theme and what is proven: `tasks/reference/reduction-to-standard-position.md`.
- The code the notebook runs: `src/gacalc/standardposition.py`, tests `tests/test_standardposition.py`.
- The sibling voice-pass task, same shape: `tasks/levels-of-abstraction-book-voice-pass.md`.
- The book pipeline (jupytext → myst_nb, venv kernel gotchas): `tasks/reference/book-and-docs-pipeline.md`.
