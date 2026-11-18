# Why the demo and book notebooks differ, and a plan to unify them (both able to sit in the book)

**Status:** parked — do NOT start until the maintainer explicitly says to start this task. Filed
2026-11-18 by William Emerison Six <billsix@gmail.com>: "That task is not to be started on your
own, until I tell you explicitly." A batch go-ahead for other tasks does not cover it.
**Priority:** 8 (parked)
**Difficulty:** 6
**Created:** 2026-11-18
**Related:** `tasks/archive/2026/11/18/notebooks-like-displaymv.md` (brought both sets up to `notebooks/displaymv.py`'s
style; its decision 1 spun this task off)

## BLUF

gacalc has two sets of jupytext notebooks:
- **demo notebooks** under `notebooks/` (`displaymv.py`, `displayg2.py`, …);
- **book notebooks** under `book/docs/notebooks/` (the companions of the book's pages).

They differ in conventions, tooling and figure library. The maintainer wants to know why, and wants
a plan that unifies them while letting a demo notebook appear in the book too. Done means a written
finding (a reference doc, or a section of `tasks/reference/book-notebook-teaching-style.md`) and a
scaffolded implementation plan, both reviewed by the maintainer, with no notebooks moved yet.

## Context (read first)

- `tasks/reference/book-notebook-teaching-style.md`: the guidance both sets now follow (rule 6 already
  splits them: "numbers before symbols" for demo notebooks, symbolic throughout for book notebooks).
- `tasks/reference/book-outline.md` ("Structural conventions"): the book notebooks' structure (one
  plot-values cell, live ePiX figures, one check per cell).
- `tasks/reference/book-and-docs-pipeline.md`: how myst-nb executes the book notebooks
  (`nb_execution_raise_on_error`, `nb_render_markdown_format = "myst"`, the kernel in the venv).
- `CLAUDE.md` › "Dev workflow": `make check-notebooks` (pyright over `notebooks/`), and
  `entrypoint/format.sh` (`ty` over `book/docs/notebooks`).

## Differences found so far (2026-11-18, to verify and complete)

| | Demo `notebooks/` | Book `book/docs/notebooks/` |
| --- | --- | --- |
| Purpose | standalone explorations of the library | each the companion of one `.rst` page |
| Figures | matplotlib via `gacalc.nbplotutils` (all but `displayproofs`, `displayvectorcalc`) | live ePiX via `book/figures/epix/` helpers (20 notebooks), added to `sys.path` |
| Values | numbers before symbols | symbolic throughout; numbers only in one plot-values cell and the figures |
| Type gate | pyright (`make check-notebooks`, `pyrightconfig.json` includes `notebooks`) | `ty check book/docs/notebooks` in `format.sh` |
| Lint | E501 applies | E501 exempt (`pyproject.toml`); prose width checked by `tools/check_notebook_prose_width.py` |
| Executed by | nobody automatically (run by hand in JupyterLab) | myst-nb at `make docs`, failing the build on an error |
| Representation | mostly `Gn`, `g2`/`g3` full classes with aliases (`CLAUDE.md` carve-out) | graded `g2`/`g3` types |
| Annotation audit | `tools/check_annotations.py` covers both | same |

## Plan (when started)

1. Verify and complete the table: the import patterns, the helper modules each set uses,
   `.ipynb` generation (`make notebooks-ipynb` vs myst-nb), and the CI coverage of each.
2. For each difference, record why it exists (git history, the task archive), and whether it is
   essential (it follows from book versus exploration) or incidental (history).
3. Propose the unification:
   - one style guide with any book-only rules marked;
   - one type gate and one lint config;
   - a figure-library decision (ePiX everywhere, matplotlib for demos, or either with a reason);
   - how a demo notebook can be included in the book, for example a toctree "Explorations" part that
     myst-nb executes, and what that requires of the notebook (its execution time, no GUI backend,
     deterministic output).
4. Write the finding and the proposed steps; scaffold the implementation as its own task, proposed
   and needing go-ahead.

## Open questions

None yet. Raise them when the task is started.
