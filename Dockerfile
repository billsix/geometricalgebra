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
    emacs --batch --load /root/.emacs.d/install-melpa-packages.el && \
    echo "alias ls='ls --color=auto'" >> ~/.bashrc && \
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
    echo "emacs src/geometricalgebra/multivector.py tests/test_multivector.py &" >> ~/.bash_history && \
    uv pip install --system setuptools && \
    dnf install -y libatomic && uv pip install --system pyright && \
    uv pip install --system -r /requirements.txt && \
    rm /requirements.txt


ENTRYPOINT ["/entrypoint.sh"]
