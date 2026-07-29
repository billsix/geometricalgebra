# Copyright (c) 2018-2026 William Emerison Six
# SPDX-License-Identifier: LGPL-2.1-only
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License, version
# 2.1, as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License (the LICENSE file in this repository)
# for more details.


import contextlib
import contextvars
import itertools
import math
from collections.abc import Generator, Sequence
from typing import cast

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
import sympy
from IPython import get_ipython
from IPython.display import Markdown, Math, display
from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import Polygon
from matplotlib_inline.backend_inline import set_matplotlib_formats

from gacalc.base import BladeCoef, Coef, MultiVectorBase, blade_dict_latex
from gacalc.gn import (
    InvertibleFunction,
    MultiVector,
    identity,
)

# The inline SVG backend is only meaningful inside an IPython/Jupyter session;
# guarding it lets this module import headless (under pytest, or a plain script)
# instead of raising when there is no shell to enable a GUI for.
if get_ipython() is not None:
    set_matplotlib_formats("svg")

_IDENTITY = identity()


def _coord(mv: MultiVectorBase, blade: tuple[int, ...]) -> Coef:
    """The coefficient ``mv`` stores on ``blade`` (e.g. (1,) for e_1, (2,) for e_2).

    Reads the value straight from the blade-dict interchange -- the coefficient
    each representation already holds -- rather than recomputing it.
    """
    return mv.to_blade_dict().get(blade, 0)


def _to_xy(mv: MultiVectorBase) -> list[float]:
    """``mv``'s (e_1, e_2) coefficients as a plain ``[x, y]`` for matplotlib.

    Was written inline as ``lambda mv: [float(_coord(mv, (1,))), float(_coord(mv,
    (2,)))]`` in nine places across five ``draw_*`` helpers.  It lives at module
    scope rather than inside each of them because all five need it.
    """
    return [float(_coord(mv, (1,))), float(_coord(mv, (2,)))]


extra_lines_multiplier: int = 3


def generategridlines(
    graph_bounds: tuple[int, int],
    interval: int = 1,
    cls: type[MultiVectorBase] = MultiVector,
) -> Generator[tuple[list[MultiVectorBase], int], None, None]:
    ex = cls.basis_vector(1)
    ey = cls.basis_vector(2)
    for x in range(
        -graph_bounds[0] * extra_lines_multiplier,
        graph_bounds[0] * extra_lines_multiplier,
        interval,
    ):
        thickness = 4 if np.isclose(x, 0.0) else 1
        yield (
            [
                x * ex + (-graph_bounds[1] * extra_lines_multiplier) * ey,
                x * ex + (graph_bounds[1] * extra_lines_multiplier) * ey,
            ],
            thickness,
        )

    for y in range(
        -graph_bounds[1] * extra_lines_multiplier,
        graph_bounds[1] * extra_lines_multiplier,
        interval,
    ):
        thickness = 4 if np.isclose(y, 0.0) else 1
        yield (
            [
                (-graph_bounds[0] * extra_lines_multiplier) * ex + y * ey,
                (graph_bounds[0] * extra_lines_multiplier) * ex + y * ey,
            ],
            thickness,
        )


#: The axes established by the enclosing ``create_graphs()`` block.
#:
#: A :class:`contextvars.ContextVar` rather than a plain module global for two
#: reasons.  ``set()`` returns a token and ``reset(token)`` restores the
#: *previous* value, so nested ``create_graphs()`` blocks no longer clobber each
#: other (a bare global left the outer block with ``None``).  And an unset
#: ContextVar raises at the point of use, which is how ``_current_axes()`` can
#: report the real mistake instead of an ``AttributeError`` further downstream.
_axes: contextvars.ContextVar[Axes] = contextvars.ContextVar("axes")


def _current_axes() -> Axes:
    """The axes of the enclosing ``create_graphs()`` block.

    Raises :class:`RuntimeError` naming the actual mistake if there is no such
    block -- this replaced scattered ``assert axes is not None`` checks.
    """
    try:
        return _axes.get()
    except LookupError:
        raise RuntimeError(
            "no active figure -- call this inside a `with create_graphs():` block"
        ) from None


