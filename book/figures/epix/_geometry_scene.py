"""Shared points for the geometry-from-vectors figures (``geom_*``).

The points of `book/docs/geometry-from-vectors.rst` and of the angle figure in
`book/docs/product-from-projection.rst`, each a position vector, so every figure of a
pair agrees on one geometry. Generic primitives come from
:mod:`gacalc.epixscene.scene2d`. CC0, like the other figure helpers.
"""

from __future__ import annotations

from gacalc.epixscene.scene2d import Point

# The segment and line figures: two points a and b.
SEG_A: Point = Point(x=0.4, y=1.2)
SEG_B: Point = Point(x=2.0, y=0.4)
SEG_LOWER_LEFT: Point = Point(x=-0.45, y=-0.4)
SEG_UPPER_RIGHT: Point = Point(x=2.6, y=1.75)
LINE_LOWER_LEFT: Point = Point(x=-0.95, y=-0.55)
LINE_UPPER_RIGHT: Point = Point(x=3.3, y=1.95)


def on_segment(start: Point, finish: Point, t: float) -> Point:
    """The point ``start + t * (finish - start)``."""
    return start + t * (finish - start)


# The triangle (and its midsegment): three corners a, b, c.
TRI_A: Point = Point(x=0.3, y=0.3)
TRI_B: Point = Point(x=2.4, y=0.5)
TRI_C: Point = Point(x=1.2, y=1.8)
TRI_LOWER_LEFT: Point = Point(x=-0.35, y=-0.35)
TRI_UPPER_RIGHT: Point = Point(x=2.85, y=2.1)

# The parallelogram a, b, c, d in order, with c chosen so that b - a = c - d.
PAR_A: Point = Point(x=0.3, y=0.3)
PAR_B: Point = Point(x=2.0, y=0.5)
PAR_D: Point = Point(x=0.8, y=1.5)
PAR_C: Point = PAR_B + PAR_D - PAR_A
PAR_LOWER_LEFT: Point = Point(x=-0.35, y=-0.35)
PAR_UPPER_RIGHT: Point = Point(x=2.95, y=2.0)

# The angle at the vertex b between the rays toward a and toward c.
ANG_A: Point = Point(x=2.4, y=0.6)
ANG_B: Point = Point(x=0.5, y=0.3)
ANG_C: Point = Point(x=1.3, y=1.8)
ANG_LOWER_LEFT: Point = Point(x=-0.35, y=-0.35)
ANG_UPPER_RIGHT: Point = Point(x=2.85, y=2.1)
