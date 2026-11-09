# Harvest build & dev-workflow gotchas into CLAUDE.md / book pipeline

**Created:** 2026-08-13 · **Completed:** 2026-08-13

Group C of the 2026-08-13 archive gap-analysis sweep: low-risk operational facts that lived only
in archived docs. Siblings: the other `harvest-*` tasks in this folder and
`tasks/archive/2026/08/13/blade-dict-interchange-reference.md`.

## What was harvested, and where

Five items were applied, each verified against source first. (Source docs are under
`tasks/archive/`.)

- **Book prose is licensed GFDL-1.3**, distinct from the LGPL-2.1-only code →
  `tasks/reference/book-and-docs-pipeline.md`. From
  `2026/08/03/port-rotation-explanation-from-mvp.md`.
- **Notebook PDF export:** XeLaTeX chosen over WebPDF (no Chromium), installed unconditionally;
  nbconvert's default template needs `soul.sty` (`texlive-soul`) beyond the recommended
  collections → `book-and-docs-pipeline.md`. From `2026/06/28/notebook-pdf-export.md`.
- **`ruff format` does not accept `--extend-exclude` on the CLI** (only `ruff check` does), so
  the vendored-Emacs `entrypoint/` exclusion must live in `pyproject.toml`
  `[tool.ruff] extend-exclude`; "fixing" `format.sh` to pass the flag would silently reformat the
  27-file vendored tree → CLAUDE.md dev-workflow. From `2026/06/05/cleanups-and-hygiene.md`.
- **Baked JupyterLab settings:** `jupytext-config set-default-viewer python` (single-click opens
  py:percent files as notebooks; accepted trade-off: `.py` no longer opens as plain text by
  default) and the announcements/"news" labextension disabled (locked at sys-prefix) → CLAUDE.md
  dev-workflow (Containerized dev bullet). From `2026/07/29/jupytext-default-viewer.md` and
  `2026/07/29/suppress-jupyter-news-prompt.md`.
- **Pixel-verification footgun:** `savefig` must be *inside* the `with create_graphs() as ax:`
  block, because it calls `plt.close()` on exit; saving afterward captures a blank canvas, and
  blank == blank compares equal (a vacuous "pixel-identical"). Sanity-check that the baseline is
  non-blank, and reconstruct the "before" via `git stash`/`git show` → CLAUDE.md dev-workflow. From
  `2026/07/19/dedup-draw-ndc-plot-helper.md`.

## Skipped

The optional numpy freshness nit was skipped: `g2.py` indeed had no numpy import (ruff strips the
header's now-unused one), but numpy was still a genuine runtime dependency via
`base.py`/`transforms.py`, so CLAUDE.md's framing of numpy as a runtime dep was not behind.
