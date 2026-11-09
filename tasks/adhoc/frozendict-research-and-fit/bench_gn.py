#!/usr/bin/env python3
"""Time the Gn operations whose cost a frozendict storage could change.

Run from the repo root, in a fresh process per variant (the working tree's
``src/gacalc/gn.py`` is whatever variant is applied)::

    PYTHONPATH=src python tasks/adhoc/frozendict-research-and-fit/bench_gn.py LABEL

Prints one CSV line per operation: label, operation, best-of-5 microseconds per
call.  Numeric operations isolate the container overhead (``sympy.simplify`` on
an integer is cheap); the symbolic product shows whether that overhead matters
next to the simplify that dominates real Gn work.
"""

import itertools
import sys
import timeit
from collections.abc import Callable

from gacalc.gn import Gn

LABEL: str = sys.argv[1] if len(sys.argv) > 1 else "run"


def full(n: int, base: int) -> Gn:
    """A dense numeric multivector of dimension n (every blade nonzero)."""
    blades: list[tuple[int, ...]] = [
        b for k in range(n + 1) for b in itertools.combinations(range(1, n + 1), k)
    ]
    return Gn.from_blade_dict({b: base + i + 1 for i, b in enumerate(blades)})


a3: Gn = full(3, 0)
b3: Gn = full(3, 10)
d8: dict[tuple[int, ...], int] = dict(a3.to_blade_dict())
sa: Gn = Gn.symbolic_multivector(3, "a")
sb: Gn = Gn.symbolic_multivector(3, "b")

CASES: list[tuple[str, Callable[[], object], int]] = [
    ("to_blade_dict (8 blades)", lambda: a3.to_blade_dict(), 200000),
    ("from_blade_dict numeric (8 blades)", lambda: Gn.from_blade_dict(d8), 2000),
    ("add numeric 3D", lambda: a3 + b3, 2000),
    ("geometric product numeric 3D", lambda: a3 * b3, 200),
    ("geometric product symbolic 3D", lambda: sa * sb, 3),
]

name: str
fn: Callable[[], object]
number: int
for name, fn, number in CASES:
    best: float = min(timeit.repeat(fn, number=number, repeat=5)) / number
    print(f"{LABEL},{name},{best * 1e6:.2f}")  # noqa: T201 -- the report is the output