@contextlib.contextmanager
def create_graphs(
    graph_bounds: tuple[int, int] = (3, 3),
    title: str | None = None,
    filename: str | None = None,
) -> Generator[Axes, None, Figure]:
    fig, axes = plt.subplots(figsize=graph_bounds)
    token = _axes.set(axes)
    axes.set_xlim((-graph_bounds[0], graph_bounds[0]))
    axes.set_ylim((-graph_bounds[1], graph_bounds[1]))

    plt.tight_layout()

    try:
        yield axes
    finally:
        _axes.reset(token)

    fig.patch.set_edgecolor("black")
    fig.patch.set_linewidth(2)

    # make sure the x and y axis are equally proportional in screen space
    plt.gca().set_aspect("equal", adjustable="box")
    axes.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1))
    axes.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1))
    fig.canvas.draw()
    np.array(cast(FigureCanvasAgg, fig.canvas).renderer.buffer_rgba())
    display(fig)
    plt.close()

    return fig


def create_basis(
    fn: InvertibleFunction = _IDENTITY,
    graph_bounds: tuple[int, int] = (10, 10),
    gridline_interval: int = 1,
    xcolor: tuple[float, float, float] = (0.0, 0.0, 1.0),
    ycolor: tuple[float, float, float] = (1.0, 0.0, 1.0),
    cls: type[MultiVectorBase] = MultiVector,
) -> None:
    # plot transformed basis
    for vecs, thickness in generategridlines(
        graph_bounds, interval=gridline_interval, cls=cls
    ):
        plt.plot(
            [float(_coord(fn(vec), (1,))) for vec in vecs],
            [float(_coord(fn(vec), (2,))) for vec in vecs],
            "-",
            lw=thickness,
            color=(0.1, 0.2, 0.5),
            alpha=0.3,
        )


def create_unit_circle(
    fn: InvertibleFunction = _IDENTITY,
    cls: type[MultiVectorBase] = MultiVector,
) -> None:
    ex = cls.basis_vector(1)
    ey = cls.basis_vector(2)

    def generate_circle() -> Generator[list[MultiVectorBase], None, None]:
        theta_increment: float = 0.01
        scale_radius: float = 1.0

        for theta in np.arange(0.0, 2 * math.pi, theta_increment):
            yield (
                [
                    scale_radius * (math.cos(theta) * ex + math.sin(theta) * ey),
                    scale_radius
                    * (
                        math.cos(theta + theta_increment) * ex
                        + math.sin(theta + theta_increment) * ey
                    ),
                ]
            )

    # plot transformed basis
    for vecs in generate_circle():
        plt.plot(
            [float(_coord(fn(vec), (1,))) for vec in vecs],
            [float(_coord(fn(vec), (2,))) for vec in vecs],
            "-",
            lw=1,
            color=(0.0, 0.0, 0.0),
            alpha=0.5,
        )


def create_x_and_y(
    fn: InvertibleFunction = _IDENTITY,
    xcolor: tuple[float, float, float] = (0.0, 0.0, 1.0),
    ycolor: tuple[float, float, float] = (1.0, 0.0, 1.0),
    cls: type[MultiVectorBase] = MultiVector,
) -> None:
    ex = cls.basis_vector(1)
    ey = cls.basis_vector(2)
    origin = cls.zero()
    # x axis
    x_axis = [origin, ex]
    plt.plot(
        [float(_coord(fn(vec), (1,))) for vec in x_axis],
        [float(_coord(fn(vec), (2,))) for vec in x_axis],
        "-",
        lw=1.0,
        color=xcolor,
    )

    # y axis
    y_axis = [origin, ey]
    plt.plot(
        [float(_coord(fn(vec), (1,))) for vec in y_axis],
        [float(_coord(fn(vec), (2,))) for vec in y_axis],
        "-",
        lw=1.0,
        color=ycolor,
    )


def cosine(v1: MultiVectorBase, v2: MultiVectorBase) -> Coef:
    return (v1.dot(v2) * (abs(v1 * v2) ** (-1))).scalar_part()


def sine(v1: MultiVectorBase, v2: MultiVectorBase) -> Coef:
    # rotate v1 by 90 degrees in the e_1 e_2 plane (v1 * e_1 e_2), then project on v2
    rot90: MultiVectorBase = v1 * type(v1).from_blade_dict({(1, 2): 1})
    return (rot90.dot(v2) * (abs(v1 * v2) ** (-1))).scalar_part()


