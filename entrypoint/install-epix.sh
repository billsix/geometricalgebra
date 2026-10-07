#!/usr/bin/env bash
#
# install-epix.sh -- fetch the maintainer's ePiX mirror (github.com/billsix/epix-mirror)
# at ONE pinned commit and install it into /usr/local with Meson, so the gacalc image
# carries `epix`, `elaps`, `flix`, `laps`, libepix.a and its headers for the book's
# LaTeX-native figures. Run after 06-install-epix.sh (the build + runtime packages).
# Host-runnable: on a bare Fedora host, run both scripts as root.
#
# The commit comes from the environment -- the Dockerfile passes its EPIX_COMMIT ARG
# explicitly (`RUN EPIX_COMMIT=$EPIX_COMMIT install-epix.sh`), so the pin lives in one
# place (the Dockerfile) and a bare-host run must name it too. Pinning to a commit, not a
# branch, is what makes the image layer reproducible; bump the ARG to move it.
#
# The fetch is a shallow fetch of exactly that commit (GitHub serves reachable SHAs), so
# the layer holds one tree, not the history. The source stays at /opt/epix-src (small;
# its samples/ and python/ are the reference for writing figures); the Meson build dir is
# removed. This runs at IMAGE-BUILD time -- network is used here and never at run time,
# per the "deps fetched at build, offline thereafter" rule.
set -euo pipefail

: "${EPIX_COMMIT:?install-epix.sh: set EPIX_COMMIT to the epix-mirror commit SHA to install}"
EPIX_URL="${EPIX_URL:-https://github.com/billsix/epix-mirror.git}"
SRC="${EPIX_SRC:-/opt/epix-src}"

rm -rf "$SRC"
git init -q "$SRC"
git -C "$SRC" remote add origin "$EPIX_URL"
git -C "$SRC" fetch -q --depth 1 origin "$EPIX_COMMIT"
git -C "$SRC" checkout -q --detach FETCH_HEAD
echo "epix-mirror at $(git -C "$SRC" rev-parse HEAD)"

meson setup "$SRC/build" "$SRC" --prefix=/usr/local
meson install -C "$SRC/build"
rm -rf "$SRC/build" "$SRC/.git"

epix --version
