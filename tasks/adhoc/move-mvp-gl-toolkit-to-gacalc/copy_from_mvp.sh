#!/usr/bin/env bash
# Copy modelviewprojection (mvp) source files into gacalc for the
# move-mvp-gl-toolkit-to-gacalc initiative (tasks/move-mvp-gl-toolkit-to-gacalc.md).
#
# Usage: copy_from_mvp.sh <mvp-repo-root> <mvp-relative-src>:<gacalc-relative-dst> ...
#
# For each pair it:
#   1. drops the source's leading comment block (mvp's licence header and any
#      header comments) and the blank line after it;
#   2. prepends gacalc's LGPL-2.1-only header, read from
#      tests/test_rotate_90_degrees.py (the file gacalc's CLAUDE.md names as
#      the header to copy);
#   3. rewrites the imports of modules that have already moved
#      (modelviewprojection.cayley -> gacalc.cayley,
#      modelviewprojection.matrix_stack -> gacalc.gl.matrix_stack,
#      modelviewprojection.mvpvisualization -> gacalc.gl).
#
# Anything else that refers to mvp (mathutils imports, docstrings) is left for
# a hand edit, and the script reports the remaining "modelviewprojection" lines.
# It overwrites the destination from the source every time, so rerunning it
# discards those hand edits: run it once per file.
set -u

gacalc_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
mvp_root=$1
shift

# The header is the leading comment block of the reference file.
header=$(awk '/^#/ { print; next } { exit }' \
    "$gacalc_root/tests/test_rotate_90_degrees.py")

status=0
for pair in "$@"; do
    src="$mvp_root/${pair%%:*}"
    dst="$gacalc_root/${pair#*:}"
    if [ ! -f "$src" ]; then
        echo "missing source: $src" >&2
        status=1
        continue
    fi
    mkdir -p "$(dirname "$dst")"
    {
        printf '%s\n\n' "$header"
        # Skip the leading '#' block, then one blank line if present.
        awk 'body { print; next }
             /^#/ { next }
             /^$/ && !skipped_blank { skipped_blank = 1; body = 1; next }
             { body = 1; print }' "$src"
    } | sed -e 's/modelviewprojection\.cayley/gacalc.cayley/g' \
            -e 's/import modelviewprojection\.matrix_stack/import gacalc.gl.matrix_stack/g' \
            -e 's/modelviewprojection\.matrix_stack/gacalc.gl.matrix_stack/g' \
            -e 's/from modelviewprojection\.mvpvisualization import/from gacalc.gl import/g' \
            -e 's/modelviewprojection\.mvpvisualization/gacalc.gl/g' \
        > "$dst"
    echo "copied ${pair%%:*} -> ${pair#*:}"
    grep -n "modelviewprojection" "$dst" | sed "s|^|  still mentions mvp: ${pair#*:}:|"
done
exit $status
