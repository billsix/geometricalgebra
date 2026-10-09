# Emacs LSP in the container (lsp-mode + lsp-pyright), and the hardcoded-root trap

**Reference document** — how the in-container Emacs gives Python LSP (inline type errors +
autocomplete), why it was dead in geometricalgebra while live in modelviewprojection, and the one
convention that must hold. Durable; update in place. Written 2026-10-09 (William Emerison Six
<billsix@gmail.com>) from `tasks/archive/2026/10/09/emacs-lsp-not-working-in-geometricalgebra.md`.

## The setup (shared across the container-per-project template)

`entrypoint/dotfiles/.emacs.d/` (`init.el`, `preferences.el`, `helm.el`, vendored `elpa/`):

- Python LSP is **`lsp-mode` + `lsp-pyright`** (NOT eglot). `preferences.el` registers an
  `eglot-ensure` python hook, but `init.el` then `(remove-hook 'python-mode-hook 'eglot-ensure)` and
  wires `lsp-deferred`, so lsp-mode is the active client for Python. (The two clients coexisting in the
  config is intentional and harmless given the remove-hook; it is not the bug below.)
- The Pyright **server** is pip-installed into `/venv` (its runtime dep `libatomic` is installed by the
  Dockerfile); `shell.sh` activates the venv, generates the gitignored `g*.py`, and `uv pip install -e .`
  so the server resolves `import gacalc` and the generated modules. So package resolution is fine.
- The workspace **root** is pinned, not guessed: `init.el` sets `lsp-auto-guess-root nil` and overrides
  `lsp--calculate-root` with `my-lsp-root`, a function returning a **fixed absolute path**.

## The convention that must hold — and the trap

**`my-lsp-root` MUST equal the in-container repo mount path**, i.e. the `-v $(pwd):/<here>/:Z` target in
the Makefile's `FILES_TO_MOUNT`. If it names a directory that does not exist in the container, lsp-mode
cannot establish a workspace, so lsp-pyright produces **no diagnostics and no completion** — LSP looks
simply dead, with no obvious error.

The trap is a copy-paste/rename slip when forking the template: the root tends to get set to the
**project's name** rather than its **mount path**, and the two differ.

| project | Makefile mount (`FILES_TO_MOUNT`) | `my-lsp-root` | result |
|---|---|---|---|
| modelviewprojection | `-v $(pwd):/mvp/:Z` | `"/mvp/"` | match → LSP works |
| geometricalgebra (before 2026-10-09) | `-v $(pwd):/gacalc/:Z` | `"/geometricalgebra/"` | **mismatch → LSP dead** |
| geometricalgebra (fixed) | `-v $(pwd):/gacalc/:Z` | `"/gacalc/"` | match → LSP should work |

That mismatch was the entire cause of "Emacs LSP works in mvp's container but not geometricalgebra's":
the configs are otherwise identical. Fixed by setting `my-lsp-root` to `"/gacalc/"` in
`entrypoint/dotfiles/.emacs.d/init.el`.

**When forking the template to a new project, change `my-lsp-root` to the new mount path** (and keep it
in sync if the mount path ever changes). A more robust alternative, if the hardcoded override keeps
drifting: derive the root from the buffer's file (e.g. locate the dominating `pyproject.toml`) instead
of a literal, or just let `lsp-auto-guess-root` do it — but the fixed-path form is what the template
uses, so the rule is "keep the literal equal to the mount."

## Verification status

The fix is a one-line literal change matching mvp's proven-working config. It could not be verified
end-to-end in the authoring session (that needs an interactive GUI Emacs inside geometricalgebra's own
container, `make shell`, which this environment can't run). **The maintainer should confirm** by opening
a `src/gacalc/*.py` in Emacs in the container and checking that type errors and completion appear.
