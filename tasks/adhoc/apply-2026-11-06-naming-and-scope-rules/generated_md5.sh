#!/bin/bash
# Regenerate g1-g3 in the container and print their checksums (compare before and after).
set -e
source /venv/bin/activate
cd /gacalc
python tools/gen_specialized.py > /dev/null
md5sum src/gacalc/g1.py src/gacalc/g2.py src/gacalc/g3.py
