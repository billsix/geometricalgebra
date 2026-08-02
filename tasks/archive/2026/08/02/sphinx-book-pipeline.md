# Stand up a Sphinx book pipeline for gacalc (HTML + PDF)

**Status:** complete
**Completed:** 2026-08-02
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-08-02 (Bill)

Stood up gacalc's Sphinx book ("Plotting On Crappy Graph Paper", William Emerison Six,
0.0.1) as an **empty-but-building skeleton** — HTML + PDF, no EPUB, with an autodoc
`api.rst` for context. **The durable design (how it builds, the decisions, the
gotchas) lives in `tasks/reference/book-and-docs-pipeline.md`** — read that, not this.

## What was built (permanent)

- `book/docs/` — `conf.py` (furo; lualatex; autodoc/napoleon/viewcode/mathjax/
  imgconverter/nbsphinx/myst_nb), `index.rst`, `api.rst`, `_static/custom.css`, stock
  quickstart `Makefile`.
- `Dockerfile` — `ARG BUILD_DOCS=0` + gated book-toolchain block.
- `Makefile` — `BUILD_DOCS ?= 1`, `--build-arg BUILD_DOCS`, `docs` + `clean` targets.
- `entrypoint/docs.sh` — in-container build (generate + editable-install → html →
  latexpdf → copy to `output/gacalc/`).
- `.gitignore` — `book/docs/_build/`, `output/*` (keep `.gitkeep`); `output/.gitkeep`.
- Cross-repo: the book toolchain packages added to `runClaudeInContainer`'s Dockerfile
  and its `sandbox-capability-map.md`.

## Verified

- HTML build: ✓ (sandbox `sphinx-build -b html`, exit 0).
- PDF build: ✓ (sandbox `sphinx-build -M latexpdf`, ~205 KB via lualatex — confirming
  the lualatex-for-Unicode-docstrings decision).
- Remaining gate (for Bill / nested): `make image BUILD_DOCS=1 && make docs` — the full
  end-to-end container build.

## Method (Bill's temp-scaffold convention, applied)

The generative setup (`sphinx-quickstart` + the `conf.py`/index/api/css/output edits)
was captured as heavily-commented shell scripts under `tasks/adhoc/sphinx-book-pipeline/`
(the standard `tasks/adhoc/<slug>/` convention), then removed at archive. Permanent
build-file edits were made directly (scripting them would only duplicate committed
content); sandbox `dnf install`s were not logged (environment setup outside the project).

## Follow-ups (gacalc docstring polish — see the reference doc)

Two autodoc-surfaced content issues, not pipeline bugs: `|A|` reads as an RST
substitution (12 warnings); `ₙ` U+2099 is absent from FreeSerif (drops from the PDF).
Details + fixes in `tasks/reference/book-and-docs-pipeline.md`.
