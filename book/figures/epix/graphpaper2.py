# %% [markdown]
# # graphpaper2 — rotate a few points by 30°
#
# Take a few of the grid points and rotate each about the origin by 30°: this corner
# swings to there, that one to there. Doing it point by point is a lot of work.

# %%
from __future__ import annotations

from _graphpaper_scene import (
    ANGLE,
    BACKGROUND,  # noqa: F401  (read by tools/render_epix_figures.py from the module globals)
    BLUE,
    FAINT,
    PendingFigure,
    Point,
    draw_grid,
    epix,
    rotate,
    unit_circle_scene,
)

LOW: Point = Point(x=-2.0, y=-0.6)
HIGH: Point = Point(x=3.4, y=4.6)
MOVERS: list[Point] = [Point(x=3.0, y=0.0), Point(x=0.0, y=3.0), Point(x=2.0, y=2.0)]

fig: PendingFigure
with unit_circle_scene(lower_left=LOW, upper_right=HIGH, disc=False) as fig:
    draw_grid(angle=0.0, color=FAINT, width=0.8, dots=True)
    for mover in MOVERS:
        moved: Point = rotate(point=mover, angle=ANGLE)
        epix.pen(color=BLUE, width=1.2)
        epix.arrow(tail=mover, head=moved, scale=0.6)
        epix.dot(at=moved)

# %%
fig
