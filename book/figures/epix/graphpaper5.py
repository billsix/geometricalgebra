# %% [markdown]
# # graphpaper5 — plot y = x² on the tilted paper
#
# The rotated grid is just graph paper, tilted. We can plot on it exactly as we always
# do: here is `y = x²` drawn on the rotated frame. It is the same parabola you know from
# high school — the paper under it is simply turned by 30°.

# %%
from __future__ import annotations

from _graphpaper_scene import (
    ANGLE,
    BACKGROUND,  # noqa: F401  (read by tools/render_epix_figures.py from the module globals)
    GREEN,
    PendingFigure,
    Point,
    draw_grid,
    epix,
    parabola_points,
    unit_circle_scene,
)

LOW: Point = Point(x=-2.0, y=-0.6)
HIGH: Point = Point(x=3.4, y=4.6)

fig: PendingFigure
with unit_circle_scene(lower_left=LOW, upper_right=HIGH, disc=False) as fig:
    draw_grid(angle=ANGLE, color=epix.black(intensity=0.45), width=0.8, dots=False)
    curve: list[Point] = parabola_points(angle=ANGLE, x_min=0.0, x_max=1.8)
    epix.pen(color=GREEN, width=1.8)
    epix.Path(data=curve, closed=False, filled=False).draw()
    epix.label_color(color=GREEN)
    epix.label(
        at=curve[-1], offset=Point(x=10, y=2), text="$y = x^2$", align=epix.LabelPos.l
    )
    epix.label_color(color=epix.black())

# %%
fig
