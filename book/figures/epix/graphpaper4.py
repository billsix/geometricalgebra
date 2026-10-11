# %% [markdown]
# # graphpaper4 — it was the paper that turned
#
# Here is the easy way to see it: draw the grid *lines* rotated too (blue). The points
# did not each move on their own — the whole **sheet of graph paper** turned by 30°, and
# every point rode along with it. That is all a rotation is: turning the graph paper.

# %%
from __future__ import annotations

from _graphpaper_scene import (
    ANGLE,
    BACKGROUND,  # noqa: F401  (read by tools/render_epix_figures.py from the module globals)
    BLUE,
    PendingFigure,
    Point,
    draw_grid,
    epix,
    unit_circle_scene,
)

LOW: Point = Point(x=-2.0, y=-0.6)
HIGH: Point = Point(x=3.4, y=4.6)

fig: PendingFigure
with unit_circle_scene(lower_left=LOW, upper_right=HIGH, disc=False) as fig:
    draw_grid(angle=0.0, color=epix.black(intensity=0.2), width=0.7, dots=False)
    draw_grid(angle=ANGLE, color=BLUE, width=0.9, dots=True)

# %%
fig
