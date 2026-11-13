FROM registry.fedoraproject.org/fedora:45

RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    echo "keepcache=True" >> /etc/dnf/dnf.conf && \
    dnf upgrade -y

# Every optional-feature ARG defaults to 0 so a bare `podman build` stays lean; the
# Makefile passes each flag's real value (full by default, host or nested; lean with
# `make image MINIMAL_IMAGE=1` -- see the Makefile flag block and runClaudeInContainer
# tasks/reference/minimal-nested-images.md). Each ARG is declared just before the
# first layer that reads it, never all at the top: a build-arg's value is part of
# the cache key of EVERY later RUN (used or not), so a top-of-file ARG makes
# changing any flag, or bumping EPIX_COMMIT, rebuild everything below it,
# including the multi-GB Lean/Mathlib bake.
#
# USE_LEAN gates the Lean 4 theorem-prover toolchain (install-lean.sh) and the
# Mathlib bake. `make test` needs neither.
ARG USE_LEAN=0

# Lean 4 (theorem prover) via elan — host-runnable script, curl-installed; bakes the
# stable toolchain so an exported image has Lean offline. Gated behind USE_LEAN: the
# Lean toolchain is a large download not needed by `make test`, so a lean nested image
# skips it. The PATH entry is harmless when the dir is absent, so it stays unconditional.
#
# CACHE ORDERING: this block (Lean toolchain + the multi-GB Mathlib bake below) is
# the slowest step in the build and depends on nothing but install-lean.sh and
# proofs/'s dep-defining files -- not the dnf groups, the dotfiles, the other
# feature flags, src/ or tools/. It therefore sits FIRST, right after the
# never-changing `dnf upgrade` layer, so no edit or flag change elsewhere in this
# file rebuilds it. The toolchain installed is the one proofs/lean-toolchain pins,
# so `lake` never fetches a second one.
COPY entrypoint/install-lean.sh /usr/local/bin/
COPY proofs/lean-toolchain /opt/gacalc-proofs/
RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    if [ "$USE_LEAN" = "1" ]; then \
      LEAN_TOOLCHAIN="$(cat /opt/gacalc-proofs/lean-toolchain)" \
        /usr/local/bin/install-lean.sh ; \
    fi
ENV PATH="/root/.elan/bin:${PATH}"

# Bake Mathlib into the image (a committed layer OUTSIDE the bind-mounted repo) so
# `make lean` runs OFFLINE -- the "deps fetched at build, offline thereafter" rule.
# Only proofs/'s dep-defining files are staged here (NOT the .lean sources), so
# editing a proof doesn't rebust this layer -- and, being first (see the CACHE
# ORDERING note above), nothing else in the build does either. `lake exe cache get`
# clones the pinned Mathlib and downloads its prebuilt oleans into
# /opt/gacalc-proofs/.lake; proofs/check.sh copies that into the (mounted, gitignored)
# proofs/.lake at runtime -- the bind-mount would otherwise shadow a baked
# proofs/.lake. Gated on USE_LEAN (adds several GB, so only Lean images pay it). git
# (needed to clone Mathlib) is installed by install-lean.sh above.
COPY proofs/lakefile.toml proofs/lake-manifest.json /opt/gacalc-proofs/
RUN if [ "$USE_LEAN" = "1" ]; then \
      cd /opt/gacalc-proofs && touch GacalcProofs.lean && lake exe cache get ; \
    fi

# USE_SPYDER and USE_EMACS gate optional dnf groups in the base layer below.
ARG USE_SPYDER=0
ARG USE_EMACS=0

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
    /usr/local/bin/01-install-base.sh && \
    if [ "$USE_EMACS" = "1" ]; then /usr/local/bin/05-install-emacs.sh ; fi && \
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
    fi && \
    echo "/usr/local/bin/jupyter.sh # on http://127.0.0.1:8888/lab" >> ~/.bash_history && \
    echo "emacs src/gacalc/gn.py tests/test_multivector.py &" >> ~/.bash_history && \
    echo "source ~/.extrabashrc" >> ~/.bashrc && \
    echo "from gacalc.gn import *" >> ~/.python_history  && \
    python3 -m venv --system-site-packages /venv/ && \
    export VIRTUAL_ENV_DISABLE_PROMPT=1 && \
    source /venv/bin/activate && \
    uv pip install --python $(which python) setuptools wheel numpy sympy

# USE_JUPYTER gates the pandoc + XeLaTeX toolchain nbconvert's notebook "Export to
# PDF" renders through (03-install-notebook-tex.sh); BUILD_DOCS gates the Sphinx
# book toolchain. `make test` needs neither.
ARG USE_JUPYTER=0
ARG BUILD_DOCS=0

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

# USE_EPIX bakes the maintainer's ePiX mirror (C++ figure library + the epix/elaps
# drivers) for the book's LaTeX-native figures; EPIX_COMMIT is the ONE place its pin
# lives (tasks/archive/2026/10/07/epix-plot-integration.md). `make test` needs neither.
ARG USE_EPIX=0
ARG EPIX_COMMIT=275adefe5ced0abdba30a5efd443955c8370fb48

