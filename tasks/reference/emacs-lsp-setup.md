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
- The Pyright **server** is npm-installed at image build (`npm install -g pyright` in
  `entrypoint/01-install-base.sh`, into `/usr/local/bin`), so it runs offline. Don't use the pip
  `pyright` package: it is only a launcher that downloads Node and the server the first time it runs in
  each fresh container, and without network it exits (`nodeenv failed`), leaving Emacs with no Python
  completion at all (`tasks/archive/2026/11/04/emacs-python-lsp-investigation.md`). The same pyright
  serves `make check-notebooks`. `shell.sh` activates the venv, generates the gitignored `g*.py`, and
  `uv pip install -e .`, so the server resolves `import gacalc` and the generated modules.
- lsp-mode also starts the **ruff** add-on beside pyright. The vendored lsp-mode ships a `ty-ls` client
  too, but at priority -1 it loses to lsp-pyright's 2 whenever `pyright-langserver` is on `PATH`; if
  pyright is missing, lsp-mode silently runs ty instead (github.com/billsix/multivariate-math's image
  did that as of 2026-11-04).
- **Parameter hints** come from pyright's signature help. lsp-mode shows them when you type `(` or `,`
  (`lsp-signature-auto-activate` is `(:on-trigger-char :on-server-request)`); `M-x
  lsp-signature-activate` shows them on demand. eglot instead shows them continuously through eldoc
  while the cursor is inside a call.
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

Verified 2026-11-04 with a headless Emacs that loads the real `init.el` in the gacalc image, with the
network cut (`--network=none`): pyright and ruff attached, completion after `g3.e_1.` returned the full
member list, and signature help inside `g3.e_1.project(` returned all four overloads. The probe was a
one-shot pair of scripts (`probe.el` + `run_probe.sh`), kept in git history under
`tasks/adhoc/emacs-python-lsp-investigation/`.
