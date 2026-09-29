#!/usr/bin/env python3
"""Derive the 𝒢₃ geometric-product formula from gacalc's `Gn` reference (the oracle),
to transcribe verbatim into the from-scratch Lean `G3.mul`
(`proofs/GacalcProofs/G3.lean`).

Runs `Gn` on two fully-symbolic 3D multivectors `A`, `B` (a sympy symbol per basis blade)
and prints each output coefficient of `A * B` as an expanded formula. This is the
mechanical "before" (per the repo's codegen/instrumentation conventions) so the Lean
product is correct-by-construction rather than hand-derived. Also prints `reverse(A)` and
`A ∧ B` (wedge) and the dot for the same reason. Run in the container (needs gacalc):

    podman run --rm -v "$(pwd)":/gacalc:Z --entrypoint /bin/bash gacalc \\
      -c 'source /venv/bin/activate && cd /gacalc && \\
          python tasks/adhoc/build-g3-lean/derive_g3_product.py'
"""

import sympy
from gacalc.gn import Gn

BLADES: list[tuple[int, ...]] = [
    (),
    (1,),
    (2,),
    (3,),
    (1, 2),
    (1, 3),
    (2, 3),
    (1, 2, 3),
]


def blade_name(bl: tuple[int, ...], prefix: str) -> str:
    """Field-name for a blade: () -> '<prefix>s', (1,2) -> '<prefix>12', etc."""
    suffix: str = "s" if bl == () else "".join(str(i) for i in bl)
    return prefix + suffix


a: dict[tuple[int, ...], sympy.Symbol] = {
    bl: sympy.Symbol(blade_name(bl, "a")) for bl in BLADES
}
b: dict[tuple[int, ...], sympy.Symbol] = {
    bl: sympy.Symbol(blade_name(bl, "b")) for bl in BLADES
}
A: Gn = Gn.from_blade_dict(a)
B: Gn = Gn.from_blade_dict(b)

product: Gn = A * B
product_coefs: dict[tuple[int, ...], object] = product.to_blade_dict()
print("=== geometric product  A * B ===")
bl: tuple[int, ...]
for bl in BLADES:
    coef: object = sympy.expand(product_coefs.get(bl, sympy.Integer(0)))
    print(f"{blade_name(bl, 'c')} = {coef}")

wedge: Gn = A.outer_product(B)
wedge_coefs: dict[tuple[int, ...], object] = wedge.to_blade_dict()
print("\n=== wedge  A ^ B ===")
for bl in BLADES:
    wcoef: object = sympy.expand(wedge_coefs.get(bl, sympy.Integer(0)))
    print(f"{blade_name(bl, 'w')} = {wcoef}")

reverse: Gn = A.reverse()
reverse_coefs: dict[tuple[int, ...], object] = reverse.to_blade_dict()
print("\n=== reverse  A~ (grade sign) ===")
for bl in BLADES:
    rcoef: object = sympy.expand(reverse_coefs.get(bl, sympy.Integer(0)))
    print(f"{blade_name(bl, 'r')} = {rcoef}")
