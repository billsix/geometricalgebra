#!/usr/bin/env python3
"""Derive a from-scratch Lean geometric-algebra's product / wedge / reverse formulas from gacalc's
`Gn` reference (the oracle), for verbatim transcription into a Lean `G<n>` module (e.g.
`proofs/GacalcProofs/G3.lean`).

Runs `Gn` on two fully-symbolic *n*-dimensional multivectors (one sympy symbol per basis blade) and
prints each output coefficient of the geometric product ``A * B``, the wedge ``A ^ B``, and the
reverse ``A~``, as an expanded formula. This is the mechanical "before" (per the repo's
codegen / instrumentation conventions — derive the target mechanically, never hand-transcribe), so the
Lean product is **correct-by-construction against gacalc** rather than hand-derived.

Parallels ``tools/gen_specialized.py`` (which generates the *Python* specialized classes ``G``); this
emits the formulas for their *Lean* twins in ``proofs/GacalcProofs/``. The coefficient/field names
match the Lean struct fields: ``s`` for the scalar, ``12`` for e₁e₂, etc. (single-digit indices, so
n ≤ 9).

Run in the container (needs gacalc importable):

    python tools/derive_lean_algebra.py [N]        # N = dimension, default 3

or, from the host via the project's container:

    make shell-exec CMD='python tools/derive_lean_algebra.py 3'
"""

import itertools
import sys

import sympy

from gacalc.gn import Gn


def blades(n: int) -> list[tuple[int, ...]]:
    """All canonical basis blades of 𝒢ₙ, grade-ascending then lexicographic — matching gacalc's
    canonical blade keys (sorted ascending index tuples)."""
    out: list[tuple[int, ...]] = []
    for grade in range(n + 1):
        out.extend(itertools.combinations(range(1, n + 1), grade))
    return out


def blade_name(bl: tuple[int, ...], prefix: str) -> str:
    """Field-name for a blade: () -> '<prefix>s', (1,2) -> '<prefix>12', etc."""
    suffix: str = "s" if bl == () else "".join(str(i) for i in bl)
    return prefix + suffix


def dump(title: str, value: Gn, prefix: str, all_blades: list[tuple[int, ...]]) -> None:
    """Print each coefficient of `value` as `<prefix><blade> = <expanded formula>`."""
    coefs: dict[tuple[int, ...], object] = value.to_blade_dict()
    print(f"\n=== {title} ===")
    bl: tuple[int, ...]
    for bl in all_blades:
        coef: object = sympy.expand(coefs.get(bl, sympy.Integer(0)))
        print(f"{blade_name(bl, prefix)} = {coef}")


def main() -> None:
    n: int = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    all_blades: list[tuple[int, ...]] = blades(n)
    a: dict[tuple[int, ...], sympy.Symbol] = {
        bl: sympy.Symbol(blade_name(bl, "a")) for bl in all_blades
    }
    b: dict[tuple[int, ...], sympy.Symbol] = {
        bl: sympy.Symbol(blade_name(bl, "b")) for bl in all_blades
    }
    A: Gn = Gn.from_blade_dict(a)
    B: Gn = Gn.from_blade_dict(b)
    dump(f"geometric product  A * B  (𝒢{n})", A * B, "c", all_blades)
    dump("wedge  A ^ B", A.outer_product(B), "w", all_blades)
    dump("reverse  A~ (grade sign)", A.reverse(), "r", all_blades)


if __name__ == "__main__":
    main()
