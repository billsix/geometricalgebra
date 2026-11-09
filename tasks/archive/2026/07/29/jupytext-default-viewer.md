# Make JupyterLab open py:percent files as notebooks by default

**Completed:** 2026-07-29

## Goal

In the JupyterLab web interface (`make jupyter`), a single click on a jupytext py:percent `.py`
file opens it **as a notebook**, without right-click → "Open With → Notebook". Accepted trade-off:
`.py` files no longer open as plain text by default in JupyterLab; a regular text editor covers that
case.

## The change

The `Dockerfile` runs `jupytext-config set-default-viewer python` inside `/venv`, after the layer
that installs the package extras (`uv pip install ... ".[dev,notebooks,jupyter]"`):

```dockerfile
RUN export VIRTUAL_ENV_DISABLE_PROMPT=1 && source /venv/bin/activate && \
    jupytext-config set-default-viewer python
```

## Constraints checked (2026-07-29)

- `jupytext-config` is a console script of the `jupytext` package, installed via the `notebooks`
  extra in `pyproject.toml` into `/venv`, so it exists only after that install layer and only inside
  the venv.
- It writes `~/.jupyter/labconfig/default_setting_overrides.json` for the build user (root). The
  container runs as root and the Makefile mounts nothing over `/root/.jupyter` (only `.tmux.conf`,
  `.gitconfig`, `.gnupg`, `.pypirc`, emacs `elpa`), so the baked config is what `make jupyter` sees.
- No `jupytext-config` / `set-default-viewer` call existed anywhere in the repo before (Dockerfile,
  Makefile, `entrypoint/*.sh` grepped).

## Verification (2026-07-29)

1. `make image` passed (nested podman).
2. In the built image, `jupytext-config list-default-viewer` printed `python: Jupytext Notebook`.
3. `/root/.jupyter/labconfig/default_setting_overrides.json` exists and sets
   `@jupyterlab/docmanager-extension:plugin` → `defaultViewers` → `python: "Jupytext Notebook"`
   (note the `:plugin` suffix on the real key).

The interactive browser check (`make jupyter`, open http://127.0.0.1:8888/lab, single-click a
py:percent file) was left to the maintainer.
