#!/usr/bin/env bash
# Execute every notebook (or the ones named) into tasks/adhoc/cancellation-underbrace-everywhere/data/executed/
# inside the gacalc image, then report each show_difference line that is not a clean
# cancellation (scan_outputs.py). Run from the repo root on the host/sandbox.
status=0
root=$(git rev-parse --show-toplevel)
cd "$root" || exit 1
podman run ${PODMAN_RUN_FLAGS:---cgroups=disabled} --rm -v "$root":/gacalc:Z --entrypoint /bin/bash gacalc -c '
source /venv/bin/activate; cd /gacalc
python tools/gen_specialized.py >/dev/null
uv pip install --python "$(which python)" --no-deps --no-index --no-build-isolation -e . >/dev/null 2>&1
out=tasks/adhoc/cancellation-underbrace-everywhere/data/executed
mkdir -p "$out"
status=0
names=("$@")
[ ${#names[@]} -eq 0 ] && names=(notebooks/*.py)
for f in "${names[@]}"; do
  base=$(basename "${f%.py}")
  jupytext --to ipynb --execute -o "$out/$base.ipynb" "$f" >"$out/$base.log" 2>&1 || { echo "FAIL $f"; status=1; }
done
exit $status
' bash "$@" || status=1
python3 tasks/adhoc/cancellation-underbrace-everywhere/scan_outputs.py || status=1
exit $status
