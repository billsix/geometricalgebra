#!/usr/bin/env bash
#
# 03-install-notebook-tex.sh -- pandoc + the XeLaTeX toolchain that nbconvert's
# "Export to PDF" path renders through. The Dockerfile runs it when USE_JUPYTER=1 or
# BUILD_DOCS=1 (the book's LaTeX build relies on its collections). Kept as its own
# group because it is a distinct, documented set separate from the base toolchain.
# No options -- see 01-install-base.sh for the design.
#
# Single dnf call, so its own exit status is this script's exit status.
set -uo pipefail

dnf install -y \
    pandoc \
    texlive-xetex \
    texlive-collection-fontsrecommended \
    texlive-collection-latexrecommended \
    texlive-adjustbox \
    texlive-tcolorbox \
    texlive-collectbox \
    texlive-ucs \
    texlive-titling \
    texlive-enumitem \
    texlive-rsfs \
    texlive-jknapltx \
    texlive-upquote \
    texlive-ulem \
    texlive-soul \
    texlive-eurosym \
    texlive-pgf \
    texlive-environ \
    texlive-trimspaces \
    texlive-parskip
