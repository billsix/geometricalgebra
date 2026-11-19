"""Live ePiX helpers for the relative-graph-paper pictures.

Used by ``book/docs/notebooks/relative-graph-paper.py`` and
``rotation-graph-paper.py``. A function of the plane carries the whole sheet of graph
paper with it: its grid lines, its origin, its two unit arrows, and anything drawn on
it. Each picture shows the standard graph paper faintly underneath, and the carried
paper on top, so a reader sees where the sheet went.

The function is passed in as a :class:`Mapping` ``(x, y) -> Point``: the point that
the spot with coordinates ``(x, y)`` on the standard paper is carried to. The notebooks
build it from a gacalc function, so this module needs only ePiX.

The colours follow the book's figures: the carried grid brown, the carried first arrow
green, the second blue, the shape on the paper purple, and each label in the colour of
what it labels. Every call passes its arguments by keyword (the ``check_epix_keywords``
gate). CC0, like the other figure helpers.
"""

from __future__ import annotations

from collections.abc import Generator, Sequence
from contextlib import contextmanager
from typing import Protocol

from gacalc.epixscene.scene2d import (
    BACKGROUND,
    BLUE,
    GREEN,
    PURPLE,
    PURPLE_FILL,
    PendingFigure,
    Point,
    epix,
)

__all__: list[str] = [
    "Mapping",
    "PendingFigure",
    "Point",
    "paper_scene",
    "carried_paper",
]


class Mapping(Protocol):
    """Where the spot with standard coordinates ``(x, y)`` is carried to."""

    def __call__(self, x_coordinate: float, y_coordinate: float) -> Point:
        """The carried spot."""
        ...


_UNIT_IN: float = 0.28  # inches per unit
_EXTENT: int = 3  # the carried paper's grid runs from -_EXTENT to _EXTENT
_SHAPE: list[tuple[float, float]] = [(0.3, 0.3), (1.6, 0.3), (0.3, 1.1)]
_CARRIED_GRID: epix.Color = epix.rgb(
    r=0.55, g=0.45, b=0.25
)  # brown, unlike the gray paper


@contextmanager
def paper_scene(
    lower_left: Point, upper_right: Point, caption: str
) -> Generator[PendingFigure]:
    """A figure with the standard graph paper drawn faintly, its axes, and ``caption``
    (a LaTeX string, usually the function so far) in the top left corner."""
    width: float = upper_right.x1() - lower_left.x1()
    height: float = upper_right.x2() - lower_left.x2()
    size: str = f"{width * _UNIT_IN:.2f}x{height * _UNIT_IN:.2f}in"
    fig: PendingFigure
    with epix.figure(
        lower_left=lower_left, upper_right=upper_right, size=size, background=BACKGROUND
    ) as fig:
        epix.font_size(size="small")
        epix.pen(color=epix.black(intensity=0.2), width=0.3)
        column: int
        for column in range(int(lower_left.x1()), int(upper_right.x1()) + 1):
            epix.line(
                tail=Point(x=column, y=lower_left.x2()),
                head=Point(x=column, y=upper_right.x2()),
            )
        row: int
        for row in range(int(lower_left.x2()), int(upper_right.x2()) + 1):
            epix.line(
                tail=Point(x=lower_left.x1(), y=row),
                head=Point(x=upper_right.x1(), y=row),
            )
        epix.pen(color=epix.black(intensity=0.45), width=0.6)
        epix.line(
            tail=Point(x=lower_left.x1(), y=0), head=Point(x=upper_right.x1(), y=0)
        )
        epix.line(
            tail=Point(x=0, y=lower_left.x2()), head=Point(x=0, y=upper_right.x2())
        )
        epix.label_color(color=epix.black())
        epix.label(
            at=Point(x=lower_left.x1(), y=upper_right.x2()),
            offset=Point(x=4, y=-4),
            text=caption,
            align=epix.LabelPos.br,
        )
        yield fig


def carried_paper(
    mapped: Mapping,
    first: str = r"$\vec{\mathbf{e}}_1'$",
    second: str = r"$\vec{\mathbf{e}}_2'$",
    shape: Sequence[tuple[float, float]] = _SHAPE,
) -> None:
    """The graph paper after the function: its grid lines (gray), the shape drawn on
    it (purple), and its two unit arrows from its carried origin (green and blue,
    labelled ``first`` and ``second``)."""
    epix.pen(color=_CARRIED_GRID, width=0.7)
    line: int
    for line in range(-_EXTENT, _EXTENT + 1):
        epix.line(
            tail=mapped(x_coordinate=line, y_coordinate=-_EXTENT),
            head=mapped(x_coordinate=line, y_coordinate=_EXTENT),
        )
        epix.line(
            tail=mapped(x_coordinate=-_EXTENT, y_coordinate=line),
            head=mapped(x_coordinate=_EXTENT, y_coordinate=line),
        )
    epix.pen(color=PURPLE, width=0.8)
    epix.fill(color=PURPLE_FILL)
    epix.Path(
        data=[mapped(x_coordinate=x, y_coordinate=y) for x, y in shape],
        closed=True,
        filled=True,
    ).draw()
    epix.nofill()
    origin: Point = mapped(x_coordinate=0, y_coordinate=0)
    tip: Point
    color: epix.Color
    text: str
    align: epix.LabelPos
    for tip, color, text, align in (
        (mapped(x_coordinate=1, y_coordinate=0), GREEN, first, epix.LabelPos.br),
        (mapped(x_coordinate=0, y_coordinate=1), BLUE, second, epix.LabelPos.tl),
    ):
        epix.pen(color=color, width=1.6)
        epix.arrow(tail=origin, head=tip, scale=0.6)
        epix.label_color(color=color)
        epix.label(at=tip, offset=Point(x=0, y=0), text=text, align=align)
    epix.pen(color=epix.black(), width=1.0)
    epix.dot(at=origin)
