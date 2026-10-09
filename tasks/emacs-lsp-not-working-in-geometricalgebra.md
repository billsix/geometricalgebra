# Why Emacs LSP (type errors + autocomplete) works in modelviewprojection's container but not geometricalgebra's

**Status:** in-progress
**Priority:** 4
**Difficulty:** 4
**Started:** 2026-10-09

## BLUF

In modelviewprojection's container, Emacs gives the maintainer working LSP (inline type errors,
autocomplete); in geometricalgebra's container it does not. Study both setups, determine **if and why**
the difference exists, and make one or more concrete proposals to fix geometricalgebra's. Deliverable:
a findings write-up (root cause, with evidence) plus proposal(s); the actual config fix is a follow-on
(`proposed — needs go-ahead`) unless a proposal is a clearly-safe one-liner the maintainer wants applied.

## Context (read first)

Both repos are mounted: `/foo/opt/geometricalgebra` and `/foo/opt/modelviewprojection`.

- **geometricalgebra's Emacs config:** `entrypoint/dotfiles/.emacs.d/` — `init.el`, `preferences.el`,
  `helm.el`, `install-melpa-packages.el`. Early leads (verify, do not assume):
  - `init.el` disables the eglot python hook and configures **`lsp-mode` + `lsp-pyright`**
    (`lsp-pyright-typechecking-mode "basic"`), sets `lsp-auto-guess-root nil`, and **overrides
    `lsp--calculate-root` with a fixed `my-lsp-root`** (advice) — a wrong root would break workspace
    resolution and hence errors/completion.
  - `preferences.el` ALSO configures **`eglot`** with `(python-mode . eglot-ensure)` — a direct
    conflict with `init.el`'s lsp-mode-for-python; which one wins depends on load order. This dual
    config is the prime suspect.
  - The Pyright **server binary**: `CLAUDE.md` says the Dockerfile pip-installs `pyright` into the
    venv (libatomic is its runtime dep). Confirm the `pyright-langserver` the `lsp-pyright` Emacs
    package shells out to is actually found on PATH in the container, and that it sees the project.
  - **Package resolution for the server:** geometricalgebra is `src/`-layout with `pythonpath = src`,
    and `g1/g2/g3.py` are **gitignored + generated**. If the server's env has no editable install and
    `src` is not on its path, `import gacalc` (and the generated modules) won't resolve → spurious
    "unresolved import" errors and no completion. Check whether anything editable-installs the package
    or sets the server's extra paths (compare to how `docs.sh` editable-installs for autodoc).
- **modelviewprojection's Emacs config:** NOT under `modelviewprojection/entrypoint/dotfiles/` (empty).
  Find where mvp's container gets its Emacs config — likely a mounted host config
  (`/foo/opt/billsEmacsConfigs` or `/foo/opt/dotfiles`) or a different entrypoint layout. Determine
  which lsp client mvp uses (eglot vs lsp-mode), which server, and how mvp makes its package importable
  to the server. The DIFFERENCE between the two setups is the answer.
- Both projects share the container-per-project template; the Emacs tree is vendored under
  `entrypoint/dotfiles/.emacs.d/elpa/` in geometricalgebra (off-limits to reformat, but readable).

## Goal

Write up the root cause (why LSP is dead in geometricalgebra but live in mvp), backed by evidence from
both configs, in a reference doc (`tasks/reference/emacs-lsp-setup.md`) or inline in this task, and give
one or more concrete fix proposals (e.g. resolve the lsp-mode/eglot conflict, fix the lsp root, ensure
the server resolves `gacalc`/the generated modules). Scaffold the chosen fix as a follow-on task.

## Plan

- [ ] Read geometricalgebra's `init.el`/`preferences.el`/`install-melpa-packages.el` in full; pin down
      the lsp-mode vs eglot load order and the `my-lsp-root` value.
- [ ] Locate and read mvp's Emacs/LSP config (find the mount); identify its client/server and how its
      package is importable to the server.
- [ ] Confirm the Pyright server binary presence/PATH and the package-resolution story in
      geometricalgebra's container (does the server see `src/` and the generated `g*.py`?).
- [ ] State the root cause with evidence; write proposal(s); scaffold the fix task.

## Open questions

None — both repos are mounted and the investigation is self-contained; the fix itself is go-ahead-gated.
