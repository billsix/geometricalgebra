# Turn pyright's unused-expression rule off for the notebooks only, never per line

**Completed:** 2026-11-18
**Priority:** 6
**Difficulty:** 1
**Created:** 2026-11-18 (William Emerison Six <billsix@gmail.com>: "do type suppression for the
unused expression … at the top of the file, instead of per line … I don't want that exception on
every line, it clutters up the view of the notebooks")

## Outcome

`pyrightconfig.json` turns `reportUnusedExpression` off with one `executionEnvironments` entry each
for `notebooks/` and `book/docs/notebooks/`. The project-wide setting is gone, so `src/`, `tests/`,
`tools/` and `examples/` files keep pyright's default warning in an editor. No notebook carries a
suppression comment.

A notebook cell ends in a bare expression because that expression is the cell's output, which is why
the rule is off there. The per-line `# pyright: ignore[reportUnusedExpression]` trailers had already
been removed (all 60) by `tasks/archive/2026/11/18/notebooks-like-displaymv.md`, which relied on a
project-wide setting. This task narrowed that setting to the notebook directories.

Docs: `CLAUDE.md` › "Dev workflow" (the `make check-notebooks` bullet) and
`tasks/reference/book-notebook-teaching-style.md` (quality 15). The cross-project guidance is the
"Notebook cells: turn the unused-expression rule off once, never per line" section of the shared
`python-coding-standard.md` in github.com/billsix/runClaudeInContainer, mirrored in
github.com/billsix/runCrushInContainer.

## Decision (William Emerison Six <billsix@gmail.com>, 2026-11-18)

Option (a), a scoped `executionEnvironments` entry per notebook directory, over (b), a
`# pyright: reportUnusedExpression=false` header in each of the 41 notebooks. With (a) the notebooks
show nothing at all, and both editors already read the repo's config: Emacs pins the LSP root to
`/gacalc` (`entrypoint/dotfiles/.emacs.d/init.el`), and JupyterLab starts there
(`entrypoint/jupyter.sh`).

## Alternatives tested (pyright 1.1.414 in the gacalc image)

On a two-cell jupytext file ending in `x + 1`:
- the old top-level setting silences every file;
- an `executionEnvironments` entry silences only its root;
- the header comment silences only its file.

ruff needed nothing, because its equivalent rule, B018, is not selected in `pyproject.toml`.

## Verification

In the container:
- `pyright notebooks/` gave 0 errors and 0 warnings;
- `pyright book/docs/notebooks/rotate.py` reported no unused expression;
- a scratch `src/gacalc/` file ending in `x + 1` still warned `reportUnusedExpression`, and was
  deleted afterwards.
