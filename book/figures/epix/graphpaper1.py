# %% [markdown]
# # graphpaper1 — ordinary graph paper, a grid of points
#
# A 4×4 grid of points `{0,1,2,3}²` on ordinary graph paper. The next figures rotate
# it about the origin by 30°. Built with the `epix` Python package.

# %%
from __future__ import annotations

from _graphpaper_scene import (
    BACKGROUND,  # noqa: F401  (read by tools/render_epix_figures.py from the module globals)
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
    draw_grid(angle=0.0, color=epix.black(intensity=0.5), width=0.8, dots=False)
    epix.pen(color=epix.black(), width=1.0)
    for grid_point in grid_points(angle=0.0):
        epix.dot(at=grid_point)

# %%
fig