def _draw_labelled_triangle(
    vertex_coefficients: Sequence[tuple[float, float]],
    labels: Sequence[str],
    fn: InvertibleFunction = _IDENTITY,
    color: tuple[float, float, float] = (0.0, 0.0, 1.0),
    cls: type[MultiVectorBase] = MultiVector,
    label_offset_x_sign: float = 1.0,
) -> None:
    """Draw a filled, vertex-labelled triangle under the transform ``fn``.

    The three ``draw_*_triangle`` helpers below were 58-line near-duplicates
    (91-93% identical); the only things that varied were the two non-origin
    vertices, the label strings, and which way the labels are nudged in x.
    ``vertex_coefficients`` gives each vertex as ``(a, b)`` meaning
    ``a * e_1 + b * e_2``.
    """
    axes = _current_axes()
    ex = cls.basis_vector(1)
    ey = cls.basis_vector(2)
    origin = cls.zero()
    x_prime_direction_world_space = fn(ex) - fn(origin)
    x_world_space = ex
    y_prime_direction_world_space = fn(ey) - fn(origin)
    angle_radians = math.atan2(
        sine(x_world_space, x_prime_direction_world_space),
        cosine(x_world_space, x_prime_direction_world_space),
    )
    label_offset = (
        0.0 * x_prime_direction_world_space + 0.20 * y_prime_direction_world_space
    )

    vertices = [fn(a * ex + b * ey) for a, b in vertex_coefficients]

    triangle = Polygon(
        list(map(_to_xy, vertices)),
        closed=True,
        facecolor="lightblue",
        edgecolor="black",
    )
    axes.add_patch(triangle)

    vertices_as_np = np.array(list(map(_to_xy, vertices)))
    # Plot dots at the vertices
    axes.scatter(
        vertices_as_np[:, 0], vertices_as_np[:, 1], color="red", s=5, zorder=5
    )  # zorder ensures dots are on top

    # Label each vertex
    for i, label in enumerate(labels):
        # Use plt.annotate to place the label near the point
        plt.annotate(
            label,
            xy=(vertices_as_np[i, 0], vertices_as_np[i, 1]),
            xytext=(
                vertices_as_np[i, 0] + label_offset_x_sign * _coord(label_offset, (1,)),
                vertices_as_np[i, 1] + _coord(label_offset, (2,)),
            ),
            rotation=math.degrees(angle_radians),
            rotation_mode="anchor",
            zorder=6,
        )


def draw_isoceles_triangle(
    fn: InvertibleFunction = _IDENTITY,
    color: tuple[float, float, float] = (0.0, 0.0, 1.0),
    cls: type[MultiVectorBase] = MultiVector,
) -> None:
    """An isoceles triangle with vertices labelled A, B, C."""
    _draw_labelled_triangle(
        [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)], ["A", "B", "C"], fn, color, cls
    )


def draw_second_right_triangle(
    fn: InvertibleFunction = _IDENTITY,
    color: tuple[float, float, float] = (0.0, 0.0, 1.0),
    cls: type[MultiVectorBase] = MultiVector,
) -> None:
    """A 3-4-5 right triangle in the second quadrant, labelled by coordinate."""
    _draw_labelled_triangle(
        [(0.0, 0.0), (0.0, 3.0), (-4.0, 3.0)],
        ["(0,0)", "(0,3)", "(-4,3)"],
        fn,
        color,
        cls,
        label_offset_x_sign=-1.0,
    )


def draw_right_triangle(
    fn: InvertibleFunction = _IDENTITY,
    color: tuple[float, float, float] = (0.0, 0.0, 1.0),
    cls: type[MultiVectorBase] = MultiVector,
) -> None:
    """A 3-4-5 right triangle in the first quadrant, labelled by coordinate."""
    _draw_labelled_triangle(
        [(0.0, 0.0), (3.0, 0.0), (3.0, 4.0)],
        ["(0,0)", "(3,0)", "(3,4)"],
        fn,
        color,
        cls,
    )


#         # Annotate with a 45-degree rotation
# ax.annotate('Rotated Annotation', xy=(0.5, 0.5), xytext=(0.7, 0.3),
#             arrowprops=dict(facecolor='black', shrink=0.05),
#             rotation=45)


