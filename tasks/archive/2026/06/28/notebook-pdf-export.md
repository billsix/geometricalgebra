# Notebook "Export to PDF" should work in the container

**Status:** DONE (2026-06-28)
**Created:** 2026-06-28

## Goal

When running the JupyterLab notebooks in the container (`make jupyter`, or
`/usr/local/bin/jupyter.sh` from `make shell`), JupyterLab's
**File → Save and Export Notebook As → PDF** failed: the image shipped no
PDF-export toolchain. The `Dockerfile` now installs that toolchain so PDF export
works out of the box.

## What was done

Added a dedicated `dnf install` layer to the `Dockerfile` (after the main install
layer, before the project `COPY`s) with **pandoc + a XeLaTeX toolchain**:

```
pandoc
texlive-xetex
texlive-collection-fontsrecommended
texlive-collection-latexrecommended
texlive-adjustbox texlive-tcolorbox texlive-collectbox
texlive-ucs texlive-titling texlive-enumitem texlive-rsfs
texlive-jknapltx texlive-upquote texlive-ulem texlive-soul
texlive-eurosym texlive-pgf texlive-environ texlive-trimspaces texlive-parskip
```

### Decisions

- **LaTeX route (`--to pdf`), not WebPDF** — conventional, matches the family's
  TeX usage, no Chromium download.
- **Installed unconditionally** (not behind a feature flag). The jupyter stack
  itself (`.[dev,notebooks,jupyter]`) is already installed unconditionally in
  this image, so the PDF-export toolchain that completes it is too. (geo's other
  heavy features — emacs/spyder — are flag-gated and default off, but those are
  optional editors, not part of the always-present notebook workflow.) If image
  size later becomes a concern, this layer can be moved behind a
  `USE_PDF_EXPORT`-style `ARG` (default `1` in the Makefile, `0` in the
  Dockerfile, per the family convention).

### How the package set was determined

Empirically: built a throwaway `fedora:44` image with pandoc + nbconvert + a
candidate TeX set and ran `jupyter nbconvert --to pdf --execute` on a math-heavy
test notebook (sympy LaTeX output + display math). The default nbconvert LaTeX
template needed one package beyond the obvious collections — **`soul.sty`
(`texlive-soul`)** — surfaced as a missing-`.sty` error; everything else resolved
from the two recommended collections + the named helper packages.

## Verification

- **Isolated:** the package set produced a PDF (`nbconvert --to pdf --execute`) in
  a clean `fedora:44` container.
- **In-image (end to end):** rebuilt the real geo image with the new layer
  (`podman build`, exit 0); `pandoc` and `xelatex` present; ran
  `nbconvert --to pdf --execute` inside it using geo's own `/venv` →
  **20,843-byte `geotest.pdf`**, exit 0. Throwaway images cleaned up afterward.

## Follow-ups (optional, not blocking)

- If a notebook later uses a LaTeX feature outside this set, the failure names the
  exact missing `.sty` → add the matching `texlive-*` package.
- Consider the `ARG`-gating above only if image size becomes a problem.
