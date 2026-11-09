# Why Emacs LSP (type errors + autocomplete) works in modelviewprojection's container but not geometricalgebra's

**Created:** 2026-10-09 · **Completed:** 2026-10-09

**Root cause found and fixed.** Both containers use the identical `lsp-mode` + `lsp-pyright` Emacs
config with a hardcoded LSP workspace root. The root must equal the in-container repo **mount path**;
modelviewprojection's literal matches mvp's repo mount path, so LSP works there, but geometricalgebra's
was set to the project **name** `/geometricalgebra/` while the repo mounts at `/gacalc` — a
non-existent workspace root, so lsp-pyright produced no diagnostics and no completion. Fixed
`my-lsp-root` to `"/gacalc/"` in `entrypoint/dotfiles/.emacs.d/init.el`. Durable write-up:
`tasks/reference/emacs-lsp-setup.md`.

## The evidence

- geometricalgebra `init.el`: `lsp-mode` + `lsp-pyright`, `lsp-auto-guess-root nil`, and
  `(advice-add 'lsp--calculate-root :override #'my-lsp-root)` with `my-lsp-root` returning
  `"/geometricalgebra/"`.
- geometricalgebra `Makefile`: `FILES_TO_MOUNT = -v $(pwd):/gacalc/:Z`, and `shell.sh` does
  `cd /gacalc/`. So the repo is at **`/gacalc`**, not `/geometricalgebra` → the forced LSP root pointed
  at a directory that does not exist in the container → lsp-mode couldn't establish a workspace.
- modelviewprojection (github.com/billsix/modelviewprojection `entrypoint/dotfiles/.emacs.d/init.el`):
  the **same** config, but its
  `my-lsp-root` returns the same path its `Makefile` mounts the repo at — the root matches the mount,
  so lsp-pyright establishes the workspace and LSP works.
- Not the cause: the eglot hook in `preferences.el` is removed by `init.el`'s
  `(remove-hook 'python-mode-hook 'eglot-ensure)` (mvp does the identical thing and works); the Pyright
  server is pip-installed in `/venv` and `shell.sh` editable-installs the package + generates `g*.py`,
  so package resolution is fine once the root is correct.

So the two setups differed in exactly one literal: the hardcoded root. gacalc's was a copy-paste/rename
slip when forking mvp's template (name vs. mount path).

## Fix applied

`entrypoint/dotfiles/.emacs.d/init.el`: `my-lsp-root` `"/geometricalgebra/"` → `"/gacalc/"` (matches
`FILES_TO_MOUNT`). One line, matching mvp's proven-working form.

## Decisions

1. **Applied:** fix the hardcoded root to `/gacalc/` — the smallest change, matching mvp exactly.
2. **Not applied:** computing the root from the buffer's file (locate the dominating `pyproject.toml`)
   or re-enabling `lsp-auto-guess-root`, in case the literal keeps drifting on future forks. Recorded in
   the reference doc as the fallback; the template's convention is the fixed literal = the mount path.

## Verification

Not verified end-to-end in this session: it needs an interactive GUI Emacs **inside geometricalgebra's
own container** (`make shell`), which the agent's environment couldn't run. The check left for the
maintainer was to open a `src/gacalc/*.py` in Emacs in the container and confirm that inline type
errors and autocomplete appear; no automated gate covers it.
