#!/usr/bin/env bash
# Start Spyder on the repo. Spyder is in the image only when it was built with
# USE_SPYDER=1 (entrypoint/02-install-spyder.sh); say so instead of failing with
# a bare "command not found". Run by `make spyder`, or by hand inside `make shell`.
export VIRTUAL_ENV_DISABLE_PROMPT=1
source /venv/bin/activate
command -v spyder >/dev/null || {
    echo "spyder is not installed in this image; rebuild with: make image USE_SPYDER=1" >&2
    exit 2
}
exec spyder -p /gacalc/
