"""Ad-hoc proof/demo for the Odd_3 graded type (tasks/model-odd-graded-type.md).

Shows the three ``Bivector * Vector`` geometric cases resolving to ``Odd_3`` and
exercises the opt-in cast API (``to_vector`` / ``to_trivector``) plus value inspection.
The dual-of-wedge relationship is not needed here since e_12 is already axis-aligned:
``e_12 * e_1`` is in-plane (grade 1), ``e_12 * e_3`` is perpendicular (grade 3).

Superseded at archive time by ``tests/test_odd3.py`` + ``notebooks/displayodd3.py``;
kept meanwhile as the record of how the cast API was proven.

Run in the gacalc container from the repo root:
    make shell-exec SCRIPT=tasks/adhoc/model-odd-graded-type/verify.sh   # (full gate)
or, once gacalc is installed and g3.py generated, directly:
    python tasks/adhoc/model-odd-graded-type/inspect_odd3.py
"""

import gacalc.g3 as g3

B = g3.Bivector.e_12
in_plane = B * g3.Vector.e_1  # -e_2  (grade 1)
perp = B * g3.Vector.e_3  # e_123 (grade 3)
mixed = B * (g3.Vector.e_1 + g3.Vector.e_3)  # grades {1,3}


def show(label, f):
    try:
        r = f()
        print(f"  {label}: OK -> {type(r).__name__}  value={r}")
    except ValueError as e:
        print(f"  {label}: raised ValueError -> {e}")


print("has to_vector/to_trivector:",
      hasattr(g3.Odd_3, "to_vector"), hasattr(g3.Odd_3, "to_trivector"))
print("in-plane (grades", in_plane.grades(), "):")
show("to_vector", in_plane.to_vector)
show("to_trivector", in_plane.to_trivector)
print("perp (grades", perp.grades(), "):")
show("to_vector", perp.to_vector)
show("to_trivector", perp.to_trivector)
print("mixed (grades", mixed.grades(), "):")
show("to_vector", mixed.to_vector)
show("to_trivector", mixed.to_trivector)
v = in_plane.to_vector()
print("value query on narrowed Vector: x,y,z =", v.x, v.y, v.z)
t = perp.to_trivector()
print("value query on narrowed Trivector: coeff_e_123 =", t.coeff_e_123)
