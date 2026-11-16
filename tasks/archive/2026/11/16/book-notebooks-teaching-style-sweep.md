# Bring every book notebook up to the teaching-style standard

**Completed:** 2026-11-16 (William Emerison Six <billsix@gmail.com>; done by Claude on the
`book-notebooks-teaching-style` branch)

## What was done

Every book notebook with content (20 of `book/docs/notebooks/*.py`; the task first said 22, a
miscount) was revised to the standard in `tasks/reference/book-notebook-teaching-style.md`. The ten
16-line placeholders were left alone; they get the standard when written. The `show_mult` tables
went in first, in `tasks/archive/2026/11/16/book-notebooks-show-mult-tables.md`; the style of the
proof companions moved here from `tasks/proof-notebooks-student-math-notation-style.md`, which keeps
only the backfill of a notebook for every proof (decided by the maintainer 2026-11-16).

Gap survey before the revision, and what each notebook got. Codes: **L** prose math in backticks,
not `$…$` LaTeX; **A** checks that showed nothing or gave the answer first (`assert`,
`== … # -> True`); **D** a list of coordinate differences instead of one subtraction cell;
**C** teaching prose in code comments; **M** several ideas in one cell; **O** an opening that did not
start from what the reader knows.

| Notebook | Gaps fixed |
|---|---|
| `bootstrap-rotation.py`, `bootstrap-projection.py`, `bootstrap-rotation-from-projection.py`, `bootstrap-product.py`, `bootstrap-projection-from-product.py`, `bootstrap-rotation-from-product.py` | L (they already followed `book-outline.md`'s structure) |
| `proof-projection.py` | L, A, D, C, M; the worked example now shows where $a$ lands in standard position |
| `proof-projection-3d.py` | O, L, D, A, M; cites `projectSP_eq_proj` / `rejectSP_eq_reject` |
| `proof-rotate-from-a-to-b.py` | L, A, C, M; `symbolically_equal(...) # -> True` became subtraction cells |
| `proof-cross.py` | L, D |
| `proof-reciprocal-frame.py` | A (12 sites); the Kronecker-delta tables show as `sympy.Matrix` |
| `frame-qr-2d.py` | O (a graph-paper opening) |
| `frame-qr-3d.py` | one formula split across two lines |
| `geometric-product.py` | O, L, A, C (opens from multiplying by $i$) |
| `rotation-from-vectors.py` | O, L, C (opens from the angle-difference identity) |
| `product-from-projection.py` | L, A, M |
| `levels-of-abstraction.py` | L, A, C |
| `vector-addition.py` | L, A, C |
| `rotate.py` | L, A |
| `three-dimensions.py` | L, A |

## Judgment calls

- **Checks are subtraction cells showing $0$**, per `book-outline.md`, including where a notebook had
  `symbolically_equal` or `==` returning `True`: `.simplified()` on the difference reduced every
  one to $0$, trigonometric ones included.
- **`vector-addition.py`'s lattice check was dropped, not kept as a list of nine zeros.** The
  symbolic $t(a) = a + b$ check already covers every point, and the cell now shows the slid lattice;
  the notebook says so.
- **Backticked code names stayed code** (`Vector.rotate(θ)`, `versor_rotation`, Lean theorem names,
  file paths); only math became LaTeX. In the six Part III notebooks this was done by an allowlisted
  symbol table (`tasks/adhoc/book-notebooks-teaching-style-sweep/backticks_to_latex.py`, idempotent),
  and the paragraphs that grew past 88 columns were reflowed without splitting a formula
  (`reflow_long_markdown.py`).
- **Not done, as out of scope:** adding live ePiX figures or a values cell to the Part I and proof
  notebooks. `book-outline.md`'s companion structure was written for Part III; extending it is a
  separate decision.

## Verification

- Each revised notebook ran cell by cell with the sweep's cell runner, promoted at the end to
  `tools/run_notebook_cells.py` (doctested), which prints every code cell's
  last value: in the rewritten notebooks every check cell printed a zero value. The six Part III
  notebooks, whose code did not change, ran without error inside the `gacalc` image (they need
  ePiX).
- `ruff check`, `ruff format`, `ty check book/docs/notebooks` and `tools/check_annotations.py` clean;
  a scan found no inline `$…$` split across lines.
- In the image: the book built (HTML and PDF), `entrypoint/format.sh` passed, and
  `pytest -m "not slow"` passed.
