FROM registry.fedoraproject.org/fedora:44

ARG USE_SPYDER=0
ARG USE_EMACS=0

RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    echo "keepcache=True" >> /etc/dnf/dnf.conf && \
    dnf upgrade -y

COPY entrypoint/dotfiles/ /root/
COPY requirements.txt /requirements.txt

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
                   ty ;  \
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
    uv pip install --system setuptools && \
    dnf install -y libatomic && uv pip install --system pyright && \
    uv pip install --system -r /requirements.txt && \
    rm /requirements.txt

# Copy the build-relevant project files (not the whole tree: the 31M vendored
# Emacs elpa tree is already at /root, and .dockerignore is global so it can't be
# excluded for just this COPY). Placed after the slow dnf/MELPA/requirements
# layers so editing source doesn't re-run them. At runtime `make shell`'s bind
# mount overlays /gacalc with the live host tree, so this copy is only
# used for the build below.
COPY pyproject.toml setup.py requirements.txt README.md /gacalc/
COPY src   /gacalc/src
COPY tools /gacalc/tools

# Install the package + its "dev" extras (build, twine) from pyproject's own
# [project.optional-dependencies] -- the single source of truth, no hardcoded
# package list. Runtime deps are already installed above, so this mainly fetches
# the dev tools; --no-build-isolation reuses the system setuptools/wheel/numpy/
# sympy, and the setup.py build_py hook generates the algebras if missing.
RUN cd /gacalc && uv pip install --system --no-build-isolation ".[dev]"


ENTRYPOINT ["/entrypoint.sh"]
