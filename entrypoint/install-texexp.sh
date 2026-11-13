#!/usr/bin/env bash
#
# install-texexp.sh -- fetch texExpToPng (github.com/billsix/tex-expression-to-png) at
# ONE pinned commit and install it into /usr/local with Meson, so gacalc.gl.labels
# finds it on PATH and the graphing calculators draw their TeX labels. Run after
# 08-install-tex-labels.sh (the build + runtime packages). Host-runnable: on a bare
# Fedora host, run both as root.
#
# The commit comes from the environment: the Dockerfile passes its TEXEXP_COMMIT ARG
# explicitly (`RUN TEXEXP_COMMIT=$TEXEXP_COMMIT install-texexp.sh`), so the pin lives in
# one place and a bare-host run must name it too. The fetch is a shallow fetch of
# exactly that commit, at image-build time; the installed tool runs offline.
set -euo pipefail

: "${TEXEXP_COMMIT:?install-texexp.sh: set TEXEXP_COMMIT to the tex-expression-to-png commit SHA to install}"
TEXEXP_URL="${TEXEXP_URL:-https://github.com/billsix/tex-expression-to-png.git}"
SRC=$(mktemp -d)

git init -q "$SRC"
git -C "$SRC" remote add origin "$TEXEXP_URL"
git -C "$SRC" fetch -q --depth 1 origin "$TEXEXP_COMMIT"
git -C "$SRC" checkout -q --detach FETCH_HEAD
echo "tex-expression-to-png at $(git -C "$SRC" rev-parse HEAD)"

meson setup "$SRC/build" "$SRC" --prefix=/usr/local
meson compile -C "$SRC/build"
meson install -C "$SRC/build"
rm -rf "$SRC"

# Render one label the way gacalc.gl.labels does, so a broken TeX set fails the build
# here rather than leaving the graphers silently without labels.
OUT=$(mktemp -d)
(cd "$OUT" && texExpToPng --exp '$\sin(x)$' --size 600 --fg 'rgb 1 1 1' \
    --bg Transparent --output "$OUT/check.png" >/dev/null)
test -s "$OUT/check.png"
rm -rf "$OUT"
echo "texExpToPng OK: $(command -v texExpToPng)"