# ePiX (github.com/billsix/epix-mirror), pinned to EPIX_COMMIT, built from source with
# Meson into /usr/local -- the `epix`/`elaps`/`flix`/`laps` drivers + libepix for the
# book's LaTeX-native figures (decision 2026-10-06: epix COEXISTS with the matplotlib
# plotting in nbplotutils.py; it is the book's figure source, not the notebooks').
# Two host-runnable scripts: 06-install-epix.sh (dnf: git, meson/g++, ghostscript,
# ImageMagick, the TeX set epix's own render script names) then install-epix.sh (shallow
# git fetch of the pinned commit, meson install). Gated on USE_EPIX; placed before
# COPY src so a code edit never rebuilds it. The fetch is
# the only network use and happens at build time; the installed tools run offline.
COPY entrypoint/06-install-epix.sh entrypoint/install-epix.sh /usr/local/bin/
RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    if [ "$USE_EPIX" = "1" ]; then \
      /usr/local/bin/06-install-epix.sh && \
      EPIX_COMMIT="$EPIX_COMMIT" /usr/local/bin/install-epix.sh ; \
    fi

# OpenGL system libraries for gacalc.gl; always installed (no flag), since `make test`
# imports gacalc.gl. See entrypoint/07-install-gl.sh.
COPY entrypoint/07-install-gl.sh /usr/local/bin/
RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    /usr/local/bin/07-install-gl.sh

# USE_TEX_LABELS builds texExpToPng (github.com/billsix/tex-expression-to-png), pinned to
# TEXEXP_COMMIT (the commit modelviewprojection pins), which gacalc.gl.labels runs to
# draw the graphing calculators' TeX labels. Without it the graphers run unlabelled.
# 08-install-tex-labels.sh installs the build tools and TeX set; install-texexp.sh
# fetches, builds and checks it. The fetch is the only network use, at build time.
ARG USE_TEX_LABELS=0
ARG TEXEXP_COMMIT=67da442daf12eff07d5d8e6d57258be01492e3d0
COPY entrypoint/08-install-tex-labels.sh entrypoint/install-texexp.sh /usr/local/bin/
RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    if [ "$USE_TEX_LABELS" = "1" ]; then \
      /usr/local/bin/08-install-tex-labels.sh && \
      TEXEXP_COMMIT="$TEXEXP_COMMIT" /usr/local/bin/install-texexp.sh ; \
    fi

# --- Dependencies (the slow layer) -- from pyproject, needs ONLY pyproject.toml ---
# Install the project's runtime deps + the dev/notebooks/jupyter/gl extras straight from
# pyproject's own [project.(optional-)dependencies] -- the single source of truth (no
# requirements.txt, no hardcoded list). `-r pyproject.toml` installs the DEPENDENCIES,
# NOT the gacalc package, so this layer neither builds gacalc nor needs src/ or tools/,
# and is placed BEFORE `COPY src`/`COPY tools` so a code edit never rebusts it. It also
# sits after every slow source-independent layer (dnf/TeX + the Lean/Mathlib bake
# above). The uv CACHE MOUNT only speeds a rebuild (it is discarded, not in the image);
# the deps still land in the committed /venv, so an exported image stays self-contained.
#
# Every version is pinned by constraints.txt (regenerated by `make update-pins`), so two
# builds months apart install the same packages; pyproject.toml itself stays loose for
# the library's consumers. The earlier, slower layers install their few pip packages
# (setuptools/wheel/numpy/sympy, the Sphinx set, ePiX's nanobind) unpinned so a pin bump doesn't rebuild
# them; this layer re-installs those same packages under the constraints, so the final
# /venv matches constraints.txt exactly.
COPY pyproject.toml setup.py README.md constraints.txt /gacalc/
RUN --mount=type=cache,target=/root/.cache/uv \
    export VIRTUAL_ENV_DISABLE_PROMPT=1 && source /venv/bin/activate && \
    cd /gacalc && \
    uv pip install --python $(which python) -c constraints.txt -r pyproject.toml \
        --extra dev --extra notebooks --extra jupyter --extra gl setuptools wheel && \
    if [ "$USE_EPIX" = "1" ]; then \
      uv pip install --python $(which python) -c constraints.txt nanobind ; \
    fi && \
    if [ "$BUILD_DOCS" = "1" ]; then \
      uv pip install --python $(which python) -c constraints.txt \
        sphinx furo nbsphinx myst-nb ; \
    fi && \
    jupytext-config set-default-viewer python && \
    jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

# --- The gacalc package itself (the cheap layer) -- needs src/ + tools/ ---
# Build + install gacalc. The install runs setup.py's build_py hook, which execs
# tools/gen_specialized.py to generate g1/g2/g3.py when they are absent -- so tools/
# must be present HERE (this is the only step that needs it; the dep layer above does
# not). --no-deps: the deps are already installed above; the build prereqs
# (setuptools/wheel/numpy/sympy, installed earlier) satisfy --no-build-isolation. A
# src/ or tools/ edit now rebusts only this small layer, never the deps. At runtime
# `make shell`'s bind mount overlays /gacalc with the live host tree and re-installs
# editable (regenerating the algebras), so this copy is used only for the build -- and
# for a non-mounted/pulled image, which then has a working `import gacalc` standalone.
COPY src   /gacalc/src
COPY tools /gacalc/tools
RUN --mount=type=cache,target=/root/.cache/uv \
    export VIRTUAL_ENV_DISABLE_PROMPT=1 && source /venv/bin/activate && \
    cd /gacalc && uv pip install --python $(which python) --no-deps --no-build-isolation .

# The entrypoint is baked so a pulled or non-mounted image starts on its own; the
# Makefile also bind-mounts it, so an edit takes effect without a rebuild.
COPY entrypoint/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
