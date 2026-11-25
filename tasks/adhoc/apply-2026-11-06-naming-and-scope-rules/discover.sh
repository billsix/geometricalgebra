#!/bin/bash
# Survey for the 2026-11-06 naming and scope rules (rules 1-4); writes data/candidates.txt.
# The generated g1-g5 modules are gitignored and never listed here.
exec python3 "$(dirname "$0")/discover.py" src/gacalc/base.py src/gacalc/cayley src/gacalc/epixscene src/gacalc/frame.py src/gacalc/functions.py src/gacalc/gl src/gacalc/gn.py src/gacalc/measure.py src/gacalc/nbdisplay.py src/gacalc/nbplotutils.py src/gacalc/standardposition.py src/gacalc/transforms.py src/gacalc/vectorcalc.py tools tests notebooks book/figures/epix examples