def draw_ndc(
    fn: InvertibleFunction = _IDENTITY,
    color: tuple[float, float, float] = (0.0, 0.0, 1.0),
    cls: type[MultiVectorBase] = MultiVector,
) -> None:
    axes = _current_axes()
    ex = cls.basis_vector(1)
    ey = cls.basis_vector(2)
    origin = cls.zero()
    x_prime_direction_world_space = fn(ex) - fn(origin)
    x_world_space = ex
    y_prime_direction_world_space = fn(ey) - fn(origin)
    angle_radians = math.atan2(
        sine(x_world_space, x_prime_direction_world_space),
        cosine(x_world_space, x_prime_direction_world_space),
    )
    label_offset = (
        0.0 * x_prime_direction_world_space + 0.20 * y_prime_direction_world_space
    )

    vertices = [
        fn(v)
        for v in [
            (-1.0) * ex + (-1.0) * ey,
            (1.0) * ex + (-1.0) * ey,
            (1.0) * ex,
            +(1.0) * ey,
            (-1.0) * ex + (1.0) * ey,
        ]
    ]

    square = Polygon(
        list(map(_to_xy, vertices)),
        closed=True,
        fc="none",
        edgecolor="black",
    )
    axes.add_patch(square)

    vertices_as_np = np.array(list(map(_to_xy, vertices)))
    # Plot dots at the vertices
    axes.scatter(
        vertices_as_np[:, 0], vertices_as_np[:, 1], color="red", s=5, zorder=5
    )  # zorder ensures dots are on top

    # Label each vertex
    labels = ["(-1,-1)", "(1,-1)", "(1,1)", "(-1,1)"]
    for i, label in enumerate(labels):
        # Use plt.annotate to place the label near the point
        plt.annotate(
            label,
            xy=(vertices_as_np[i, 0], vertices_as_np[i, 1]),
            xytext=(
                vertices_as_np[i, 0] + _coord(label_offset, (1,)),
                vertices_as_np[i, 1] + _coord(label_offset, (2,)),
            ),
            rotation=math.degrees(angle_radians),
            rotation_mode="anchor",
            zorder=6,
        )


def draw_screen(
    width: int,
    height: int,
    fn: InvertibleFunction = _IDENTITY,
    color: tuple[float, float, float] = (0.0, 0.0, 1.0),
    cls: type[MultiVectorBase] = MultiVector,
) -> None:
    axes = _current_axes()
    ex = cls.basis_vector(1)
    ey = cls.basis_vector(2)
    d_width = 2.0 / width
    d_height = 2.0 / height
    for x in range(width):
        for y in range(height):
            vertices = [
                fn(v)
                for v in [
                    (-1.0 + d_width * x) * ex + (-1.0 + d_height * y) * ey,
                    (-1.0 + d_width * (x + 1)) * ex + (-1.0 + d_height * y) * ey,
                    (-1.0 + d_width * (x + 1)) * ex + (-1.0 + d_height * (y + 1)) * ey,
                    (-1.0 + d_width * (x)) * ex + (-1.0 + d_height * (y + 1)) * ey,
                ]
            ]

            square = Polygon(
                list(
                    map(
                        _to_xy,
                        vertices,
                    )
                ),
                closed=True,
                fc="none",
                edgecolor="black",
            )
            axes.add_patch(square)


def _blade_latex(blade: tuple[int, ...]) -> str:
    if blade == ():
        return "1"
    return r"\,".join(r"\mathbf{\vec{e}}_{" + str(b) + "}" for b in blade)


def _coef_as_float(coef: Coef) -> float | None:
    try:
        return float(coef)
    except (TypeError, ValueError):
        return None


