# Voice pass + figures for the "Proof: Projection by Rotating to Standard Position" book page

**Status:** proposed — maintainer's own voice pass (not agent-blocked)
**Priority:** 7
**Difficulty:** 3
**Created:** 2026-10-04 (William Emerison Six <billsix@gmail.com>), spun off at the archive of
`tasks/archive/2026/10/04/reduce-to-standard-position.md`

## BLUF

The `proof-projection` book page and its notebook were drafted (and the notebook runs) as part of the
reduction-to-standard-position work. The prose is a draft in the agent's voice, modelled on
`proof-rotate.rst`, with figure spots left as `.. TODO figure`; this task is the **maintainer's voice
pass** — rewrite the prose in his teaching voice, add the real figures, and build-check — before the
page is considered book-ready. "Done" = the maintainer has revised the `.rst`/notebook prose, the
figures are in, `make docs` builds the page, and the `DRAFT` comment block at the top of the `.rst` is
removed.

## What exists (drafted 2026-09-30, citations updated 2026-10-04)

- `book/docs/proof-projection.rst` — the narrative proof: rotate `b` onto the x-axis one coordinate
  plane at a time with the 2D rotation of `proof-rotate.rst`, keep the x-coordinate, rotate back; why
  that is allowed (projection commutes with rotation); the payoff (no product used, so project/reject
  can later build the product). Cites `proj_rotXY_equivariant`/`proj_rotXZ_equivariant` and the
  single theorem `projectSP_eq_proj` in `proofs/GacalcProofs/StandardPosition.lean`.
- `book/docs/notebooks/proof-projection.py` — the companion calculation notebook (jupytext percent
  format; `.ipynb` is a build artifact): `project_sp` vs `projected_onto` on a concrete pair, then
  symbolically for a general `a` against `b = 3e₁ + 4e₂ + 12e₃` (exact `k = 5`, `|b| = 13`), and
  project + reject = `a`. Verified to execute 2026-10-04 against the live source.
- Both registered in `book/docs/projection.rst`'s toctree.

## Remaining (maintainer)

- Voice pass over the `.rst` + notebook markdown (teaching voice, per `tasks/reference/book-outline.md`).
- Real figures at the two `.. TODO figure` spots (a and b with the shadow on the line through b; the
  same pair after the frame is rotated so b is on the x-axis).
- A `make docs` build check (the page has never been built), then remove the `DRAFT` comment block.

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
