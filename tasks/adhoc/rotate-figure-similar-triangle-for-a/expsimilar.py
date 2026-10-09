# %% [markdown]
# # EXPERIMENT (not for the book) — vector a as a similar triangle
#
# Overlays the unit right triangle (cos θ, sin θ) and a's scaled-up similar triangle
# (r·cos θ, r·sin θ) to show the same-angles-are-proportional idea. R_EXP is the
# experiment knob for |a|; re-render at 1.25, 1.6, 2.0 to judge label overlap.

# %%
from __future__ import annotations

import math

from _rotation_scene import (
    BACKGROUND,  # noqa: F401  (read by tools/render_epix_figures.py from the module globals)
    BETA,
    BLUE,
    GREEN,
    ORIGIN,
    THETA,
    PendingFigure,
    Point,
    epix,
    leg,
    polar,
    unit_circle_scene,
    vector,
    wedge,
)
from _scene2d import dashed_vector

# %%
R_EXP: float = 1.6  # experiment knob: |a|

# unit triangle (radius 1)
x_prime: Point = polar(radius=1, angle=BETA)
y_prime: Point = polar(radius=1, angle=BETA + math.pi / 2)
rotated: Point = polar(radius=1, angle=BETA + THETA)
foot: Point = polar(radius=math.cos(THETA), angle=BETA)

# a's scaled-up similar triangle (radius R_EXP)
result: Point = polar(radius=R_EXP, angle=BETA + THETA)
big_foot: Point = polar(radius=R_EXP * math.cos(THETA), angle=BETA)

fig: PendingFigure
with unit_circle_scene(
    lower_left=Point(x=-2.6, y=-1.3), upper_right=Point(x=2.2, y=3.1)
) as fig:
    wedge(start=BETA, finish=BETA + THETA, text=r"$\theta$")
    vector(head=x_prime, text=r"$\vec{x'}$")
    vector(
        head=y_prime, text=r"$\vec{y'}$", offset=Point(x=-7, y=4), align=epix.LabelPos.l
    )

    # unit triangle: hypotenuse dashed (the unit-circle direction), legs cos/sin
    dashed_vector(tail=ORIGIN, head=rotated)
    leg(
        tail=ORIGIN,
        head=foot,
        color=BLUE,
        text=r"$\cos(\theta)$",
        angle=BETA,
        offset=Point(x=11, y=-5),
    )
    leg(
        tail=foot,
        head=rotated,
        color=GREEN,
        text=r"$\sin(\theta)$",
        angle=BETA - math.pi / 2,
        offset=Point(x=5, y=11),
    )

    # a's similar triangle: hypotenuse solid (the actual a), legs r*cos/r*sin
    leg(
        tail=ORIGIN,
        head=big_foot,
        color=BLUE,
        text=r"$r\cos(\theta)$",
        angle=BETA,
        offset=Point(x=11, y=-16),
    )
    leg(
        tail=big_foot,
        head=result,
        color=GREEN,
        text=r"$r\sin(\theta)$",
        angle=BETA - math.pi / 2,
        offset=Point(x=16, y=11),
    )
    vector(head=result, text=r"$\vec{r}(\vec{a};\theta)$", offset=Point(x=6, y=10))

# %%
fig
