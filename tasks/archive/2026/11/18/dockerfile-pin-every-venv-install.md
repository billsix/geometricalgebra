# Dockerfile: install each venv package once, pinned; silence uv's hardlink warning (done)

**Done:** 2026-11-18 (William Emerison Six <billsix@gmail.com>)

`make image` printed uv's "Failed to hardlink files" warning, and the pinned dependency layer (the
`COPY … constraints.txt` + `RUN` near the end of `Dockerfile`) downgraded about a dozen packages that
earlier layers had installed unpinned (on a 2026-11-18 build: numpy 2.5.5→2.5.4, docutils, tornado,
markdown-it-py, mdit-py-plugins, soupsieve, myst-parser, sqlalchemy, importlib-metadata). The final
`/venv` was already right. The changes remove the redundant work:

- The venv-creation `RUN` installs only `setuptools wheel`, which the ePiX layer's
  `--no-build-isolation` editable install of `epix-mirror/python` needs. `numpy sympy` were dropped;
  nothing before the pinned layer uses them.
- The `BUILD_DOCS` TeX `RUN` keeps only `04-install-docs.sh`. Its unpinned
  `uv pip install sphinx furo nbsphinx myst-nb` was removed, because the pinned layer already
  installs that set under `BUILD_DOCS`. The comment above it says where the install happens.
- The pinned layer's comment names what is still installed early (setuptools/wheel and ePiX's
  nanobind) and why, and `ENV UV_LINK_MODE=copy` is set just before it. The uv cache mount is a
  different filesystem from the layer, so uv has to copy.

**Decision on the open question** (2026-11-18, William Emerison Six <billsix@gmail.com>, taking the
recommendation): setuptools/wheel/nanobind stay unpinned in the early layers. Pinning them would
mean `COPY constraints.txt` before the ePiX layer, so every `make update-pins` would rebuild the
ePiX, GL and texExp layers.

Verified nested on 2026-11-18 with default flags (`USE_EPIX=1`, `BUILD_DOCS=1`):
- `make image`: no hardlink warning, and no `-` (uninstall) lines anywhere in the log, so each
  package was installed once.
- `make test`: 1913 passed, 2 skipped.
- `make docs`: HTML + PDF built. This exercises the Sphinx set now installed only in the pinned layer.

The rule is recorded in the `python-coding-standard.md` reference doc in
github.com/billsix/runClaudeInContainer ("Pin direct dependencies").
