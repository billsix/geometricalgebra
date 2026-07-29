# Make JupyterLab open py:percent files as notebooks by default

**Status:** proposed — needs go-ahead to implement

## Goal

In the JupyterLab web interface (`make jupyter`), a single click on a
jupytext py:percent `.py` file should open it **as a notebook**, without the
user having to right-click → "Open With → Notebook". Accepted trade-off:
`.py` files no longer open as plain text by default in JupyterLab — a
regular text editor covers that case.

## The change

Add to the `Dockerfile`, immediately after the layer that installs the
package extras (the `uv pip install ... ".[dev,notebooks,jupyter]"` RUN at
the end of the Dockerfile, currently around line 106–107):

```dockerfile
RUN export VIRTUAL_ENV_DISABLE_PROMPT=1 && source /venv/bin/activate && \
    jupytext-config set-default-viewer python
```

(Or fold it into that same RUN layer — implementer's choice; keeping it in
the same layer avoids an extra layer but re-runs the install layer's cache
key semantics unchanged either way.)

## Why this works / constraints checked (2026-07-29)

- `jupytext-config` is a console script shipped by the `jupytext` package,
  which this repo installs via the `notebooks` extra in `pyproject.toml`
  (`notebooks = [... "jupytext"]`) into `/venv`. So the command exists only
  **after** that install layer and only **inside the venv** — the RUN must
  `source /venv/bin/activate` (or call `/venv/bin/jupytext-config`).
- It writes `~/.jupyter/labconfig/default_setting_overrides.json` for the
  build user (root → `/root/.jupyter/...`). The container runs as root and
  the Makefile mounts nothing over `/root/.jupyter` (checked: only
  `.tmux.conf`, `.gitconfig`, `.gnupg`, `.pypirc`, emacs `elpa`), so the
  baked config is what `make jupyter` sees.
- No `jupytext-config` / `set-default-viewer` call exists anywhere in the
  repo today (grepped Dockerfile, Makefile, entrypoint/*.sh).

## Verification

1. `make image` (nested podman: transient `--cgroups=disabled` per standing
   arrangement).
2. In the built image:
   `source /venv/bin/activate && jupytext-config list-default-viewer`
   → should print `python`.
3. Confirm `/root/.jupyter/labconfig/default_setting_overrides.json` exists
   in the image and names `@jupyterlab/docmanager-extension` →
   `defaultViewers` → `python: "Jupytext Notebook"`.
4. Real check: `make jupyter`, open http://127.0.0.1:8888/lab, single-click
   a py:percent notebook file — it must open in the notebook editor.
