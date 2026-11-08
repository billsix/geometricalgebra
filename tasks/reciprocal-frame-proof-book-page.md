# Book page (prose + LaTeX) and notebook for the reciprocal-frame and frame-inverse proofs

**Status:** proposed — needs go-ahead (open questions answered)
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-11-08 (William Emerison Six <billsix@gmail.com>): "make a task for the book page"
**Depends on:** `tasks/archive/2026/11/07/lean-reciprocal-frame-and-frame-inverses.md` (done; the Lean
form of this math, scoped "Lean only", so the other two of the three forms were skipped there).

## BLUF

The reciprocal frame and the two `Frame` inverses are machine-checked in Lean for 𝒢₂ and 𝒢₃, but the
book has no page stating or deriving them, and no notebook shows a student the coordinates. Write the
prose + LaTeX proof page and its symbolic notebook so the result exists in all three forms (repo
`CLAUDE.md`, "Every piece of math comes in three forms"). Done = a proof page under `book/docs/` that
states and derives theorems 1–8 and cites each Lean theorem by name, a `book/docs/notebooks/*.py`
notebook that checks them with gacalc + sympy, both reachable from the toctree, and `make docs` plus
`make check-regions` green.

## Context

- **Model trio to copy:** `book/docs/proof-projection.rst` + `book/docs/notebooks/proof-projection.py`
  + `proofs/GacalcProofs/StandardPosition.lean`.
- **Proof-page conventions:** `tasks/reference/book-outline.md`, "Notation & prose conventions for
  proof pages" (state, prove, then verify in coordinates).
- **The Lean statements to narrate:** `proofs/GacalcProofs/ReciprocalFrame2D.lean` and
  `proofs/GacalcProofs/ReciprocalFrame3D.lean` (theorems `dot_recip_kronecker`, `reconstruct`,
  `coord*_of_perp`, `recip*_eq_normal_div`, `recip3_eq_reject_div` / `recip2_eq_reject_div`, the
  `frameMap_*` / `invPeel_*` round trips, `invReciprocal_eq_invPeel`). The task's done-record lists
  theorems 1–8 and maps each to H&S equations 3.4, 3.5, 3.7.
- **The math in prose:** `tasks/reference/frames-qr-and-reciprocal-frames.md`.
- **The existing frames page:** `book/docs/frames-qr.rst` is a stub with a maintainer-voice TODO and
  the two QR notebooks (`notebooks/frame-qr-2d`, `notebooks/frame-qr-3d`). The new proof page belongs
  next to it (or in its toctree); the narrative prose in that TODO is the maintainer's to write and is
  out of scope here.
- **The Python side already cites the theorems:** `src/gacalc/frame.py` docstrings,
  `tests/test_frame.py`, `tests/test_frame_class.py`. The notebook can reuse those checks' shape.

## Plan

1. Read the model trio and the proof-page conventions.
2. Write the notebook first (symbolic `a1, a2[, a3]`, compute the reciprocal frame, show the Kronecker
   table, reconstruction, both inverses agreeing, all simplified to equality).
3. Write the proof page: statement, derivation (the similar-triangles coordinate, last reciprocal
   vector = last rejection over its norm squared, peel vs reciprocal inverse), Lean citations, then
   pull the notebook's verification in via doc regions.
4. Add it to the toctree; run `make docs` and `make check-regions`.

## Decisions

- **Page placement (William Emerison Six <billsix@gmail.com>, 2026-11-08): a new
  `book/docs/proof-reciprocal-frame.rst`** beside the other `proof-*.rst` pages, linked from
  `book/docs/frames-qr.rst`. This matches the existing proof pages and leaves `frames-qr.rst` for the
  maintainer-voice narrative its TODO describes.
