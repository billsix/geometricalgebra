# Suppress JupyterLab's "official Jupyter news" notification prompt

**Completed:** 2026-07-29

## Goal

`make jupyter` comes up without the "Would you like to receive official Jupyter news?" toast. The
prompt is JupyterLab's built-in announcements plugin
(`@jupyterlab/apputils-extension:announcements`) phoning the news feed; disabling the plugin removes
both the prompt and the fetch.

## The change

In the `Dockerfile`, the same venv-activated `RUN` that runs `jupytext-config set-default-viewer
python` (after the `uv pip install ... ".[dev,notebooks,jupyter]"` layer) gained:

```dockerfile
    jupytext-config set-default-viewer python && \
    jupyter labextension disable "@jupyterlab/apputils-extension:announcements"
```

With `/venv` active, the command writes `/venv/etc/jupyter/labconfig/page_config.json`
(`{"disabledExtensions": {"@jupyterlab/apputils-extension:announcements": true}}`), a sys-prefix
setting, so it must run with the venv activated. Nothing in the Makefile mounts over `/venv`, so the
baked config survives to `make jupyter`.

**Lock:** the command warns that since JupyterLab 4.1 a user can re-enable disabled plugins in the
UI unless they are locked (`jupyter labextension lock`). A separate lock step was judged unnecessary
for a single-user teaching container, and turned out not to be needed anyway: this JupyterLab
version **auto-locks** the plugin when disabling at sys-prefix level (`lockedExtensions` written
alongside `disabledExtensions`), so users cannot re-enable it from the UI.

## Verification (2026-07-29)

`make image` passed; in the built image the plugin lists under "Disabled extensions",
`/venv/etc/jupyter/labconfig/page_config.json` has the entry, and the jupytext default-viewer
setting survived (regression check, `tasks/archive/2026/07/29/jupytext-default-viewer.md`).

The browser check (`make jupyter`, open http://127.0.0.1:8888/lab in a fresh browser profile or
private window, since a browser-side "answered" flag can make an already-used profile false-pass)
was left to the maintainer.
