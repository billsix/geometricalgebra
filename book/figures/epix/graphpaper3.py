# %% [markdown]
# # graphpaper3 — rotate every point
#
# Rotate all sixteen grid points by 30° (blue). The faint grid is where they started.
# The whole grid has turned — but we did it the hard way, one point at a time.

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
    grid_points,
    unit_circle_scene,
)

LOW: Point = Point(x=-2.0, y=-0.6)
HIGH: Point = Point(x=3.4, y=4.6)

fig: PendingFigure
with unit_circle_scene(lower_left=LOW, upper_right=HIGH, disc=False) as fig:
    draw_grid(angle=0.0, color=FAINT, width=0.8, dots=True)
    epix.pen(color=BLUE, width=1.0)
    for moved in grid_points(angle=ANGLE):
        epix.dot(at=moved)

# %%
fig
