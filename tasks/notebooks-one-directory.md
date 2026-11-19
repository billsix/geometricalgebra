# One notebook directory that students open, and the book draws from

**Status:** proposed — questions answered; implementation waits for the maintainer's go-ahead
**Priority:** 4
**Difficulty:** 5
**Created:** 2026-11-19 (William Emerison Six <billsix@gmail.com>), the implementation plan from
`tasks/unify-demo-and-book-notebooks.md`.

## BLUF

Put every notebook, demo and book companion alike, in the top-level `notebooks/`. That directory is
the one a student opens with `make jupyter` and runs like a graphing calculator, and the book renders
whichever of its notebooks the toctrees name. The ePiX scene helpers move into an installed package,
so no notebook edits `sys.path`. Done means:
- one directory, documented in the README and the book;
- no `sys.path` lines;
- `make format`, `make check-notebooks`, `make test` and `make docs` pass;
- the prebuilt ePiX figures are byte-identical to before.

## Context (read first)

- `tasks/reference/demo-and-book-notebooks.md`: the measured differences, why each exists, and the
  import-path finding. Its table is the checklist for this task.
- `tasks/reference/book-and-docs-pipeline.md`: myst-nb, `entrypoint/docs.sh`, and the ePiX figures.
- `tasks/reference/book-notebook-teaching-style.md`: the teaching rules, including rule 6 (numbers
  first for explorations, symbolic for companions).
- `CLAUDE.md` › "Dev workflow" and the module layout: the text to update once the directories merge.

## Plan

1. **Helpers into a package.** Move the seven generic ePiX helpers (`_scene2d`, `_scene3d`,
   `_frame_scene`, `_bootstrap_live`, `_line_scene`, `_paper_scene`, `_venn_scene`) from
   `book/figures/epix/` into `src/gacalc/epixscene/`, dropping the leading underscore, and keep them
   out of `import gacalc`. Add a boundary test like `tests/test_gl_import_boundary.py`.
   - Every importer then uses `from gacalc.epixscene.scene2d import …`: the notebooks, the six
     figure-specific modules and the prebuilt figure scripts.
   - Remove the 31 `sys.path` cells, the E402 exemption, and `book/figures/epix` from ty's
     `extra-paths`.
   - Point `tools/check_epix_keywords.py` at the new paths.
   - Before the move, render the figures with `tools/render_epix_figures.py`; render again after it
     and `cmp` every `.png`/`.pdf`. The two renders must be identical.
2. **One directory.** `git mv notebooks/*.py notebooks/` (the names do not collide). Then:
   - `entrypoint/docs.sh` converts `notebooks/*.py` into `book/docs/notebooks/*.ipynb` (still
     gitignored build output), so the toctree entries `notebooks/<page>` stay as they are.
   - Notebooks the book leaves out go in `conf.py`'s `exclude_patterns`.
   - Every header asks for the `python3` kernel.
   - The paths move in `entrypoint/format.sh` (ty), `pyrightconfig.json`, `pyproject.toml`'s
     per-file ignores, `.gitignore`, `tools/check_notebook_prose_width.py`,
     `tools/check_annotations.py`, `tools/check_epix_keywords.py` and `entrypoint/percentToIpynb.sh`.
   - pyright has never checked the book notebooks, so expect it to report errors there to fix.
3. **The book shows every notebook** (decision 1): add all 11 demo notebooks to the book as a new
   part called "Explorations".
4. **License headers** (decision 2): give the 32 companions the LGPL-2.1-only header cell, tagged
   `remove-cell` so myst-nb does not print it, and tag the demos' existing header cells the same way.
5. **Make it findable.**
   - `make jupyter` opens at `notebooks/` (decision 3), and its help line says so.
   - A `notebooks/README.md`, which JupyterLab renders, lists every notebook with its book page, or
     marks it as an exploration.
   - The README gains a short "Notebooks" section (`[HOST] make jupyter`, then open `notebooks/`).
   - The book tells students the same, on the `interactive-calculator.rst` placeholder or a short
     front-matter section.
6. **One style guide.** In `tasks/reference/book-notebook-teaching-style.md`, state the two kinds by
   role (a page's companion, an exploration) instead of by directory. Update `CLAUDE.md`: the module
   layout, the full-`G` alias carve-out list and `make check-notebooks`.
7. **Gates.** `make format`, `make check-notebooks`, `make test`, `make docs` (every notebook the book
   includes executes there), `tools/check_annotations.py`, and the figure comparison from step 1.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-19)

1. **All 11 demo notebooks go in the book**, as a new part called "Explorations". A notebook can be
   dropped later by adding it to `conf.py`'s `exclude_patterns`.
2. **The 32 companion notebooks get the LGPL-2.1-only header cell**, tagged `remove-cell` so myst-nb
   does not print it. The `.rst` pages stay GFDL; the notebooks are code.
3. **`make jupyter` lands in `notebooks/`** (`--ServerApp.default_url=/lab/tree/notebooks`) with the
   rest of the repository still browsable, so a student can follow a notebook into the source it
   calls.
4. **The ePiX helpers become the `gacalc.epixscene` subpackage**, shipped in the wheel. It imports
   only where ePiX is installed, because ePiX is not on PyPI. It follows the
   `gacalc.nbplotutils`/`gacalc.gl` precedent, and it is kept out of `import gacalc` by a boundary
   test.

## Open questions

None. Implementation waits for the maintainer's go-ahead.