def plot_multivector(
    mv: MultiVectorBase,
    x_range: tuple[float, float] | None = None,
    title: str | None = None,
    figsize: tuple[float, float] | None = None,
    symbolic_range: float = 0.8,
    random_seed: int | None = 0,
) -> Figure:
    """Plot each blade of ``mv`` on its own horizontal number line, stacked vertically.

    Works on any ``MultiVectorBase`` representation (``Gn``, ``G1``/``G2``/``G3``)
    via the ``to_blade_dict()`` interchange protocol.

    Each row is one basis blade (sorted by grade, then by index). Numeric
    coefficients appear as a dot at their value. Symbolic coefficients are
    placed at a small random x in ``[-symbolic_range, symbolic_range]`` (so
    rows don't all stack at zero); the latex of the symbol labels the dot.
    ``random_seed`` defaults to 0 for reproducibility — pass ``None`` for
    fresh randomness on every call.
    """
    blade_dict: BladeCoef = mv.to_blade_dict()
    blades = sorted(blade_dict.keys(), key=lambda b: (len(b), b)) or [()]
    n = len(blades)

    rng: np.random.Generator = np.random.default_rng(random_seed)

    coefs = [blade_dict.get(b, 0) for b in blades]
    xs: list[float] = []
    for coef in coefs:
        x: float | None = _coef_as_float(coef)
        xs.append(
            x if x is not None else float(rng.uniform(-symbolic_range, symbolic_range))
        )

    if x_range is not None:
        xmin, xmax = x_range
    else:
        m = max(max(abs(x) for x in xs), 1.0)
        xmin, xmax = -1.2 * m, 1.2 * m

    fig, ax = plt.subplots(figsize=figsize or (8, max(2.0, 0.7 * n)))

    for i, (blade, coef, x) in enumerate(zip(blades, coefs, xs)):
        y = n - 1 - i  # top blade drawn first
        ax.axhline(y, xmin=0.0, xmax=1.0, color="gray", linewidth=0.5, alpha=0.6)
        ax.plot([0], [y], marker="|", color="black", markersize=14, zorder=2)

        is_numeric = _coef_as_float(coef) is not None
        ax.plot(
            [x],
            [y],
            marker="o",
            color="C0" if is_numeric else "C1",
            markersize=10,
            zorder=3,
        )
        label = f"{x:g}" if is_numeric else "$" + sympy.latex(coef) + "$"
        ax.annotate(
            label,
            (x, y),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            fontsize=10,
        )

        ax.text(
            xmin - 0.06 * (xmax - xmin),
            y,
            "$" + _blade_latex(blade) + "$",
            ha="right",
            va="center",
            fontsize=12,
        )

    ax.set_xlim(xmin - 0.20 * (xmax - xmin), xmax + 0.05 * (xmax - xmin))
    ax.set_ylim(-0.5, n - 0.5)
    ax.set_yticks([])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)

    ax.set_title(title if title is not None else mv._repr_latex_())

    plt.tight_layout()
    display(fig)
    plt.close(fig)
    return fig


def _blade_terms(mv: MultiVectorBase) -> list:
    """The single-blade multivectors that sum to ``mv`` (its product-table terms).

    ``__iter__`` now yields a multivector's coefficient *values*, so the
    component-by-component product breakdown decomposes via ``to_blade_dict``.
    """
    return [
        type(mv).from_blade_dict({blade: coef})
        for blade, coef in sorted(
            mv.to_blade_dict().items(), key=lambda item: (len(item[0]), item[0])
        )
    ]


def _expand_numerators_dict(mv: MultiVectorBase) -> dict:
    """``mv``'s blade dict with each coefficient's NUMERATOR expanded and its
    denominator left factored — for display.

    This deliberately does NOT rebuild the multivector: it expands the raw
    ``to_blade_dict()`` coefficients in place.  That matters for the eager-simplifying
    ``Gn`` (`displaymv.py`), whose ``from_blade_dict`` re-runs ``sympy.simplify`` and
    would re-factor the just-distributed numerator (e.g. back to ``a0*(b0*c0 + ...)``).
    Expanding the dict directly keeps the distributed form on every representation.
    """
    out: dict = {}
    for blade, coef in mv.to_blade_dict().items():
        numerator, denominator = sympy.fraction(sympy.together(coef))
        out[blade] = sympy.expand(numerator) / denominator
    return out


def show_mult(a: MultiVectorBase, b: MultiVectorBase) -> None:
    display(Markdown("**We want to evaluate**"))
    # print the values as latex before they are multiplied
    display(Math("$($" + a._repr_latex_() + "$)*($" + b._repr_latex_() + "$)$"))
    display(Markdown("**Multivector Multiplication is distributive over additon**"))

    data: list = list(itertools.product(_blade_terms(a), _blade_terms(b)))
    result = [(left, "*", right, "=", left * right) for left, right in data]
    df: pd.DataFrame = pd.DataFrame(
        result,
        columns=pd.Index(["Left Component", "*", "Right Component", "=", "Product"]),
    )
    # Convert to markdown string and display
    df_latex: pd.DataFrame = df.map(
        lambda x: (
            blade_dict_latex(_expand_numerators_dict(x))
            if hasattr(x, "to_blade_dict")
            else x
        )
    )
    display(Markdown(df_latex.to_markdown(index=False)))
    display(Markdown("**Summing all the products up, we get**"))
    display(Math("$" + blade_dict_latex(_expand_numerators_dict(a * b)) + "$"))
