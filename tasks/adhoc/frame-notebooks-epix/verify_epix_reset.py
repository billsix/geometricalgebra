#!/usr/bin/env python3
"""Check, in gacalc's image, that ePiX resets its global state per figure.

Run from the repo root inside the container:
    python tasks/adhoc/frame-notebooks-epix/verify_epix_reset.py

1. The red/dashed repro: a plain figure drawn after a red, dashed one equals the
   same plain figure drawn in a fresh process (palette lines included).
2. A 3D figure drawn after a 2D one that moved the camera equals the 3D figure
   drawn in a fresh process (the camera is reset).
Exits 1 if either differs.
"""

from __future__ import annotations

import subprocess
import sys

import epix
from epix import Point


def plain() -> str:
    fig: object
    with epix.figure(
        lower_left=Point(x=-1, y=-1), upper_right=Point(x=1, y=1), size="2x2in"
    ) as fig:
        epix.line(tail=Point(x=-1, y=0), head=Point(x=1, y=0))
    return fig.eepic


def red_dashed() -> str:
    fig: object
    with epix.figure(
        lower_left=Point(x=-1, y=-1), upper_right=Point(x=1, y=1), size="2x2in"
    ) as fig:
        epix.pen(color=epix.rgb(r=1, g=0, b=0), width=3)
        epix.dashed()
        epix.camera.at(Point(x=1, y=1, z=20))
        epix.line(tail=Point(x=-1, y=0), head=Point(x=1, y=0))
    return fig.eepic


def three_d() -> str:
    fig: object
    with epix.figure(
        lower_left=Point(x=-2, y=-2), upper_right=Point(x=2, y=2), size="2x2in"
    ) as fig:
        epix.line(tail=Point(x=0, y=0, z=0), head=Point(x=1, y=1, z=1))
    return fig.eepic


def strip(text: str) -> str:
    return "\n".join(
        line
        for line in text.splitlines()
        if "Generated" not in line and "Automatically" not in line
    )


CASES: dict[str, object] = {"plain": plain, "three_d": three_d}

if __name__ == "__main__":
    if len(sys.argv) == 2:  # the fresh-process half: print one figure, alone
        sys.stdout.write(strip(CASES[sys.argv[1]]()))
        sys.exit(0)
    status: int = 0
    name: str
    for name in CASES:
        red_dashed()  # leave pen, dashes, palette and camera behind
        together: str = strip(CASES[name]())
        alone: str = subprocess.run(
            [sys.executable, __file__, name], check=True, capture_output=True, text=True
        ).stdout
        ok: bool = together == alone
        status |= 0 if ok else 1
        print(f"{name} after red_dashed: {'PASS' if ok else 'FAIL'}")
    sys.exit(status)
