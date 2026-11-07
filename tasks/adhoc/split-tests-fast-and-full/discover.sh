#!/bin/bash
# Per-test durations of the whole suite, run in the gacalc image (the same
# invocation `make test` uses), every test that takes 1 s or more.  Run from the
# repo root; writes data/durations.txt next to this script.
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(git -C "$here" rev-parse --show-toplevel)"
podman run ${PODMAN_RUN_FLAGS:---cgroups=disabled} --rm -v "$root":/gacalc/:Z \
    --entrypoint /bin/bash gacalc -c \
    'source /venv/bin/activate; cd /gacalc; python tools/gen_specialized.py >/dev/null;
     python -m pytest -q -p no:cacheprovider --durations=0 --durations-min=1.0' \
    > "$here/data/durations.txt" 2>&1
echo "rc=$?" >> "$here/data/durations.txt"
