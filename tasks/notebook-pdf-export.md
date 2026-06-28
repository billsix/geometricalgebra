# Notebook "Export to PDF" should work in the container

**Status:** proposed — needs go-ahead
**Created:** 2026-06-28

## Goal

When running the JupyterLab notebooks in the container (`make jupyter`, or
`/usr/local/bin/jupyter.sh` from `make shell`), JupyterLab's
**File → Save and Export Notebook As → PDF** currently fails: the image ships no
PDF-export toolchain. Update the `Dockerfile` so PDF export works out of the box.

## Background

- The `jupyter` extra (`pyproject.toml`, installed via
  `".[dev,notebooks,jupyter]"`) pulls in JupyterLab + **nbconvert**, but nbconvert's
  default PDF path (`--to pdf`) shells out to external tools that are **not** in
  the image.
- The current `Dockerfile` `dnf install` list (lines ~15–31) has **no `pandoc`,
  no TeX Live, no `nbconvert` system deps**. So the LaTeX-based PDF export has
  nothing to run.

## What "export to PDF" needs

nbconvert's classic PDF route is: notebook → (pandoc) → LaTeX → PDF via a LaTeX
engine. Concretely the image needs:

1. **`pandoc`** — the markdown/notebook → LaTeX converter.
2. **A LaTeX engine + packages** — `xelatex` (nbconvert's default template uses
   it) plus the support packages nbconvert's `article`/`base` templates pull in.
   On Fedora that's roughly:
   - `texlive-xetex` (the engine),
   - `texlive-collection-fontsrecommended`,
   - `texlive-collection-latexrecommended`,
   - `texlive-adjustbox`, `texlive-tcolorbox`, `texlive-collectbox`,
     `texlive-ucs`, `texlive-titling`, `texlive-enumitem`,
     `texlive-rsfs`, `texlive-jknapltx` (the packages nbconvert's default
     template historically requires — confirm against the actual error output).
3. Possibly **`texlive-collection-mathscience`** since these notebooks render a
   lot of math (sympy/LaTeX output).

(An alternative is nbconvert's **WebPDF** exporter, which uses headless Chromium
via Playwright instead of LaTeX — lighter on TeX packages but adds a browser
download. Decide which route; LaTeX/`--to pdf` is the conventional one and keeps
parity with the rest of Bill's TeX-based projects.)

## Plan

1. Add `pandoc` + the TeX Live package set above to the `Dockerfile`'s `dnf
   install` list (the first/unconditional one around line 15, so it's always
   present — PDF export isn't gated behind a feature flag).
2. Rebuild: `make image`.
3. Verify end-to-end inside the container: open a notebook (e.g.
   `notebooks/displaymv.py` materialized to `.ipynb`) and run
   `jupyter nbconvert --to pdf <notebook>.ipynb`, then the GUI
   **Save and Export As → PDF**. Iterate on the TeX package list until a math-heavy
   notebook exports cleanly (missing-`.sty` errors name the exact package to add).
4. Note the size cost: TeX Live collections are heavy. If that's a concern, gate
   them behind a `BUILD_DOCS`-style `ARG` (default on) rather than always
   installing — open question below.

## Open questions

- **LaTeX route vs WebPDF?** LaTeX/`--to pdf` is conventional and matches the
  family's TeX usage; WebPDF avoids the TeX Live bulk but adds Chromium.
- **Always install, or gate behind an `ARG`?** TeX Live is large; if image size
  matters, a `USE_PDF_EXPORT`/`BUILD_DOCS` arg (default `1` in the Makefile, `0`
  in the Dockerfile, per the family convention) would keep a bare `podman build`
  lean.
