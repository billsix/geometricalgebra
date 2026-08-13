# Harvest build & dev-workflow gotchas into CLAUDE.md / book pipeline

**Status:** COMPLETED 2026-08-13 — five items applied (each verified against source first):
book GFDL-1.3 license + notebook-PDF (XeLaTeX / `texlive-soul`) → `book-and-docs-pipeline.md`;
the `ruff format --extend-exclude` CLI gotcha, the baked Jupyter settings, and the
`savefig`-inside-`create_graphs()` pixel-verification footgun → CLAUDE.md dev-workflow. The
optional numpy freshness nit was **skipped**: `g2.py` indeed has no numpy import (ruff strips
the header's now-unused one), but numpy is still a genuine runtime dep via
`base.py`/`transforms.py`, so CLAUDE.md's framing isn't actually behind. Ready to commit,
then archive.
**Priority:** 5
**Difficulty:** 2
**Created:** 2026-08-13
**Origin:** the 2026-08-13 archive gap-analysis sweep (Group C — build/pipeline &
dev-workflow gotchas). Siblings: the other `harvest-*` tasks + `blade-dict-interchange-reference.md`.

Low-risk, re-litigable operational facts currently only in archived docs. A single small
batch of edits to CLAUDE.md + `tasks/reference/book-and-docs-pipeline.md`.

## Items

- [ ] **Book prose is licensed GFDL-1.3**, distinct from the LGPL-2.1-only code.
      *Source:* `2026/08/03/port-rotation-explanation-from-mvp.md`. *Home:*
      book-and-docs-pipeline.md.
- [ ] **Notebook PDF export**: XeLaTeX chosen over WebPDF (no Chromium), installed
      unconditionally; nbconvert's default template needs `soul.sty` (`texlive-soul`)
      beyond the recommended collections. *Source:* `2026/06/28/notebook-pdf-export.md`.
      *Home:* book-and-docs-pipeline.md.
- [ ] **`ruff format` does not accept `--extend-exclude` on the CLI** (only `ruff check`
      does) — the vendored-Emacs `entrypoint/` exclusion must live in `pyproject.toml`
      `[tool.ruff] extend-exclude`; "fixing" `format.sh` to pass the flag would silently
      reformat the 27-file vendored tree. *Source:* `2026/06/05/cleanups-and-hygiene.md`.
      *Home:* CLAUDE.md dev-workflow.
- [ ] **Baked JupyterLab settings**: `jupytext-config set-default-viewer python`
      (single-click opens py:percent files as notebooks; accepted trade-off — `.py` no
      longer opens as plain text by default) and the announcements/"news" labextension
      disabled (locked at sys-prefix so users can't re-enable). *Source:*
      `2026/07/29/jupytext-default-viewer.md`, `2026/07/29/suppress-jupyter-news-prompt.md`.
      *Home:* CLAUDE.md dev-workflow (Containerized dev bullet).
- [ ] **Pixel-verification footgun**: when confirming a notebook/plot change is
      behaviour-preserving, `savefig` must be *inside* the `with create_graphs() as ax:`
      block — it calls `plt.close()` on exit, so saving afterward captures a **blank**
      canvas, and blank==blank compares equal (a vacuous "pixel-identical"). Sanity-check
      the baseline is non-blank; reconstruct the "before" via `git stash`/`git show`.
      *Source:* `2026/07/19/dedup-draw-ndc-plot-helper.md`. *Home:* CLAUDE.md dev-workflow
      (a gacalc instance of the cross-project "derive the before mechanically" rule).
- [ ] *(freshness nit, optional)* CLAUDE.md frames numpy purely as a runtime dep; note
      that the `isclose` rework dropped numpy from the *generated* modules' imports.
      *Home:* CLAUDE.md.
