"""Live ePiX helpers for the number-line notebooks (``one-dimension.py``,
``vectors-as-number-lines.py``).

Three kinds of picture:

- **graph paper**: the familiar high-school plot of ``y = m * x + b``, input across and
  output up, with a light unit grid (:func:`graph_paper_scene`, :func:`graph_line`);
- **one direction**: the input ``x * e_1`` on a number line on the left and the output
  on a number line on the right, both pointing the same way
  (:func:`number_lines_scene`, :func:`number_line`, :func:`step`). Stacked one row per
  input, the output tips trace the familiar line when the page is turned sideways;
- **a vector's number line** in the plane, its multiples ``t * v`` with a tick at each
  integer (:func:`slanted_number_line`), for ``vectors-as-number-lines.py``.

The colours follow the book's figures: inputs black, the scaling step green, the
translation step blue, outputs purple, and every label in the colour of what it labels.
Every call passes its arguments by keyword (the ``check_epix_keywords``
gate). CC0, like the other figure helpers.
"""

from __future__ import annotations

import math
from collections.abc import Generator
from contextlib import contextmanager

from gacalc.epixscene.scene2d import (
    BACKGROUND,
    BLUE,
    GREEN,
    GRID,
    PURPLE,
    PendingFigure,
    Point,
    epix,
    grid,
)

__all__: list[str] = [
    "BLACK",
    "BLUE",
    "Color",
    "GREEN",
    "OUTPUT_OFFSET",
    "PURPLE",
    "PendingFigure",
    "Point",
    "graph_line",
    "graph_paper_scene",
    "number_line",
    "number_lines_scene",
    "slanted_number_line",
    "step",
    "tip",
]

Color = epix.Color  # the colour type, for annotating a loop over colours
BLACK: epix.Color = epix.black()
GRAPH_UNIT_IN: float = 0.2  # inches per unit on the graph paper
LINES_UNIT_IN: float = 0.13  # inches per unit on the number lines
OUTPUT_OFFSET: float = 22.0  # how far right the output number line's 0 sits
_TICK: float = 0.18
_NO_SHIFT: Point = Point(x=0, y=0)


@contextmanager
def graph_paper_scene(
    lower_left: Point, upper_right: Point
) -> Generator[PendingFigure]:
    """Graph paper with a unit grid and labelled axes.

    The ``x`` axis is the input and the ``y`` axis the output.
    """
    width: float = upper_right.x1() - lower_left.x1()
    height: float = upper_right.x2() - lower_left.x2()
    size: str = f"{width * GRAPH_UNIT_IN:.2f}x{height * GRAPH_UNIT_IN:.2f}in"
    fig: PendingFigure
    with epix.figure(
        lower_left=lower_left, upper_right=upper_right, size=size, background=BACKGROUND
    ) as fig:
        epix.font_size(size="small")
        grid(lower_left=lower_left, upper_right=upper_right, color=GRID, width=0.3)
        epix.pen(color=epix.black(), width=0.9)
        x_end: Point = Point(x=upper_right.x1(), y=0)
        y_end: Point = Point(x=0, y=upper_right.x2())
        epix.arrow(tail=Point(x=lower_left.x1(), y=0), head=x_end, scale=0.6)
        epix.arrow(tail=Point(x=0, y=lower_left.x2()), head=y_end, scale=0.6)
        epix.label_color(color=epix.black())
        epix.label(at=x_end, offset=Point(x=4, y=0), text="$x$", align=epix.LabelPos.r)
        epix.label(at=y_end, offset=Point(x=0, y=4), text="$y$", align=epix.LabelPos.t)
        mark: int
        for mark in (-5, 5):
            epix.label(
                at=Point(x=mark, y=0),
                offset=Point(x=0, y=-4),
                text=f"${mark}$",
                align=epix.LabelPos.b,
            )
            epix.label(
                at=Point(x=0, y=mark),
                offset=Point(x=-4, y=0),
                text=f"${mark}$",
                align=epix.LabelPos.l,
            )
        yield fig


def graph_line(start: Point, end: Point, color: epix.Color, text: str) -> None:
    """One plotted line from ``start`` to ``end``, labelled at ``end``."""
    epix.pen(color=color, width=1.4)
    epix.line(tail=start, head=end)
    epix.label_color(color=color)
    epix.label(at=end, offset=Point(x=4, y=0), text=text, align=epix.LabelPos.r)


