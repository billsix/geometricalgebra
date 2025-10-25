FROM registry.fedoraproject.org/fedora:42

RUN dnf upgrade -y && \
    dnf install -y \
                   emacs \
                   npm \
                   python3 \
                   python3-sympy \
                   ruff \
                   tmux && \
     # clean out dnf \
     dnf clean all && \
     # install pyright for lsp \
     npm install -g pyright && \


COPY entrypoint/dotfiles/ /root/

RUN emacs --batch --load /root/.emacs.d/install-melpa-packages.el && \
    echo "alias ls='ls --color=auto'" >> ~/.bashrc



ENTRYPOINT ["/entrypoint.sh"]
