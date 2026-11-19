#!/usr/bin/env bash
#
# install-epix-stubs.sh -- give an image built WITHOUT ePiX (USE_EPIX=0, e.g. the lean
# image CI uses) the types of the `epix` Python package, so ty and pyright can check
# gacalc.epixscene and the notebooks that draw ePiX figures. It fetches the package's
# typed sources from github.com/billsix/epix-mirror at the pinned commit -- the extension
# stub _epix.pyi and the pure-Python modules -- and installs them into the venv as a
# PEP 561 stub-only package, `epix-stubs`, with each module renamed to .pyi.
#
# A stub-only package is read by type checkers and never imported: `import epix` still
# fails in this image, which is what the root conftest.py relies on to skip
# gacalc.epixscene's collection. No compiler or TeX is needed; the four files are small.
# The commit comes from the environment, as for install-epix.sh -- the Dockerfile passes
# its EPIX_COMMIT ARG, so the types always match the ePiX a full image would build.
# Network is used here, at image-build time only.
set -euo pipefail

: "${EPIX_COMMIT:?install-epix-stubs.sh: set EPIX_COMMIT to the epix-mirror commit SHA}"
EPIX_RAW="${EPIX_RAW:-https://raw.githubusercontent.com/billsix/epix-mirror}"

export VIRTUAL_ENV_DISABLE_PROMPT=1
source /venv/bin/activate
site=$(python -c 'import sysconfig; print(sysconfig.get_path("purelib"))')
dest="$site/epix-stubs"
rm -rf "$dest"
mkdir -p "$dest"

for module in __init__ figure render; do
    curl -fsSL -o "$dest/$module.pyi" "$EPIX_RAW/$EPIX_COMMIT/python/epix/$module.py"
done
curl -fsSL -o "$dest/_epix.pyi" "$EPIX_RAW/$EPIX_COMMIT/python/epix/_epix.pyi"
echo "epix type stubs from epix-mirror $EPIX_COMMIT in $dest:"
ls "$dest"
