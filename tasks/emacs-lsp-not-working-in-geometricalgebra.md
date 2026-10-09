# Why Emacs LSP (type errors + autocomplete) works in modelviewprojection's container but not geometricalgebra's

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 4
**Difficulty:** 4
**Started:** 2026-10-09

## BLUF

**Root cause found and fixed (fix needs the maintainer's interactive confirmation).** Both containers
use the identical `lsp-mode` + `lsp-pyright` Emacs config with a hardcoded LSP workspace root. The root
must equal the in-container repo **mount path**; modelviewprojection's matches (`/mvp/`) so LSP works,
but geometricalgebra's was set to the project **name** `/geometricalgebra/` while the repo mounts at
`/gacalc` — a non-existent workspace root, so lsp-pyright produced no diagnostics and no completion.
Fixed `my-lsp-root` to `"/gacalc/"` in `entrypoint/dotfiles/.emacs.d/init.el`. Durable write-up:
`tasks/reference/emacs-lsp-setup.md`.

## The evidence

- geometricalgebra `init.el`: `lsp-mode` + `lsp-pyright`, `lsp-auto-guess-root nil`, and
  `(advice-add 'lsp--calculate-root :override #'my-lsp-root)` with `my-lsp-root` returning
  `"/geometricalgebra/"`.
- geometricalgebra `Makefile`: `FILES_TO_MOUNT = -v $(pwd):/gacalc/:Z`, and `shell.sh` does
  `cd /gacalc/`. So the repo is at **`/gacalc`**, not `/geometricalgebra` → the forced LSP root points
  at a directory that does not exist in the container → lsp-mode can't establish a workspace.
- modelviewprojection (`modelviewprojection/modelviewprojection/entrypoint/dotfiles/.emacs.d/init.el`):
  the **same** config, but `my-lsp-root` returns `"/mvp/"`, and its `Makefile` mounts `-v $(pwd):/mvp/:Z`
  — the root matches the mount, so lsp-pyright establishes the workspace and LSP works.
- Not the cause: the eglot hook in `preferences.el` is removed by `init.el`'s
  `(remove-hook 'python-mode-hook 'eglot-ensure)` (mvp does the identical thing and works); the Pyright
  server is pip-installed in `/venv` and `shell.sh` editable-installs the package + generates `g*.py`,
  so package resolution is fine once the root is correct.

So the two setups differ in exactly one literal: the hardcoded root. gacalc's was a copy-paste/rename
slip when forking mvp's template (name vs. mount path).

## Fix applied

`entrypoint/dotfiles/.emacs.d/init.el`: `my-lsp-root` `"/geometricalgebra/"` → `"/gacalc/"` (matches
`FILES_TO_MOUNT`). One line, matching mvp's proven-working form.

## Verification

Could not be verified end-to-end here: it needs an interactive GUI Emacs **inside geometricalgebra's own
container** (`make shell`), which this environment can't run. **The maintainer should confirm:** open a
`src/gacalc/*.py` in Emacs in the container and check that inline type errors and autocomplete appear.
If anything is still off, the reference doc lists the fallback (derive the root from the dominating
`pyproject.toml`, or let `lsp-auto-guess-root` do it).

## Proposals considered (per the ask)

1. **(Applied) Fix the hardcoded root to `/gacalc/`.** Smallest change, matches mvp exactly.
2. Alternative, if the literal keeps drifting on future forks: compute the root from the buffer's file
   (locate the dominating `pyproject.toml`) or re-enable `lsp-auto-guess-root`. Noted in the reference
   doc, not applied (the template's convention is the fixed literal = the mount path).

## Open questions

None. (The fix is applied; the only follow-up is the maintainer's interactive confirmation, which no
automated gate can do.)
