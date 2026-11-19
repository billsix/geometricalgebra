"""The 𝒢₂ subsets picture: the whole algebra, with the named kinds of element inside it.

Drawn by the prebuilt figure ``g2subsets`` (on the *Defining the Algebra: G2* page) and
live by ``notebooks/defining-g2.py``, so both show the same diagram.

The outer box is every element of 𝒢₂, ``s + v_1 e_1 + v_2 e_2 + B e_12``. Inside it:
the vectors (grade 1), and the versors (scalar plus bivector), which contain the
scalars (grade 0) and the bivectors (grade 2). Each region carries one example, and
``1 + e_1`` sits in the box outside every region: a general element that belongs to no
named kind. The colours follow the book's figures, and each label is the colour of the
region it names.

Every call passes its arguments by keyword (the
``check_epix_keywords`` gate). CC0, like the other figure helpers.
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from gacalc.epixscene.scene2d import (
    BACKGROUND,
    BLUE,
    GREEN,
    PURPLE,
    PendingFigure,
    Point,
    epix,
)

__all__: list[str] = ["BACKGROUND", "PendingFigure", "g2_subsets_scene"]

_LOWER_LEFT: Point = Point(x=0.0, y=0.0)
_UPPER_RIGHT: Point = Point(x=10.0, y=6.4)
_SIZE: str = "4.6x2.94in"
_BOX_FILL: epix.Color = epix.rgb(r=0.97, g=0.97, b=0.97)
_VERSOR_FILL: epix.Color = epix.rgb(r=0.93, g=0.88, b=0.92)
_SCALAR_FILL: epix.Color = epix.rgb(r=0.85, g=0.93, b=0.85)
_BIVECTOR_FILL: epix.Color = epix.rgb(r=0.86, g=0.88, b=0.97)
_VECTOR_FILL: epix.Color = epix.rgb(r=0.97, g=0.91, b=0.82)
_ORANGE: epix.Color = epix.rgb(r=0.7, g=0.35, b=0.0)


def _region(center: Point, radius: Point, edge: epix.Color, fill: epix.Color) -> None:
    """A filled ellipse with a coloured edge."""
    epix.pen(color=edge, width=1.2)
    epix.fill(color=fill)
    epix.ellipse(center=center, radius=radius)
    epix.nofill()


def _text(at: Point, text: str, color: epix.Color) -> None:
    """A centred label in ``color``."""
    epix.label_color(color=color)
    epix.label(at=at, offset=Point(x=0, y=0), text=text, align=epix.LabelPos.c)


@contextmanager
def g2_subsets_scene() -> Generator[PendingFigure]:
    """The subsets diagram, as an open figure.

    Callers may draw more before it closes.
    """
    fig: PendingFigure
    with epix.figure(
        lower_left=_LOWER_LEFT,
        upper_right=_UPPER_RIGHT,
        size=_SIZE,
        background=BACKGROUND,
    ) as fig:
        epix.font_size(size="small")
        black: epix.Color = epix.black()
        epix.pen(color=black, width=1.2)
        epix.fill(color=_BOX_FILL)
        epix.rect(lower_left=Point(x=0.1, y=0.1), upper_right=Point(x=9.9, y=6.3))
        epix.nofill()
        _text(
            at=Point(x=5.0, y=5.85),
            text=r"$\mathcal{G}_2$: $s + v_1 * \vec{\mathbf{e}}_1"
            r" + v_2 * \vec{\mathbf{e}}_2 + b * \mathbf{e}_{12}$",
            color=black,
        )

        _region(
            center=Point(x=2.1, y=3.0),
            radius=Point(x=1.75, y=1.5),
            edge=_ORANGE,
            fill=_VECTOR_FILL,
        )
        _text(at=Point(x=2.1, y=3.55), text=r"Vector (grade 1)", color=_ORANGE)
        _text(
            at=Point(x=2.1, y=2.75),
            text=r"$3 * \vec{\mathbf{e}}_1 + 4 * \vec{\mathbf{e}}_2$",
            color=_ORANGE,
        )

        _region(
            center=Point(x=6.85, y=2.9),
            radius=Point(x=2.85, y=2.25),
            edge=PURPLE,
            fill=_VERSOR_FILL,
        )
        _text(at=Point(x=6.85, y=4.6), text=r"Versor (scalar + bivector)", color=PURPLE)
        _text(
            at=Point(x=6.85, y=4.05),
            text=r"$\cos(\theta) + \sin(\theta) * \mathbf{e}_{12}$",
            color=PURPLE,
        )

        _region(
            center=Point(x=5.65, y=2.25),
            radius=Point(x=1.15, y=0.95),
            edge=GREEN,
            fill=_SCALAR_FILL,
        )
        _text(at=Point(x=5.65, y=2.75), text=r"Scalar", color=GREEN)
        _text(at=Point(x=5.65, y=2.25), text=r"(grade 0)", color=GREEN)
        _text(at=Point(x=5.65, y=1.7), text=r"$3$", color=GREEN)

        _region(
            center=Point(x=8.05, y=2.25),
            radius=Point(x=1.15, y=0.95),
            edge=BLUE,
            fill=_BIVECTOR_FILL,
        )
        _text(at=Point(x=8.05, y=2.75), text=r"Bivector", color=BLUE)
        _text(at=Point(x=8.05, y=2.25), text=r"(grade 2)", color=BLUE)
        _text(at=Point(x=8.05, y=1.7), text=r"$2 * \mathbf{e}_{12}$", color=BLUE)

        epix.pen(color=black, width=1.0)
        epix.label_color(color=black)
        epix.dot(at=Point(x=2.1, y=0.75))
        _text(
            at=Point(x=2.1, y=0.4),
            text=r"$1 + \vec{\mathbf{e}}_1$: none of these",
            color=black,
        )
        yield fig
