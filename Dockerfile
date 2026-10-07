FROM registry.fedoraproject.org/fedora:44

# Every optional-feature ARG defaults to 0 so a bare `podman build` stays lean; the
# Makefile passes each flag's real value (full on a host, lean when built nested --
# see the Makefile flag block and runClaudeInContainer
# tasks/reference/minimal-nested-images.md).
ARG USE_SPYDER=0
ARG USE_EMACS=0
ARG BUILD_DOCS=0
# USE_JUPYTER gates the pandoc + XeLaTeX toolchain nbconvert's notebook "Export to
# PDF" renders through (03-install-notebook-tex.sh). USE_LEAN gates the Lean 4
# theorem-prover toolchain (install-lean.sh). Neither is needed by `make test`.
ARG USE_JUPYTER=0
ARG USE_LEAN=0
# USE_EPIX bakes the maintainer's ePiX mirror (C++ figure library + the epix/elaps
# drivers) for the book's LaTeX-native figures; EPIX_COMMIT is the ONE place its pin
# lives (tasks/epix-plot-integration.md). `make test` needs neither.
ARG USE_EPIX=0
ARG EPIX_COMMIT=ebf3ca607ae6c1d4fa307e8b0359960d875d219c

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
     entrypoint/04-install-docs.sh \
     entrypoint/05-install-emacs.sh /usr/local/bin/

RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    /usr/local/bin/01-install-base.sh ; \
    if [ "$USE_EMACS" = "1" ]; then /usr/local/bin/05-install-emacs.sh ; fi ; \
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
# jknapltx/...) are the template's specific dependencies.
#
# Gated behind USE_JUPYTER (its own feature: notebook PDF export) OR BUILD_DOCS --
# the Sphinx-book LaTeX block below (04-install-docs.sh) relies on the "recommended"
# font/latex COLLECTIONS this installs, so the docs build needs it too. When both
# flags are 0 (the lean nested image) no TeX is installed at all; `make test` needs
# none of it.
RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    if [ "$USE_JUPYTER" = "1" ] || [ "$BUILD_DOCS" = "1" ]; then \
      /usr/local/bin/03-install-notebook-tex.sh ; \
    fi

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

# Lean 4 (theorem prover) via elan — host-runnable script, curl-installed; bakes the
# stable toolchain so an exported image has Lean offline. Gated behind USE_LEAN: the
# Lean toolchain is a large download not needed by `make test`, so a lean nested image
# skips it. The PATH entry is harmless when the dir is absent, so it stays unconditional.
#
# CACHE ORDERING: this block (Lean toolchain + the multi-GB Mathlib bake below) is
# entirely independent of the project source -- it needs only install-lean.sh and
# proofs/'s dep-defining files, NOT src/ or tools/. It is therefore placed BEFORE
# `COPY src`/`COPY tools` (which change on every code edit): editing src/ or tools/
# only rebusts the cheap COPY + editable-install layers at the end, and NEVER this
# large Lean/Mathlib bake. (Previously this block sat after COPY src, so every code
# change re-baked Mathlib -- minutes-long. Moved 2026-09-28.)
COPY entrypoint/install-lean.sh /usr/local/bin/
RUN if [ "$USE_LEAN" = "1" ]; then /usr/local/bin/install-lean.sh ; fi
ENV PATH="/root/.elan/bin:${PATH}"

# Bake Mathlib into the image (a committed layer OUTSIDE the bind-mounted repo) so
# `make lean` runs OFFLINE -- the "deps fetched at build, offline thereafter" rule.
# Only proofs/'s dep-defining files are staged here (NOT the .lean sources), so
# editing a proof doesn't rebust this layer -- and, being before COPY src (see the
# CACHE ORDERING note above), editing src/ doesn't either. `lake exe cache get`
# clones the pinned Mathlib and downloads its prebuilt oleans into
# /opt/gacalc-proofs/.lake; proofs/check.sh copies that into the (mounted, gitignored)
# proofs/.lake at runtime -- the bind-mount would otherwise shadow a baked
# proofs/.lake. Gated on USE_LEAN (adds several GB, so only Lean images pay it). git
# (needed to clone Mathlib) is installed by install-lean.sh above.
COPY proofs/lakefile.toml proofs/lean-toolchain proofs/lake-manifest.json /opt/gacalc-proofs/
RUN if [ "$USE_LEAN" = "1" ]; then \
      cd /opt/gacalc-proofs && touch GacalcProofs.lean && lake exe cache get ; \
    fi

# ePiX (github.com/billsix/epix-mirror), pinned to EPIX_COMMIT, built from source with
# Meson into /usr/local -- the `epix`/`elaps`/`flix`/`laps` drivers + libepix for the
# book's LaTeX-native figures (decision 2026-10-06: epix COEXISTS with the matplotlib
# plotting in nbplotutils.py; it is the book's figure source, not the notebooks').
# Two host-runnable scripts: 06-install-epix.sh (dnf: git, meson/g++, ghostscript,
# ImageMagick, the TeX set epix's own render script names) then install-epix.sh (shallow
# git fetch of the pinned commit, meson install). Gated on USE_EPIX; placed before
# COPY src for the same cache-ordering reason as the Lean block above. The fetch is
# the only network use and happens at build time; the installed tools run offline.
COPY entrypoint/06-install-epix.sh entrypoint/install-epix.sh /usr/local/bin/
RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    if [ "$USE_EPIX" = "1" ]; then \
      /usr/local/bin/06-install-epix.sh && \
      EPIX_COMMIT="$EPIX_COMMIT" /usr/local/bin/install-epix.sh ; \
    fi

# Copy the build-relevant project files (not the whole tree: the 31M vendored
# Emacs elpa tree is already at /root, and .dockerignore is global so it can't be
# excluded for just this COPY). Placed LAST, after every slow source-independent
# layer (dnf/MELPA/TeX + the Lean/Mathlib bake above), so editing source rebusts
# only this COPY and the editable install below -- nothing expensive. At runtime
# `make shell`'s bind mount overlays /gacalc with the live host tree, so this copy
# is only used for the build below.
COPY pyproject.toml setup.py README.md /gacalc/
COPY src   /gacalc/src
COPY tools /gacalc/tools

# Install the package + ALL its optional extras from pyproject's own
# [project.optional-dependencies] -- the single source of truth (no requirements.txt,
# no hardcoded package list). Build prereqs (setuptools/wheel/numpy/sympy) are
# installed above, so --no-build-isolation reuses them; the setup.py build_py hook
# generates the algebras if missing. This layer re-runs when src/ changes, so the
# notebook/jupyter deps would reinstall then -- the uv CACHE MOUNT below keeps that
# fast (reuses already-downloaded wheels, incl. JupyterLab). The cache is discarded
# (not in the image), but the deps still land in the committed /venv, so an exported
# image stays self-contained -- the mount only speeds the rebuild.
RUN --mount=type=cache,target=/root/.cache/uv \
    export VIRTUAL_ENV_DISABLE_PROMPT=1 && source /venv/bin/activate && \
    cd /gacalc && uv pip install --python $(which python) --no-build-isolation ".[dev,notebooks,jupyter]" && \
    jupytext-config set-default-viewer python && \
    jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

ENTRYPOINT ["/entrypoint.sh"]
