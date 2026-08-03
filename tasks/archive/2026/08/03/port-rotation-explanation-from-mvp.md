# Port the rotation explanation (and its SVGs) from the mvp book

**Status:** complete — ported and verified (HTML + PDF both build; the identity notebook
proves out live). A book-wide license pass and Bill's voice pass remain (see Follow-ups).
**Completed:** 2026-08-03
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-08-03 (Bill)

## Resolved (Bill, 2026-08-03)

- **License:** match mvp → **GFDL-1.3**. The three ported pages carry the GFDL header.
- **Placement:** option (a) — the high-school **coordinate derivation is foundational and
  early**, in `proof-rotate.rst` (a visible child of `rotate.rst`); then
  `geometric-product.rst` defines the geometric product in G2 and **re-derives rotate
  coordinate-free**, using the `12·6⁻¹·5` keep-it-exact discipline.

## What was done (scope: ch07's rotation-about-the-origin derivation only)

- **`book/docs/proof-rotate.rst`** — ported the ch07 derivation: the goal, the
  change-of-frame trick (`rotate1–8.svg` walkthrough), and the algebra collapsing to
  `r(a;θ) = cos θ·a + sin θ·(−a_y, a_x)`. All 37 mvp `inlinetex` uses converted to
  `.. math::` / `:math:` (gacalc has no inlinetex). GFDL header.
- **`book/docs/rotate.rst`** — the from→to framing (rotate vec 1 → vec 2, magnitudes
  don't matter), links to `proof-rotate` (foundation) and the notebook. GFDL header.
- **`book/docs/geometric-product.rst`** — the bridge: `(−a_y, a_x)` **is** `a·e₁₂`, so
  `R = cos θ + sin θ·e₁₂` is the rotor and rotating is `a·R`; plus the keep-it-exact
  (`12·6⁻¹·5`, cross-linked to `canonical-form`) framing. GFDL header.
- **`book/docs/notebooks/rotate.py`** — rotates `e₁` by 90° → `e₂` (a first from→to
  example).
- **`book/docs/notebooks/geometric-product.py`** — symbolically verifies
  `a·(cos θ + sin θ·e₁₂)` equals the coordinate formula **and** gacalc's
  `plane_rotation`; the difference renders as `0`.
- **SVGs** copied into `book/docs/_static/cc0/` (Bill's own `williamesix/rotate*.svg`,
  and the CC0 `Stephan_Kulla` unit circle — attribution preserved via the `cc0/<author>/`
  path).
- `index.rst`: `proof-rotate` moved out of the hidden toctree to a visible child of
  `rotate`.

## Verified (real `make docs`, in the container)

- HTML + PDF both build (PDF 73 pages). SVGs render in both (ImageMagick's `convert` for
  the PDF); the `aligned` derivation renders (mathjax HTML / lualatex PDF).
- All notebooks **execute** against the venv-installed gacalc: the rotor formula,
  gacalc's rotation, and **their difference renders as `0`** — the identity proven on
  the page.
- **Getting the notebooks to execute in `make docs` was a whole sub-investigation**
  (Sphinx had to move into the venv, ImageMagick had to be added, the notebook sources
  needed jupytext kernelspec headers). The durable write-up is in
  `tasks/reference/book-and-docs-pipeline.md` › "Executable notebooks" and "SVG figures
  in the PDF". Those pipeline fixes are committed.

## Out of scope (deferred — involves translate)

ch07's "Why it is Wrong" tail and all of ch08/09 (rotating around a paddle's center)
require translate, which the book isn't dealing with yet. Not ported. See the original
task history; revisit once translate lands.

## Follow-ups

- **Book-wide license:** only the three ported pages carry the GFDL header so far; apply
  it to the rest of the book pages (or declare it once in front matter) — a small pass.
- **Bill's voice pass** on the ported prose (it's adapted from his mvp text, but he'll
  want to refine).
