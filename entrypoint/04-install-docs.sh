#!/usr/bin/env bash
#
# 04-install-docs.sh -- the LaTeX packages the Sphinx book's PDF build \usepackage's
# (LuaLaTeX toolchain + helpers), plus ImageMagick for svg->pdf figure conversion.
# Corresponds to the Dockerfile's BUILD_DOCS flag; the Dockerfile runs this only when
# BUILD_DOCS=1. The Sphinx/doc-extension pip installs stay in the Dockerfile (they go
# into the venv, not dnf). No options -- see 01-install-base.sh for the design.
#
# Single dnf call, so its own exit status is this script's exit status.
set -uo pipefail

dnf install -y \
    ImageMagick \
    latexmk \
    texlive-luahbtex \
    texlive-luatex85 \
    texlive-lualatex-math \
    texlive-fontspec \
    texlive-gnu-freefont \
    texlive-fncychap \
    texlive-wrapfig \
    texlive-capt-of \
    texlive-needspace \
    texlive-tabulary \
    texlive-framed \
    texlive-titlesec \
    texlive-varwidth \
    texlive-fancyhdr \
    texlive-multirow \
    texlive-threeparttable \
    texlive-eqparbox
