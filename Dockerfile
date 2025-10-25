FROM registry.fedoraproject.org/fedora:43

RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    echo "keepcache=True" >> /etc/dnf/dnf.conf && \
    dnf upgrade -y && \
    dnf install -y \
                   emacs \
                   npm \
                   python3 \
                   python3-pip \
                   python3-sympy \
                   python3-pytest \
                   ruff \
                   tmux && \
     # clean out dnf \
     dnf clean all && \
     # install pyright for lsp \
     npm install -g pyright


COPY entrypoint/dotfiles/ /root/

RUN emacs --batch --load /root/.emacs.d/install-melpa-packages.el && \
    echo "alias ls='ls --color=auto'" >> ~/.bashrc

ENTRYPOINT ["/entrypoint.sh"]
