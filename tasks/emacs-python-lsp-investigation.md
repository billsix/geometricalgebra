# Which Python LSP does gacalc's Emacs use — did it change from pyright to ty?

**Status:** in progress
**Priority:** 3
**Difficulty:** 2
**Created:** 2026-11-04 (William Emerison Six <billsix@gmail.com>): "investigate what we use for emacs
lsp - did we change from pyright to ty? As I've been using the lsp, it doesn't seem to autocomplete as
well as I had remembered. So I want you to tell me if we changed what we had used for python lsp, and
once we talk, switch back to what we had been using before."

## BLUF

Find out which language server the in-container Emacs actually starts for Python, whether that changed
(pyright → ty), and why completion feels weaker. Done = the answer, with evidence, recorded here; any
switch back waits on a conversation with the maintainer.

## Context

- Emacs config: `entrypoint/dotfiles/.emacs.d/init.el` (lsp-mode + lsp-pyright), packages vendored in
  `entrypoint/dotfiles/.emacs.d/elpa/`.
- pyright is pip-installed into `/venv` by the `Dockerfile`; `ty` comes from dnf
  (`entrypoint/01-install-base.sh`) and is the `make format` type gate.

## Plan

1. Read the config and its git history for a server change.
2. Start the real config in a headless Emacs in the gacalc image and ask it which servers attached and
   what it completes (`tasks/adhoc/emacs-python-lsp-investigation/`), with and without network.
3. Report; switch nothing until the maintainer decides.
