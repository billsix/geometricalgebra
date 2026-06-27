#!/usr/bin/env python
# Copyright (c) 2025-2026 William Emerison Six
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Benchmark the general Gn representation against the specialized G1/G2/G3.

python tools/bench.py
"""

from __future__ import annotations

import os
import sys
import time
from collections.abc import Callable
from itertools import chain, combinations

import sympy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gacalc.base import MultiVectorBase  # noqa: E402
from gacalc.g1 import G1  # noqa: E402
from gacalc.g2 import G2, Vector2  # noqa: E402
from gacalc.g3 import G3, Vector3  # noqa: E402
from gacalc.gn import Gn  # noqa: E402

SPECIALIZED = {1: G1, 2: G2, 3: G3}


def blades(n: int) -> list[tuple[int, ...]]:
    idx = range(1, n + 1)
    return list(chain.from_iterable(combinations(idx, r) for r in range(n + 1)))


def num_full(n: int, base: int) -> Gn:
    return Gn.from_blade_dict({b: base + i + 1 for i, b in enumerate(blades(n))})


def to(cls: type[MultiVectorBase], g: Gn) -> MultiVectorBase:
    return cls.from_blade_dict(g.to_blade_dict())


def time_ms(fn: Callable[[], object], reps: int) -> float:
    fn()  # warm up
    t0 = time.perf_counter()
    for _ in range(reps):
        fn()
    return (time.perf_counter() - t0) / reps * 1000.0


def report(label: str, gn_ms: float, sp_ms: float) -> None:
    speedup = gn_ms / sp_ms if sp_ms else float("inf")
    sys.stdout.write(f"{label:32s} {gn_ms:11.3f} {sp_ms:11.3f} {speedup:10.1f}x\n")


def main() -> None:
    sys.stdout.write(
        f"{'operation':32s} {'Gn (ms)':>11} {'spec (ms)':>11} {'speedup':>11}\n"
    )
    sys.stdout.write("-" * 67 + "\n")

    for n in (1, 2, 3):
        cls = SPECIALIZED[n]
        a, b = num_full(n, 0), num_full(n, 10)
        ga, gb = to(cls, a), to(cls, b)

        # numeric full geometric product
        report(
            f"G{n} numeric full product",
            time_ms(lambda a=a, b=b: a * b, 200),
            time_ms(lambda ga=ga, gb=gb: ga * gb, 5000),
        )
        # now-specialized derived ops
        report(
            f"G{n} reverse",
            time_ms(lambda a=a: a.reverse(), 500),
            time_ms(lambda ga=ga: ga.reverse(), 5000),
        )
        report(
            f"G{n} numeric inner_product",
            time_ms(lambda a=a, b=b: a.inner_product(b), 200),
            time_ms(lambda ga=ga, gb=gb: ga.inner_product(gb), 5000),
        )
        report(
            f"G{n} add",
            time_ms(lambda a=a, b=b: a + b, 500),
            time_ms(lambda ga=ga, gb=gb: ga + gb, 5000),
        )

    # symbolic full product -- the headline case
    for n in (1, 2, 3):
        cls = SPECIALIZED[n]
        sa = Gn.symbolic_multivector(n, "a")
        sb = Gn.symbolic_multivector(n, "b")
        gsa, gsb = to(cls, sa), to(cls, sb)
        gn_reps = 1 if n == 3 else 5
        report(
            f"G{n} symbolic full product",
            time_ms(lambda sa=sa, sb=sb: sa * sb, gn_reps),
            time_ms(lambda gsa=gsa, gsb=gsb: gsa * gsb, 50),
        )

    # graded subtypes: a typed Vector*Vector computes only the needed components
    # (scalar + bivector) -- vs the full G_n product and the general Gn.
    sys.stdout.write("\n")
    sys.stdout.write("graded subtype: vector * vector (-> rotor)\n")
    sys.stdout.write("-" * 67 + "\n")
    for n, vector_cls in ((2, Vector2), (3, Vector3)):
        gva = Gn.from_blade_dict({(i,): i for i in range(1, n + 1)})
        gvb = Gn.from_blade_dict({(i,): i + 1 for i in range(1, n + 1)})
        va, vb = to(vector_cls, gva), to(vector_cls, gvb)
        fa, fb = to(SPECIALIZED[n], gva), to(SPECIALIZED[n], gvb)
        t_typed = time_ms(lambda va=va, vb=vb: va * vb, 5000)
        t_full = time_ms(lambda fa=fa, fb=fb: fa * fb, 5000)
        t_gn = time_ms(lambda a=gva, b=gvb: a * b, 200)
        sys.stdout.write(
            f"G{n} numeric : Vector {t_typed:8.4f} ms   full G{n} {t_full:8.4f} ms"
            f"   Gn {t_gn:8.3f} ms  "
            f"(typed {t_full / t_typed:.1f}x vs full, {t_gn / t_typed:.0f}x vs Gn)\n"
        )
        sa, sb = (
            to(
                vector_cls,
                Gn.from_blade_dict(
                    {(i,): sympy.Symbol(f"a{i}") for i in range(1, n + 1)}
                ),
            ),
            to(
                vector_cls,
                Gn.from_blade_dict(
                    {(i,): sympy.Symbol(f"b{i}") for i in range(1, n + 1)}
                ),
            ),
        )
        fsa = to(SPECIALIZED[n], widen_sym(sa))
        fsb = to(SPECIALIZED[n], widen_sym(sb))
        t_typed_s = time_ms(lambda sa=sa, sb=sb: sa * sb, 2000)
        t_full_s = time_ms(lambda fsa=fsa, fsb=fsb: fsa * fsb, 2000)
        sys.stdout.write(
            f"G{n} symbolic: Vector {t_typed_s:8.4f} ms   full G{n} {t_full_s:8.4f} ms"
            f"   (typed {t_full_s / t_typed_s:.1f}x vs full)\n"
        )


def widen_sym(x: MultiVectorBase) -> Gn:
    return Gn.from_blade_dict(x.to_blade_dict())


if __name__ == "__main__":
    main()
