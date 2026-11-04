# Which Python LSP gacalc's Emacs uses — done-record

**Completed:** 2026-11-04. Requested by William Emerison Six <billsix@gmail.com>: "investigate what we
use for emacs lsp - did we change from pyright to ty? As I've been using the lsp, it doesn't seem to
autocomplete as well as I had remembered. So I want you to tell me if we changed what we had used for
python lsp, and once we talk, switch back to what we had been using before." Investigated by the agent;
nothing was switched, since gacalc never left pyright (below).

## Findings

1. **gacalc never changed servers.** `entrypoint/dotfiles/.emacs.d/init.el` has configured lsp-mode +
   `lsp-pyright` (`typechecking-mode "basic"`, auto-import completions on) since the initial commit
   (2025-10-24), and `git log -S` finds no edit that swapped it. `ty` is only the `make format` gate.
   The vendored lsp-mode (20261009) ships a built-in `ty-ls` client, but at priority -1 it loses to
   pyright's priority 2 whenever `pyright-langserver` is on `PATH`, which it is (`/venv/bin`).
2. **With network, the real config starts pyright and completes well.** A headless Emacs loading the
   real `init.el` in the gacalc image attached `pyright` plus lsp-mode's `ruff` add-on, and after
   `g3.e_1.` pyright returned the full member list (`dot`, `wedge`, `project`, `reject`, `is_vector`, …).
3. **Without network, there is no Python completion at all.** The pip `pyright` package is a wrapper:
   on first run it downloads Node and the npm pyright into `~/.cache/pyright-python`. Nothing is cached
   in the image, so every fresh `make shell` container downloads it (about 6 s), and under
   `--network=none` pyright exits with `nodeenv failed`. Emacs then has only `ruff` attached, no
   completion from the server, and company falls back to `python-completion-at-point` and dabbrev. This
   breaks the "self-contained image" convention, and is one way completion can silently degrade.
4. **The ty switch the maintainer may be remembering happened in other repos.**
   - github.com/billsix/modelviewprojection switched its Emacs LSP from pyright to `ty server` on
     2026-08-23, deliberately (its `tasks/archive/2026/08/23/switch-typechecker-pyright-to-ty.md`), and
     removed pyright from its image.
   - github.com/billsix/multivariate-math still configures `lsp-pyright`, but its image stopped
     installing pyright on 2025-12-06 (its commit `e9b088a`, "try debian again"). The same probe in its
     image attached `ruff` + **`ty-ls`**: lsp-mode quietly fell back to ty, and after `math.sq` it
     offered only `sqrt` and `isqrt`.
   - Still on pyright, installed with `npm install -g pyright` at image build so it works offline:
     github.com/billsix/towersofhanoi `python/`, and the local `lldbassemblyhelper` and
     `billsEmacsConfigs/python` checkouts (neither has a `github` remote, so their URLs are
     unconfirmed). github.com/billsix/runClaudeInContainer's `init.el` names lsp-pyright too; its image
     was not probed.

## Verification

- The probe (`probe.el` + `run_probe.sh`, a one-shot pair removed at archive) mounted the repo
  read-only and the vendored elpa as an overlay, so the host tree was not written. Runs: gacalc with
  network (pyright + ruff, full completion), gacalc `--network=none` (ruff only, completion `nil`),
  multivariate-math with network (ruff + ty-ls).
- `pyright --version` in the gacalc image: `1.1.414` with network; `RuntimeError: nodeenv failed`
  without.

## Follow-ups (each waits on the maintainer)

- **Recommended:** make gacalc's pyright work offline by baking it into the image, e.g.
  `uv pip install 'pyright[nodejs]'` and a build-time `pyright --version` so the download lands in a
  committed layer. This changes what the image ships, so it needs a yes.
- **Recommended:** decide per repo whether modelviewprojection should go back to pyright, and make
  multivariate-math's config match its image (install pyright, or name ty explicitly).
