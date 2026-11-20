# The PDF printed `<Figure size …>` where a notebook's matplotlib figure belonged

**Created:** 2026-11-20 (William Emerison Six <billsix@gmail.com>) · **Completed:** 2026-11-20

The maintainer reported "figure" text in the PDF that was not rendered. It was the literal
`<Figure size 800x200 with 1 Axes>`, 47 times, in the Part IV explorations that plot with
matplotlib (`displaymv`, the 𝒢₂/𝒢₃ products and transforms, graded types, the rotor exponential).
The HTML showed the figures.

## Cause and fix

`src/gacalc/nbplotutils.py` set the inline backend to `set_matplotlib_formats("svg")`, so each
`display(fig)` output carried only `image/svg+xml` and `text/plain`. myst-nb's LaTeX priority
(`base_render_priority()["latex"]`: `application/pdf`, `image/png`, `image/jpeg`, `text/latex`,
`text/markdown`, `text/plain`) has no SVG, so the PDF got the text repr. The backend now emits
`("svg", "pdf")`: HTML and Jupyter keep the SVG, and LaTeX takes matplotlib's own vector PDF.
A `conf.py` `nb_mime_priority_overrides` that let LaTeX take the SVG through
`sphinx.ext.imgconverter` was the alternative; it was not used because ImageMagick rasterizes the
SVG, while matplotlib's PDF stays vector.

## Verification

Found from `book/docs/_build/latex/geometry2.tex` (the text sat in a `cell_output` verbatim) and
the executed `.ipynb`'s MIME bundle. After the fix, the book built with `entrypoint/docs.sh` in the
image (exit 0, no new Sphinx warnings): `pdftotext geometry2.pdf - | grep -c "<Figure size"` gave
0, and page 394 (`displaymv`'s `plot_multivector` cells) shows the three number-line plots. This
build also carried `tasks/archive/2026/11/20/cancellation-underbrace-everywhere.md`'s changes.
