# The PDF prints `<Figure size …>` where a notebook's matplotlib figure should be

**Status:** proposed — needs go-ahead
**Priority:** 2
**Difficulty:** 3
**Created:** 2026-11-20 (William Emerison Six <billsix@gmail.com>)

## BLUF

The book's PDF shows the literal text `<Figure size 800x200 with 1 Axes>` in 47 places, all in
notebook cells that draw with matplotlib (`gacalc.nbplotutils`). The HTML build does not show it.
Find why the LaTeX build gets the text fallback, fix it so each place shows the figure (or nothing
extra), and confirm with a fresh `make docs`. Done means `pdftotext` of the new PDF has 0
`<Figure size` matches and the figures appear.

## Context

- The maintainer's report (2026-11-20, verbatim): *"take a look at the pdf output, there are
  "figure" text that is not rendered, I think it's from the notebooks."*
- **Measured 2026-11-20** on `output/gacalc/geometry2.pdf` (built 2026-11-19 11:44) with
  `pdftotext -layout`: 47 `<Figure size WxH with 1 Axes>` lines. All are in Part IV explorations,
  by PDF section: 2.33 *How multiplication works in G_n* (`notebooks/displaymv.py`), 2.36 *G2:
  moving the plane* (17), 2.37 *Transforms in G_n* (10), 2.40 *A rotor is the exponential of a
  bivector* (2), 2.41 *Graded types* (5), 2.42 *G3: multiplying in space* (8). The ePiX live
  figures (`PendingFigure`) do not show this problem.
- `output/gacalc/html/notebooks/displaymv.html` has no `Figure size` text, so the problem is
  specific to the LaTeX output.
- The matplotlib helpers in `src/gacalc/nbplotutils.py` (e.g. `plot_multivector`) call
  `display(fig)`, then `plt.close(fig)`, then `return fig`. A cell like `figure =
  plot_multivector(p)` therefore emits one `display_data` output, which has both `image/png` and
  `text/plain`.
- Book config: `book/docs/conf.py` (myst_nb, `latex_engine = "lualatex"`, no `nb_mime_priority_overrides`
  set). Pipeline: `tasks/reference/book-and-docs-pipeline.md`; `entrypoint/docs.sh` converts
  `notebooks/*.py` to `book/docs/notebooks/*.ipynb` and runs `make html` + `make latexpdf`.

## Plan

1. Reproduce: `make docs`, keep `_build/latex/` and the executed `.ipynb`, and look at one
   affected output's MIME bundle and the `.tex` myst_nb wrote for it.
2. Find the cause. Leading hypotheses, to be checked, not assumed: myst_nb's LaTeX mime priority
   picks `text/plain` over `image/png` for these outputs; or a second, text-only output comes from
   the returned closed `Figure` or the inline backend's flush. Fix at the cause, either in
   `conf.py` (`nb_mime_priority_overrides` for `latex`) or in `nbplotutils` (do not emit the
   extra output).
3. `make docs`; `pdftotext geometry2.pdf - | grep -c "<Figure size"` reports 0; look at the six
   sections listed above in the PDF; check the HTML did not change.

## Open questions

None.
