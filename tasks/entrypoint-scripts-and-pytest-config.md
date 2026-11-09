# Remove the dead `[tool.pytest]` block; add `make spyder`, a Spyder preflight, and an all-notebooks `percentToIpynb.sh`

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §8.1

## BLUF

`pyproject.toml` has a `[tool.pytest]` block that contradicts `pytest.ini`; delete it. Then make the
two kept scripts usable: a `make spyder` target, a preflight in `spyder.sh`, and a
`percentToIpynb.sh` that converts every notebook. Done means all four are in, `make test` collects the
same number of tests, and `make help` lists the new targets.

## Context

Re-checked 2026-11-09. Most of the record's §8.1 low items are already fixed, by
`tasks/archive/2026/11/09/dockerfile-masked-install-and-entrypoint.md` (commit `f410608`):

- every `entrypoint/*.sh` is `100755` with `#!/usr/bin/env bash`;
- the Makefile `check-format` comment no longer suggests `BUILD_DOCS=0 USE_EMACS=0 USE_SPYDER=0`;
- the `pyproject.toml` comment names `gacalc.g2.Vector`.

The record was also wrong about `entrypoint/spyder.sh`: it does start Spyder (`exec spyder -p
/gacalc/`).

**Still open:** `pyproject.toml:40` `[tool.pytest] testpaths = ["tests"]`, while `pytest.ini`
(`testpaths = src tests tools`, `--doctest-modules`) is the real configuration and takes precedence.

**The scripts stay** (William Emerison Six <billsix@gmail.com>, 2026-11-09). All three improvements are approved (William Emerison Six <billsix@gmail.com>, 2026-11-09):

1. **A `make spyder` target.** Today `spyder.sh` is reachable only by typing it inside `make shell`.
   The target would mirror `shell`'s X11/Wayland flags. Because `USE_SPYDER` defaults to 0, it would
   start with the template's flag-echo guard (`@[ "$(USE_SPYDER)" = 1 ] || { echo "Spyder isn't in
   the image: export USE_SPYDER=1, make image, then make spyder"; exit 2; }`), and depend on `: image`.
2. **A preflight in `spyder.sh`**, for running it by hand: `command -v spyder >/dev/null || { echo
   "spyder not installed; rebuild with make image USE_SPYDER=1" >&2; exit 2; }`. On today's default
   image it dies with a bare `spyder: command not found`.
3. **`percentToIpynb.sh` converts every notebook**, not only `displaymv.py`: the files named as
   arguments, defaulting to all of `notebooks/*.py`. Add a `make notebooks-ipynb` target.
   JupyterLab already opens the `.py` files directly (`jupytext-config set-default-viewer`), so this
   is only for exporting `.ipynb`.

## Plan

- [ ] Delete the `[tool.pytest]` block. Compare the collected count from `make test` before and after.
- [ ] Add `make spyder` (`## `-documented, `: image`, the flag-echo guard, `shell`'s X11/Wayland
  flags and `PODMAN_RUN_FLAGS`).
- [ ] Add the `command -v spyder` preflight to `entrypoint/spyder.sh`.
- [ ] Make `entrypoint/percentToIpynb.sh` take file arguments and default to `notebooks/*.py`, and add
  `make notebooks-ipynb` (`: image`). Gitignore the `.ipynb` output if it isn't already.
- [ ] `make help`; `make notebooks-ipynb`; `make spyder` with `USE_SPYDER=0` shows the guard message.
  Starting Spyder on a real display is the maintainer's check.
- [ ] `make format`.

## Open questions

None.
