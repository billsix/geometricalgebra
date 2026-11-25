# Write the "Orthogonal" book page (done)

**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>), noticed while finishing `tasks/archive/2026/11/21/book-opening-vectors-supersede-geometry-types.md`. **Done:** 2026-11-25.

`book/docs/orthogonal.rst` was a one-line placeholder. Perpendicular lines and the perpendicular bisector were already taught in `book/docs/product-from-projection.rst` ("Angle, area and perpendicular").

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-25)

Keep the page, about orthogonal decomposition and frames (perpendicular lines are already covered elsewhere); do not fold it into `product-from-projection`.

## Result

- **`book/docs/orthogonal.rst`:** orthogonal defined as `u · v = 0` (`eq-orthogonal`, citing `eq-angle-measure`), with the quarter turn of `plotting-a-table` as the first example; the rejection is orthogonal to what it was rejected from (`eq-rejection-orthogonal`, Lean `reject_perp_dot` / `reject_perp`) and Pythagoras for projection plus rejection (`eq-pythagoras`); orthogonal frames, where a vector is the sum of its projections onto the frame vectors (`eq-orthogonal-coordinates`), built from any two non-parallel vectors by keeping the first and rejecting it from the second (`make_orthogonal_frame`); a forward pointer to `frames-qr` for space. It reuses the `proj2` figure of `projection`.
- **`notebooks/orthogonal.py`:** the companion, every step symbolic with `show_difference` for the checks (quarter turn, rejection ⊥, Pythagoras, frame ⊥, projections add back to `c`) and live ePiX figures for the split and the frame; in `notebooks/README.md`.
- **Teaching order:** `tasks/reference/teaching-order-and-dependencies.md` records what `orthogonal` uses (all taught before it) and that its `frames-qr` mention only points forward; `tasks/reference/book-outline.md` moves `orthogonal` from "prose only" to "prose + companion notebook".
- **Verification:** the notebook executes clean (`jupytext --execute`); `ty` and `pyright` (`make check-notebooks`) pass; `make docs` built the HTML and PDF with no undefined references for the new page and no overflow (0 equations or tables too wide); the one Sphinx warning is the ambiguous `InvertibleFunction` cross-reference in `gacalc.frame.Frame.to_invertible_function`, which predates this task.
- **Not done:** a Lean statement of Pythagoras in 𝒢₂ (the 𝒢₃ `plane_pythagorean` exists; the page cites only what exists), and the maintainer's voice pass (the page carries the standard draft note).
