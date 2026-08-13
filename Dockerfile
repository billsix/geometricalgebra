FROM registry.fedoraproject.org/fedora:44

ARG USE_SPYDER=0
ARG USE_EMACS=0
# BUILD_DOCS defaults to 0 here so a bare `podman build` stays lean; the Makefile
# passes BUILD_DOCS=1 so `make image` builds the Sphinx-book toolchain in.
ARG BUILD_DOCS=0

RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    echo "keepcache=True" >> /etc/dnf/dnf.conf && \
    dnf upgrade -y

COPY entrypoint/dotfiles/ /root/

# System-package installation lives in per-group scripts (entrypoint/0N-install-*.sh),
# host-runnable with no container runtime; the scripts take no options -- WHICH optional
# groups run is decided here by the ARG `if` blocks. base + notebook-tex are always
# installed; spyder/docs are flag-gated. The dnf cache mount + keepcache stay in the
# Dockerfile (build plumbing); `dnf upgrade` ran in the earlier layer above. Config that
# writes container paths (spyder.ini, the venv pip installs) also stays in the Dockerfile.
COPY entrypoint/01-install-base.sh \
     entrypoint/02-install-spyder.sh \
     entrypoint/03-install-notebook-tex.sh \
     entrypoint/04-install-docs.sh /usr/local/bin/

RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    /usr/local/bin/01-install-base.sh ; \
    if [ "$USE_SPYDER" = "1" ]; then \
      /usr/local/bin/02-install-spyder.sh && \
      mkdir -p ~/.config/spyder-py3/config && \
      echo "[editor]" >> ~/.config/spyder-py3/config/spyder.ini && \
      echo "font/family = Source Code Pro" >> ~/.config/spyder-py3/config/spyder.ini && \
      echo "font/size = 24" >> ~/.config/spyder-py3/config/spyder.ini && \
      echo "[file_explorer]" >> ~/.config/spyder-py3/config/spyder.ini && \
      echo "visible = False" >> ~/.config/spyder-py3/config/spyder.ini && \
      echo "[tours]" >> ~/.config/spyder-py3/config/spyder.ini && \
      echo "show_tour_message = False" >> ~/.config/spyder-py3/config/spyder.ini && \
      echo "[appearance]" >> ~/.config/spyder-py3/config/spyder.ini && \
      echo "font/family = Adwaita Mono" >> ~/.config/spyder-py3/config/spyder.ini && \
      echo "font/size = 18" >> ~/.config/spyder-py3/config/spyder.ini; \
    fi ; \
    echo "/usr/local/bin/jupyter.sh # on http://127.0.0.1:8888/lab" >> ~/.bash_history && \
    echo "emacs src/gacalc/gn.py tests/test_multivector.py &" >> ~/.bash_history && \
    echo "source ~/.extrabashrc" >> ~/.bashrc && \
    echo "from gacalc.gn import *" >> ~/.python_history  && \
    python3 -m venv --system-site-packages /venv/ && \
    export VIRTUAL_ENV_DISABLE_PROMPT=1 && \
    source /venv/bin/activate && \
    uv pip install --python $(which python) setuptools wheel numpy sympy && \
    uv pip install --python $(which python) pyright

# Notebook "Export to PDF": nbconvert's PDF path renders the notebook through
# pandoc -> XeLaTeX, so the image needs pandoc plus a XeLaTeX toolchain with the
# packages nbconvert's default LaTeX template pulls in. This set was verified end
# to end against a math-heavy notebook (`jupyter nbconvert --to pdf --execute`):
# the recommended font/latex collections cover most of it, and the named helper
# packages (adjustbox/tcolorbox/ucs/soul/ulem/titling/enumitem/rsfs/mathrsfs via
# jknapltx/...) are the template's specific dependencies. Installed
# unconditionally, alongside the always-present jupyter stack above.
RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    /usr/local/bin/03-install-notebook-tex.sh

# Sphinx book toolchain (`make docs` -> HTML + PDF). Gated behind BUILD_DOCS so a
# bare `podman build` stays lean; `make image` sets BUILD_DOCS=1. The PDF is built
# with LuaLaTeX (conf.py sets latex_engine=lualatex) because gacalc's docstrings
# carry Unicode math (√ ∧ · e₁ ...) that pdfLaTeX cannot typeset: texlive-luahbtex
# provides the `lualatex` binary, fontspec + gnu-freefont its fonts. The texlive-*
# helper packages are the ones Sphinx's generated LaTeX \usepackage's -- verified
# by building this book end to end. The recommended latex/font *collections* are
# already installed just above (for nbconvert), so this block only adds the rest.
#
# Sphinx and the doc extensions install into the VENV (uv pip), NOT via dnf, so
# `sphinx-build` runs as /venv/bin/python. This is load-bearing for the book's
# executable notebooks: myst_nb launches its Jupyter kernel from sphinx's OWN
# sys.prefix, so a venv sphinx selects the venv `python3` kernel -- which, via
# docs.sh's editable install, imports gacalc. A *system* sphinx (dnf) runs as
# /usr/bin/python3 and selects the system kernel, which CANNOT import gacalc, so
# every notebook importing gacalc fails silently. This is how modelviewprojection
# does it (docs toolchain in the venv). Only the LaTeX packages stay in dnf.
#
# ImageMagick provides `convert`, which sphinx.ext.imgconverter uses to turn the
# book's .svg figures into PDF for the LaTeX build. It used to arrive as a
# transitive dependency of python3-sphinx; now that sphinx is a venv (pip) package,
# it must be requested explicitly.
RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    if [ "$BUILD_DOCS" = "1" ]; then \
      /usr/local/bin/04-install-docs.sh ; \
      uv pip install --python /venv/bin/python sphinx furo nbsphinx myst-nb ; \
    fi

# Copy the build-relevant project files (not the whole tree: the 31M vendored
# Emacs elpa tree is already at /root, and .dockerignore is global so it can't be
# excluded for just this COPY). Placed after the slow dnf/MELPA layers so editing
# source doesn't re-run them. At runtime `make shell`'s bind mount overlays
# /gacalc with the live host tree, so this copy is only used for the build below.
COPY pyproject.toml setup.py README.md /gacalc/
COPY src   /gacalc/src
COPY tools /gacalc/tools

# Install the package + ALL its optional extras from pyproject's own
# [project.optional-dependencies] -- the single source of truth (no requirements.txt,
# no hardcoded package list). Build prereqs (setuptools/wheel/numpy/sympy) are
# installed above, so --no-build-isolation reuses them; the setup.py build_py hook
# generates the algebras if missing. (This layer re-runs when src/ changes, so the
# notebook/jupyter deps reinstall then -- uv's cache keeps that fast.)
RUN export VIRTUAL_ENV_DISABLE_PROMPT=1 && source /venv/bin/activate && \
    cd /gacalc && uv pip install --python $(which python) --no-build-isolation ".[dev,notebooks,jupyter]" && \
    jupytext-config set-default-viewer python && \
    jupyter labextension disable "@jupyterlab/apputils-extension:announcements"


ENTRYPOINT ["/entrypoint.sh"]
