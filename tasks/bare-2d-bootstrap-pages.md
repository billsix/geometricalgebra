# Bare-bones 2D book pages: rotation → projection → rotation → product → projection → rotation

**Status:** approved — questions answered 2026-11-15 (Decisions below); implementation starts on the maintainer's go-ahead
**Priority:** 5
**Difficulty:** 6
**Created:** 2026-11-14 (William Emerison Six <billsix@gmail.com>)

## BLUF

A run of short reStructuredText pages that does the 2D bootstrap end to end, with minimal prose and
all of the proofs, code and graphs: the precalculus rotation, then projection defined from it, then
rotation defined from projection, then the geometric product, then projection and rotation
redefined through the product. Duplicating material from the rest of the book is fine. Done means
the pages build in `make docs`, every code cell runs, and each step's proof is shown.

## Context

- The book: `book/docs/*.rst` with notebooks in `book/docs/notebooks/*.py` (jupytext percent
  format, executed at build) and ePiX figures in `book/figures/epix/*.py`
  (`tasks/reference/book-and-docs-pipeline.md`, `tasks/reference/book-outline.md`).
- Existing pages that cover pieces of the arc: `proof-rotate.rst` (`eq-rotate-formula`),
  `proof-projection.rst` (2D projection by standard position), `proof-rotate-from-a-to-b.rst`,
  `product-from-projection` (notebook), `geometric-product` (notebook).
- The arc and why it is not circular: `tasks/reference/reduction-to-standard-position.md` ("The full
  bootstrap arc"). Lean has each step in 2D: `StandardPosition2D.lean`, `RotateFromTo2D.lean`.
- `CLAUDE.md` rules that apply: the three forms (Lean, symbolic Python, prose + LaTeX) for each piece
  of math; the notation rules (parentheses apply, `*` multiplies, every angle named); a symbolic
  coefficient written `Scalar(s) * e_1`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-15)

1. **Placement:** a new top-level section at the **end** of the book: its own captioned, numbered
   toctree in `book/docs/index.rst`, after Part II and before the unnumbered Reference toctree.
   The other placement considered was a separate short document built alongside the book.
2. **Projection through the product:** `(a · b) * b⁻¹`, where `a · b` is the scalar part of
   `a * b`.
3. **Rotation through the product:** both forms, **one-sided first**. First the 2D-only one-sided
   form `v * (â * b̂)` (Lean `projRotation_eq_vec_mul`), then the half-angle sandwich `R * v * R⁻¹`
   (Lean `projRotation_eq_sandwich`), with a short proof that the two agree.
4. **Graphs:** ePiX figures in `book/figures/epix/*.py`, as elsewhere in the book, not matplotlib.
5. **Lean:** cite the existing 2D theorems, at least in comments if nowhere else. Add a theorem
   only where a step has none. The likely gap is projection stated through the product
   (`(a · b) * b⁻¹`); check for an existing one first.
6. **Granularity:** one short `.rst` page plus one jupytext notebook per step, six in all:
   1. the precalculus rotation;
   2. projection defined from rotation;
   3. rotation defined from projection;
   4. the geometric product;
   5. projection through the product;
   6. rotation through the product.

## Lean theorems already covering the arc (checked 2026-11-15)

- The precalculus rotation: `Rotation2D.lean` (`rot_vec`, `rot_add`, `rot_normSq`);
  `StandardPosition2D.lean` (`rotPlane_*`).
- Projection by standard position: `StandardPosition2D.lean` (`projectSP_eq_proj`,
  `rejectSP_eq_reject`, `proj_onto_x_axis`).
- Rotation from projection: `RotateFromTo2D.lean` (`rotateFromTo_carries`);
  `ProjectionRotation2D.lean` (`projRotation_carries_from_to`, `projRotation_isometry`).
- The product: `StandardPosition2D.lean` (`mul_eq_magnitude_smul_alignSP`).
- Rotation through the product: `ProjectionRotation2D.lean` (`projRotation_eq_vec_mul`,
  `projRotation_eq_sandwich`); `Versor2D.lean`.
