"""Compute the `linear_combination` cofactors for `rotorSandwich_planeRotor` (PlaneRotation3D.lean).

The Lean leaf proves, per vector component, a polynomial identity modulo two relations,
``cos²(θ/2) + sin²(θ/2) = 1`` and ``|i|² = p² + q² + r² = 1``. ``linear_combination`` needs the
cofactors ``Q₁``, ``Q₂`` with ``LHS − RHS = Q₁·(c² + s² − 1) + Q₂·(p² + q² + r² − 1)``; this script
finds them with sympy's multivariate division (``reduced``) over gacalc's own 𝒢₃ product — the same
product Lean's ``G3.mul`` was transcribed from — and prints them in Lean syntax (``^`` for powers).
A zero remainder is the proof that the identity holds modulo the ideal.

Run from the repo root inside the project container (needs gacalc + sympy)::

    python tasks/adhoc/lean-rotor-3d-angle-theorem/cofactors.py

Variables: ``p, q, r`` = ``i.c12, i.c13, i.c23``; ``x, y, z`` = ``v.c1, v.c2, v.c3``;
``c, s`` = ``cos (θ/2), sin (θ/2)``.
"""

import sympy

from gacalc.g3 import Bivector, Vector

p, q, r, x, y, z, c, s = sympy.symbols("p q r x y z c s", real=True)
i = p * Bivector.e_12 + q * Bivector.e_13 + r * Bivector.e_23
v = x * Vector.e_1 + y * Vector.e_2 + z * Vector.e_3
rotor = c + (-s) * i  # planeRotor θ i, with c = cos(θ/2), s = sin(θ/2)
lhs = rotor * v * rotor.reverse()  # rotorSandwich
i_inverse_unit = -i  # inverse i = reverse i / |i|² = −i for a unit bivector
turn = v < i  # inner_vb v i: the left contraction v ⌋ i (v∥ turned +90° in the plane)
proj = turn * i_inverse_unit  # project_onto i v
rej = (v ^ i) * i_inverse_unit  # reject i v
rhs = rej + (c**2 - s**2) * proj + (2 * s * c) * turn  # cos θ, sin θ by double angle
relations = [c**2 + s**2 - 1, p**2 + q**2 + r**2 - 1]
diff = (lhs - rhs).to_blade_dict()
for blade in sorted(diff, key=lambda b: (len(b), b)):
    poly = sympy.expand(sympy.sympify(diff[blade]))
    if poly == 0:
        print(blade, "identically 0 (ring)")
        continue
    quotients, remainder = sympy.reduced(poly, relations, c, s, p, q, r, x, y, z)
    assert remainder == 0, (blade, remainder)
    print(blade)
    print("  * hcs :", str(sympy.factor(quotients[0])).replace("**", "^"))
    print("  * hpqr:", str(sympy.factor(quotients[1])).replace("**", "^"))
