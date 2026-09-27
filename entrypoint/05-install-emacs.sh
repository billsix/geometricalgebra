#!/usr/bin/env bash
#
# 05-install-emacs.sh -- Emacs (the maintainer's editor) + its GTK/pgtk builds. Its
# own package group, gated by the Dockerfile's USE_EMACS ARG (the Makefile builds it
# in on a host and skips it in a lean nested image). No options -- WHICH optional
# groups run is decided by the Dockerfile's `if` blocks; see 01-install-base.sh for
# the design. Host-runnable: on a bare Fedora host, run this to add Emacs.
#
# Single dnf call, so its own exit status is this script's exit status.
set -uo pipefail

dnf install -y \
    emacs \
    emacs-gtk+x11 \
    emacs-pgtk
