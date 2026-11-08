# Publish Jupyter's port 8888 on 127.0.0.1 only

**Status:** proposed — needs go-ahead (approved in session 2026-11-08; in progress)
**Priority:** 1
**Difficulty:** 1
**Created:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §8.1 (the security finding)

## BLUF

`make jupyter` serves an unauthenticated JupyterLab, and the Makefile publishes its port on every
host interface. The fix is to publish the port on `127.0.0.1` only, so only the host itself can
reach the server. Done means `EXPOSE_PORT` binds to loopback, and `make help` and a dry run still
work.

## Context

What the server runs with:

- `entrypoint/jupyter.sh` starts JupyterLab with `--ip=0.0.0.0`, `--ServerApp.token=''`,
  `--ServerApp.password=''` and `--ServerApp.disable_check_xsrf=True`.
- The script's own comment ("super dangerous, but for our purposes, it's fine") assumes only the
  maintainer can reach it.

Why that assumption fails:

- `Makefile`'s `EXPOSE_PORT = -p 8888:8888` makes podman listen on all host interfaces.
- Anyone who can reach the host on port 8888 can then run code in the container, and the container
  has the repo mounted read-write.
- `EXPOSE_PORT` is used by `jupyter` and by `shell`/`shell-exec` (through `SHELL_RUN_FLAGS`), so all
  three are affected.

What stays as it is:

- `--ip=0.0.0.0` *inside* the container is correct: the server has to listen on the container's
  interface for the published port to reach it. The exposure comes from the host-side publish
  address.
- `README.md` says Jupyter is on `http://127.0.0.1:8888/lab` (the `jupyter` target's help text says
  so too), so binding to loopback changes nothing for the documented use.

## Plan

- [ ] Change `EXPOSE_PORT` to `-p 127.0.0.1:8888:8888`, with a comment saying why.
- [ ] Verify with `make help` and `make -n jupyter` (dry run) that the flag is in the `run` line.
- [ ] Stage, commit.

## Open questions

None.
