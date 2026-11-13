#!/usr/bin/env bash
#
# 08-install-tex-labels.sh -- the Fedora packages for the graphing calculators' TeX
# labels: what install-texexp.sh needs to build texExpToPng, and the TeX set
# texExpToPng runs at label time. Host-runnable: run it after 01-install-base.sh,
# then install-texexp.sh.
#
#   gcc git glib2-devel meson ninja-build
#                       fetch and build texExpToPng (a small C program on GLib)
#   texlive texlive-amsmath texlive-anyfontsize texlive-standalone
#   texlive-varwidth texlive-xcolor
#                       `latex` and the packages texExpToPng's preamble loads
#                       (\documentclass[varwidth]{standalone}, amsmath, xcolor)
#   texlive-dvipng      turns the .dvi into the transparent PNG gacalc.gl.labels
#                       uploads as a texture
set -uo pipefail

dnf install -y gcc git glib2-devel meson ninja-build \
    texlive texlive-amsmath texlive-anyfontsize texlive-dvipng \
    texlive-standalone texlive-varwidth texlive-xcolor
