#!/usr/bin/env bash
#
# 07-install-gl.sh -- the Fedora packages gacalc.gl (the `gl` extra) needs to open an
# OpenGL window. Host-runnable: run it after 01-install-base.sh.
#
#   glfw                the GLFW C library the glfw Python package loads
#   mesa-libGL          libGL, which PyOpenGL loads under X11 (GLX)
#   mesa-libEGL         libEGL, which PyOpenGL loads under Wayland
#   mesa-dri-drivers    Mesa's drivers; with no GPU passed through they render in
#                       software (llvmpipe), so a window still opens
#
# This group is not behind a feature flag: `make test` imports gacalc.gl for its
# doctests, so the lean CI image (MINIMAL_IMAGE=1) needs it too. It has its own late
# Dockerfile layer so that adding it did not rebuild the slow layers before it.
set -uo pipefail

dnf install -y glfw mesa-dri-drivers mesa-libEGL mesa-libGL
