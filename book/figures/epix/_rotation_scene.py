"""Shared scene for the proof-rotate figures (``rotate1`` … ``rotate8``).

One picture, built up step by step across the eight proof figures: the unit disc
with axes, the direction of :math:`\\vec{a}` at angle β, its perpendicular at β + π/2,
the rotation angle θ, the right triangle with legs cos θ and sin θ, and the result
scaled back to length r. The constants here are the single source of the geometry, so
every figure in the sequence agrees with the goal figure (same β, same θ, same r).

The generic 2D stage and primitives live in :mod:`_scene2d`; this module adds the
rotation-sequence constants and re-exports the shared helpers so the ``rotate*`` figures
import everything from one place.

Figure files are jupytext percent notebooks in the style of epix-mirror's
``notebooks/``; ``tools/render_epix_figures.py`` runs each in a fresh process (and
skips this ``_``-prefixed helper). CC0, like the hand-drawn SVGs these replace.
"""

from __future__ import annotations

import math

from _scene2d import (
    BACKGROUND,
    BLUE,
    GREEN,
    ORIGIN,
    PURPLE,
    PURPLE_FILL,
    PendingFigure,
    Point,
    epix,
    leg,
    polar,
    right_angle_marker,
    unit_circle_scene,
    vector,
    wedge,
)

__all__: list[str] = [
    "BETA",
    "THETA",
    "R",
    "ORIGIN",
    "PURPLE",
    "PURPLE_FILL",
    "GREEN",
    "BLUE",
    "BACKGROUND",
    "PendingFigure",
    "Point",
    "epix",
    "polar",
    "unit_circle_scene",
    "vector",
    "wedge",
    "right_angle_marker",
    "leg",
]

BETA: float = math.radians(66)  # the angle of a itself
THETA: float = math.radians(66)  # the angle we rotate BY (same as the goal figure)
R: float = 1.25  # |a|: a is not a unit vector -- the circle is only for scale