@contextmanager
def number_lines_scene(rows: int, low: float, high: float) -> Generator[PendingFigure]:
    """A figure tall enough for ``rows`` pairs of number lines, one unit apart.

    "input" and "output" are written over the two columns. Row 0 is at the top, at
    ``y = 0``; row ``k`` is at ``y = -k``. ``low`` and ``high`` bound the output line.
    """
    lower_left: Point = Point(x=-7.0, y=-rows + 0.3)
    upper_right: Point = Point(x=OUTPUT_OFFSET + high + 2.0, y=1.7)
    width: float = upper_right.x1() - lower_left.x1()
    height: float = upper_right.x2() - lower_left.x2()
    size: str = f"{width * LINES_UNIT_IN:.2f}x{height * LINES_UNIT_IN * 2.6:.2f}in"
    fig: PendingFigure
    with epix.figure(
        lower_left=lower_left, upper_right=upper_right, size=size, background=BACKGROUND
    ) as fig:
        epix.font_size(size="footnotesize")
        epix.label_color(color=epix.black())
        epix.label(
            at=Point(x=0, y=1.35),
            offset=Point(x=0, y=0),
            text="input",
            align=epix.LabelPos.c,
        )
        epix.label(
            at=Point(x=OUTPUT_OFFSET + 0.5 * (low + high), y=1.35),
            offset=Point(x=0, y=0),
            text="output",
            align=epix.LabelPos.c,
        )
        yield fig


def number_line(row: int, low: float, high: float, origin: float = 0.0) -> None:
    """A horizontal number line in ``row`` from ``low`` to ``high`` (in the line's own
    numbers), its ``0`` at ``x = origin``, with a tick at every integer and the ``0``
    tick labelled."""
    y: float = -row
    epix.pen(color=epix.black(intensity=0.55), width=0.6)
    epix.arrow(
        tail=Point(x=origin + low, y=y),
        head=Point(x=origin + high + 0.6, y=y),
        scale=0.5,
    )
    mark: int
    for mark in range(math.ceil(low), math.floor(high) + 1):
        epix.line(
            tail=Point(x=origin + mark, y=y - _TICK),
            head=Point(x=origin + mark, y=y + _TICK),
        )
    epix.pen(color=epix.black(), width=0.9)
    epix.line(
        tail=Point(x=origin, y=y - 2 * _TICK), head=Point(x=origin, y=y + 2 * _TICK)
    )


def step(
    row: int,
    tail: float,
    head: float,
    color: epix.Color,
    origin: float = 0.0,
    lift: float = 0.3,
) -> None:
    """An arrow along ``row``'s number line from the number ``tail`` to ``head``,
    raised by ``lift`` so it sits above the line rather than over its ticks."""
    if tail == head:
        return
    y: float = -row + lift
    epix.pen(color=color, width=1.5)
    epix.arrow(
        tail=Point(x=origin + tail, y=y), head=Point(x=origin + head, y=y), scale=0.5
    )


def tip(
    row: int, value: float, color: epix.Color, text: str, origin: float = 0.0
) -> None:
    """A dot at ``value`` on ``row``'s number line, labelled above it."""
    y: float = -row + 0.3
    epix.pen(color=color, width=1.0)
    epix.label_color(color=color)
    epix.dot(at=Point(x=origin + value, y=y))
    if text:
        epix.label(
            at=Point(x=origin + value, y=y),
            offset=Point(x=0, y=5),
            text=text,
            align=epix.LabelPos.t,
        )


def slanted_number_line(
    unit: Point,
    low: int,
    high: int,
    color: epix.Color,
    labels: tuple[int, ...] = (),
    side: float = 1.0,
    offset: Point = _NO_SHIFT,
) -> None:
    """The number line along the vector ``unit``: its points ``t * unit`` for ``t`` from
    ``low`` to ``high``, a tick at every integer ``t``, and the integers in ``labels``
    written beside their ticks, on the side ``side`` (``1`` or ``-1``) of the line. The
    whole line is shifted by ``offset``, to set two lines side by side."""
    length: float = math.hypot(unit.x1(), unit.x2())
    across: Point = Point(x=-unit.x2() / length, y=unit.x1() / length)
    epix.pen(color=color, width=0.9)
    epix.line(tail=offset + low * unit, head=offset + high * unit)
    mark: int
    for mark in range(low, high + 1):
        epix.line(
            tail=offset + mark * unit - 0.12 * across,
            head=offset + mark * unit + 0.12 * across,
        )
    epix.label_color(color=color)
    for mark in labels:
        epix.label(
            at=offset + mark * unit + side * 0.45 * across,
            offset=Point(x=0, y=0),
            text=f"${mark}$",
            align=epix.LabelPos.c,
        )
