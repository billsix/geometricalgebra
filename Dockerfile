FROM docker.io/debian:trixie

ARG USE_JUPYTER=1
ARG USE_SPYDER=1


# Install necessary packages for OpenGL
RUN apt update -y
RUN apt install -y \
    emacs \
    fonts-mathjax \
    g++ \
    gcc \
    git \
    jupyter \
    jupyterlab \
    libglfw3 \
    mesa-va-drivers \
    mesa-vdpau-drivers \
    npm \
    python3 \
    python3-dev \
    python3-jupyter-server-mathjax \
    python3-jupytext \
    python3-opengl \
    python3-pip \
    python3-pyglfw \
    python3-pytest \
    python3-setuptools \
    python3-sympy \
    python3-venv \
    python3-wheel \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-science  \
    tmux \
    which


RUN echo FOO && python3 -m venv /venv --system-site-packages  && \
    . /venv/bin/activate && \
    python -m pip install --upgrade pip setuptools && \
       python3 -m pip install ty --root-user-action=ignore  # ty \
       cd ~/ && # imgui \
       git clone https://github.com/billsix/pyimgui.git && \
       cd pyimgui && \
       git submodule init && git submodule update && \
       python3 -m pip install . --root-user-action=ignore


RUN  # install pyright for lsp \
     npm install -g pyright


RUN . /venv/bin/activate && \
    python -m pip install ty

COPY entrypoint/dotfiles/ /root/

RUN emacs --batch --load /root/.emacs.d/install-melpa-packages.el && \
    echo "alias ls='ls --color=auto'" >> ~/.bashrc

RUN echo "/usr/local/bin/jupyter.sh" >> ~/.bash_history && \
    echo "emacs src/geometricalgebra/multivector.py tests/test_multivector.py &" >> ~/.bash_history

RUN apt install -y emacs-pgtk

ENTRYPOINT ["/entrypoint.sh"]
