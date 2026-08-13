#!/usr/bin/env bash
#
# 01-install-base.sh -- the always-needed Fedora packages for this project.
#
# One package group per script, no options: WHICH optional groups also get installed is
# decided by the Dockerfile's ARG `if` blocks (or by a human choosing which scripts to
# run). Same packages during `podman build`, on a bare Fedora host, or in a guest with
# no container runtime. `dnf upgrade` stays in the Dockerfile (it runs in its own earlier
# layer, before the dotfiles COPY). Emacs is unconditional here, matching the original
# Dockerfile (the USE_EMACS ARG is declared but was never wired to a dnf group).
#
# Several dnf calls, so accumulate a non-zero exit if any fails.
set -uo pipefail

if ! command -v dnf >/dev/null 2>&1; then
    echo "01-install-base.sh: needs 'dnf' (this installs Fedora packages), not found." >&2
    echo "Run on a Fedora host/guest, or inside the project's Fedora-based image." >&2
    exit 1
fi

status=0

dnf install -y \
    emacs \
    python3 \
    python3-setuptools \
    python3-sympy \
    python3-pandas \
    python3-pytest \
    python3-wheel \
    ruff \
    emacs-gtk+x11 \
    emacs-pgtk \
    tmux \
    uv \
    ty \
    which || status=1

dnf install -y pinentry || status=1

# libatomic is a runtime dependency of pyright (the Dockerfile pip-installs pyright into
# the venv). Installed unconditionally, as in the original Dockerfile.
dnf install -y libatomic || status=1

exit $status
