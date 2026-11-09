# Port the rotation explanation (and its SVGs) from the mvp book

**Created:** 2026-08-03 · **Completed:** 2026-08-03

Ported ch07's rotation-about-the-origin derivation from the github.com/billsix/modelviewprojection
book; HTML + PDF both built and the identity notebook proved the result live.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-03)

- **License:** match mvp, **GFDL-1.3**. The three ported pages carry the GFDL header.
- **Placement:** option (a): the high-school **coordinate derivation is foundational and early**,
  in `proof-rotate.rst` (a visible child of `rotate.rst`); `geometric-product.rst` then defines the
  geometric product in G2 and **re-derives rotate coordinate-free**, using the `12·6⁻¹·5`
  keep-it-exact discipline.

## What was done

- **`book/docs/proof-rotate.rst`:** ported the ch07 derivation (the goal, the change-of-frame
  trick with the `rotate1–8.svg` walkthrough, and the algebra collapsing to
  `r(a;θ) = cos θ·a + sin θ·(−a_y, a_x)`). All 37 mvp `inlinetex` uses were converted to
  `.. math::` / `:math:` (gacalc has no inlinetex). GFDL header.
- **`book/docs/rotate.rst`:** the from→to framing (rotate vec 1 → vec 2, magnitudes don't matter),
  linking to `proof-rotate` (foundation) and the notebook. GFDL header.
- **`book/docs/geometric-product.rst`:** the bridge: `(−a_y, a_x)` **is** `a·e₁₂`, so
  `R = cos θ + sin θ·e₁₂` is the rotor and rotating is `a·R`; plus the keep-it-exact (`12·6⁻¹·5`,
  cross-linked to `canonical-form`) framing. GFDL header.
- **`book/docs/notebooks/rotate.py`:** rotates `e₁` by 90° → `e₂` (a first from→to example).
- **`book/docs/notebooks/geometric-product.py`:** symbolically verifies `a·(cos θ + sin θ·e₁₂)`
  equals the coordinate formula **and** gacalc's `plane_rotation`; the difference renders as `0`.
- **SVGs** copied into `book/docs/_static/cc0/` (the maintainer's own `williamesix/rotate*.svg`,
  and the CC0 `Stephan_Kulla` unit circle, attribution preserved via the `cc0/<author>/` path).
- `index.rst`: `proof-rotate` moved out of the hidden toctree to a visible child of `rotate`.

## Verification (real `make docs`, in the container)

- HTML + PDF both built (PDF 73 pages). SVGs rendered in both (ImageMagick's `convert` for the
  PDF); the `aligned` derivation rendered (mathjax HTML / lualatex PDF).
- All notebooks executed against the venv-installed gacalc; the rotor formula minus gacalc's
  rotation rendered as `0`.
- Getting the notebooks to execute in `make docs` was a sub-investigation (Sphinx moved into the
  venv, ImageMagick was added, the notebook sources gained jupytext kernelspec headers). Those
  pipeline fixes were committed; the write-up is in `tasks/reference/book-and-docs-pipeline.md`
  › "Executable notebooks" and "SVG figures in the PDF".

## Deferred

- ch07's "Why it is Wrong" tail and all of ch08/09 (rotating around a paddle's center) need
  translate, which the book did not cover yet; they were not ported.
- A book-wide license pass (only the three ported pages carried the GFDL header) and the
  maintainer's voice pass on the ported prose were left as follow-ups.
