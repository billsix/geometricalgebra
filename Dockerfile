FROM registry.fedoraproject.org/fedora:44

ARG USE_SPYDER=0
ARG USE_EMACS=0

RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    echo "keepcache=True" >> /etc/dnf/dnf.conf && \
    dnf upgrade -y

COPY entrypoint/dotfiles/ /root/

RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
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
                   which ;  \
    dnf install -y \
                   pinentry; \
    if [ "$USE_SPYDER" = "1" ]; then \
      dnf install -y   \
                   mesa-dri-drivers  \
                   mesa-libGLU-devel && \
      dnf install -y python3-spyder && \
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
    dnf install -y libatomic && uv pip install --python $(which python) pyright

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
    cd /gacalc && uv pip install --python $(which python) --no-build-isolation ".[dev,notebooks,jupyter]"


ENTRYPOINT ["/entrypoint.sh"]
