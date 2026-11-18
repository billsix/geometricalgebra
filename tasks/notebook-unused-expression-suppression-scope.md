# Turn pyright's unused-expression rule off for the notebooks only, never per line

**Status:** proposed — needs go-ahead (one open question)
**Priority:** 6
**Difficulty:** 1
**Created:** 2026-11-18 (William Emerison Six <billsix@gmail.com>: "do type suppression for the
unused expression … at the top of the file, instead of per line … I don't want that exception on
every line, it clutters up the view of the notebooks")

## BLUF

A notebook cell ends in a bare expression because that expression is the cell's output, and pyright
reports each one as `reportUnusedExpression`. The per-line `# pyright: ignore[reportUnusedExpression]`
trailers are already gone: the 2026-11-18 sweep removed all 60, and no notebook has a per-line
suppression of any kind now. What is left is the scope. `pyrightconfig.json` turns the rule off
project-wide, so `src/` and `tests/` files opened in Emacs lose the warning too. Done means the rule
is off for `notebooks/` and `book/docs/notebooks/` only, still with no per-line comment, and
`make check-notebooks` stays at 0 errors.

## Context (read first)

- `pyrightconfig.json` today: `{"include": ["notebooks"], "reportUnusedExpression": "none"}`. The
  `include` scopes the CLI gate (`make check-notebooks`, `CLAUDE.md` › "Dev workflow"). The
  top-level rule applies to every file pyright analyses, including any file an editor opens.
- Both editors root pyright at `/gacalc`, so they read this file:
  - Emacs pins the LSP root (`entrypoint/dotfiles/.emacs.d/init.el`, `my-lsp-root`);
  - JupyterLab starts in `/gacalc` (`entrypoint/jupyter.sh`).
- The book notebooks are type-checked by `ty` in `entrypoint/format.sh`, which has no such rule.
  They are covered by pyright only when an editor opens them.
- ruff's equivalent rule, B018, is not selected (`pyproject.toml` `[tool.ruff.lint] select`), so
  ruff needs nothing.
- `tasks/reference/type-annotation-exemptions.md` and
  `tasks/archive/2026/11/18/notebooks-like-displaymv.md` record the trailer removal.

## The three spellings (tested 2026-11-18, pyright 1.1.414 in the gacalc image)

Each was tried on a two-cell jupytext file ending in `x + 1`:

1. **Project-wide** (today): `"reportUnusedExpression": "none"` at the top of `pyrightconfig.json`.
   This silences every file.
2. **Scoped by directory:** an `executionEnvironments` entry per notebook root,
   `{"root": "notebooks", "reportUnusedExpression": "none"}`. This silenced the notebook directory,
   while a library file in a sibling root still warned. The notebooks carry no comment at all.
3. **One header line per file:** `# pyright: reportUnusedExpression=false` as the file's first
   comment. This silenced that file only. It travels with a notebook copied out of the repo, but it
   is one extra line in each of 41 notebooks (11 demo, 30 book). In the converted `.ipynb` it sits
   in the first cell.

## Plan (when started)

1. Apply the chosen spelling (open question 1). For option 2:
   - keep `include` as it is;
   - add `executionEnvironments` for `notebooks` and `book/docs/notebooks`, plus a root for the
     rest of the repo (`src`, `tests`, `tools`, `examples`), so those keep pyright's defaults;
   - remove the top-level rule.
2. Verify:
   - `pyright notebooks/` reports 0 errors;
   - a scratch `src/` file ending in a bare expression still warns under `pyright` run on that file;
   - opening a notebook in Emacs shows no unused-expression diagnostic.
3. Record the setting in `CLAUDE.md` › "Dev workflow" (the `make check-notebooks` bullet) and in
   `tasks/reference/book-notebook-teaching-style.md` (quality 15, zero developer noise).

## Open questions

1. Which spelling: **(a) scoped `executionEnvironments` in `pyrightconfig.json`** (no line in any
   notebook), or **(b) a one-line `# pyright: reportUnusedExpression=false` header** in each of the
   41 notebooks (travels with a copied file)? Recommendation: (a). The notebooks show nothing at
   all, and both editors already read the repo's config.
