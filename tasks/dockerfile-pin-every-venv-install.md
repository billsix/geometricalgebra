# Dockerfile: install each venv package once, pinned; silence uv's hardlink warning

**Status:** open (approved 2026-11-18 by William Emerison Six <billsix@gmail.com>; not started)
**Priority:** 8
**Difficulty:** 2
**Started:** 2026-11-18 (William Emerison Six <billsix@gmail.com>)

## BLUF

`make image` prints uv's "Failed to hardlink files" warning, and the constrained install layer
(the `COPY … constraints.txt` + `RUN` near the end of `Dockerfile`) downgrades about a dozen
packages that earlier layers installed unpinned. Neither changes the final `/venv`, which
matches `constraints.txt`. This is tidying: drop the redundant unpinned installs and set
`UV_LINK_MODE=copy`. Done = `make image` succeeds, the constrained layer prints no `-`/`+`
downgrade pairs for numpy/sympy/sphinx-family packages, and the hardlink warning is gone.

## Context

- **The hardlink warning.** Every `uv pip install` that runs under
  `RUN --mount=type=cache,target=/root/.cache/uv` has its cache on a different mount from the
  `/venv` layer. uv can't hardlink across mounts, so it copies and warns. Copying is what is
  needed anyway (the cache mount is discarded after the build), so the fix is just to state
  it: `ENV UV_LINK_MODE=copy` once, early in `Dockerfile`.
- **The downgrades.** Two layers install without `-c constraints.txt`, because
  `constraints.txt` is only `COPY`'d late (so a `make update-pins` doesn't re-run the slow
  TeX/ePiX layers):
  - The venv-creation `RUN` (the one ending `uv pip install … setuptools wheel numpy sympy`).
  - The `BUILD_DOCS` TeX `RUN` (`04-install-docs.sh` then `uv pip install … sphinx furo nbsphinx myst-nb`).

  The constrained layer then re-installs those under the pins. Example from a 2026-11-18
  build: numpy 2.5.5→2.5.4, docutils 0.23→0.22.4, tornado 6.6.1→6.6, markdown-it-py,
  mdit-py-plugins, soupsieve, then myst-parser 5.2.0→5.1.0, sqlalchemy, importlib-metadata.
- **What still needs the venv before the constrained layer:** the `USE_EPIX` layer runs
  `entrypoint/install-epix.sh`, which `uv pip install`s nanobind (unpinned there, since
  `CONSTRAINTS` is unset at that point) and editable-installs `epix-mirror/python` with
  `--no-build-isolation`, which needs **setuptools** already in the venv
  (epix-mirror's `python/pyproject.toml` declares `setuptools>=61`). Nothing before the
  constrained layer uses numpy, sympy, or the Sphinx packages. Checked 2026-11-18: the
  `07-install-gl.sh` and texExp layers don't touch the venv, and epix-mirror's
  `entrypoint/build_py.sh` only imports `sysconfig` and `nanobind`.

## Plan

1. Add `ENV UV_LINK_MODE=copy` (with a one-line comment: the cache mount and `/venv` are
   different filesystems, so uv must copy) before the first `uv pip install`.
2. Venv-creation `RUN`: install only `setuptools wheel` (the ePiX editable install's build
   backend). Drop `numpy sympy`.
3. `BUILD_DOCS` TeX `RUN`: remove the `uv pip install … sphinx furo nbsphinx myst-nb`. The
   constrained layer already installs them under `BUILD_DOCS`. Update the long comment above
   that `RUN` ("Sphinx and the doc extensions install into the VENV …") so it says where the
   install now happens, and fix the comment in `entrypoint/04-install-docs.sh` that says
   "The Sphinx/doc-extension pip installs stay in the Dockerfile" if its wording no longer fits.
4. Reword the constrained layer's comment ("The earlier, slower layers install their few pip
   packages …") to name what is still installed early (setuptools/wheel/nanobind for ePiX)
   and why.
5. Verify: `make image` (default flags, so `USE_EPIX=1` and `BUILD_DOCS=1` are exercised);
   the constrained layer shows only `+` lines except possibly setuptools/wheel/nanobind; no
   hardlink warning; then `make test`.

## Open questions

1. Should setuptools/wheel/nanobind be pinned in the early layers too? Doing that means
   `COPY constraints.txt` before the ePiX layer (and passing `CONSTRAINTS=` to
   `install-epix.sh`, which already supports it), so every `make update-pins` re-runs the
   ePiX, GL and texExp layers. Recommendation: no. Leave them unpinned and let the
   constrained layer correct them; on 2026-11-18 nanobind already matched (`Checked 1 package`).
