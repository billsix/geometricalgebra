#!/bin/bash
# Run probe.el in a headless Emacs inside the gacalc image, from the repo root.
# The repo is mounted read-only and the vendored elpa as an overlay (:O), so
# Emacs's byte-recompile writes nothing back to the host tree.
# Usage: tasks/adhoc/emacs-python-lsp-investigation/run_probe.sh [--network=none]
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(git -C "$here" rev-parse --show-toplevel)"
podman run --rm --cgroups=disabled "$@" \
    -v "$root":/gacalc:ro,z \
    -v "$root"/entrypoint/dotfiles/.emacs.d/elpa:/root/.emacs.d/elpa:O \
    -v "$here":/probe:ro,z \
    --entrypoint /bin/bash gacalc \
    -c 'source /venv/bin/activate; cd /gacalc; emacs --batch -l /probe/probe.el 2>&1' \
    | grep -E 'PROBE|LSP ::'
