# Stand up a Sphinx book pipeline for gacalc (HTML + PDF)

**Created:** 2026-08-02 · **Completed:** 2026-08-02

Stood up gacalc's Sphinx book ("Plotting On Crappy Graph Paper", William Emerison Six, 0.0.1) as
an **empty-but-building skeleton**: HTML + PDF, no EPUB, with an autodoc `api.rst` for context.
**The durable design (how it builds, the decisions, the gotchas) lives in
`tasks/reference/book-and-docs-pipeline.md`.**

## What was built

- `book/docs/`: `conf.py` (furo; lualatex; autodoc/napoleon/viewcode/mathjax/imgconverter/
  nbsphinx/myst_nb), `index.rst`, `api.rst`, `_static/custom.css`, stock quickstart `Makefile`.
- `Dockerfile`: `ARG BUILD_DOCS=0` + a gated book-toolchain block.
- `Makefile`: `BUILD_DOCS ?= 1`, `--build-arg BUILD_DOCS`, `docs` + `clean` targets.
- `entrypoint/docs.sh`: in-container build (generate + editable-install → html → latexpdf → copy
  to `output/gacalc/`).
- `.gitignore`: `book/docs/_build/`, `output/*` (keeping `.gitkeep`); `output/.gitkeep`.
- Cross-repo: the book toolchain packages were added to the sandbox repo's Dockerfile and to
  github.com/billsix/runClaudeInContainer `tasks/reference/sandbox-capability-map.md`.

## Verification

- HTML build passed (sandbox `sphinx-build -b html`, exit 0).
- PDF build passed (sandbox `sphinx-build -M latexpdf`, ~205 KB via lualatex, confirming the
  lualatex-for-Unicode-docstrings decision).
- The full end-to-end container gate (`make image BUILD_DOCS=1 && make docs`) was left for the
  maintainer / a nested run; it was not run in this task.

## Method

The generative setup (`sphinx-quickstart` + the `conf.py`/index/api/css/output edits) was captured
as heavily commented shell scripts (removed at archive; in git history). Permanent build-file
edits were made directly (scripting them would only duplicate committed content); sandbox
`dnf install`s were not logged (environment setup outside the project).

## Follow-ups found

Two autodoc-surfaced docstring issues (not pipeline bugs): `|A|` read as an RST substitution (12
warnings), and `ₙ` U+2099 was absent from FreeSerif (dropped from the PDF). Details and fixes were
recorded in `tasks/reference/book-and-docs-pipeline.md`.
