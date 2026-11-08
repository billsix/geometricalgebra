# Publish Jupyter's port 8888 on 127.0.0.1 only

**Created:** 2026-11-08 · **Completed:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §8.1 (the security finding)

## What was wrong

`entrypoint/jupyter.sh` runs JupyterLab with no token, no password and XSRF checks off. The
Makefile's `EXPOSE_PORT = -p 8888:8888` published that port on every host interface. Anyone who
could reach the host on port 8888 could therefore run code in the container, which has the repo
mounted read-write.

`EXPOSE_PORT` is used by `make jupyter`, and by `make shell`/`make shell-exec` through
`SHELL_RUN_FLAGS`.

## What changed

`EXPOSE_PORT` is now `-p 127.0.0.1:8888:8888`, so only the host's loopback interface reaches the
server. A comment at the definition says why.

Inside the container the server still listens on `0.0.0.0`, which the published port needs. The
documented URL, `http://127.0.0.1:8888/lab` (in `README.md` and the `jupyter` target's help text),
is unchanged.

## Verification

- `make help` runs clean.
- `make -n jupyter USE_JUPYTER=1` and `make -n shell` both show `-p 127.0.0.1:8888:8888` in their
  `run` lines.
- A live `make jupyter` was not run: the session's nested image is the lean one, without JupyterLab.
