# Copyright (c) 2025-2026 William Emerison Six
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

"""matplotlib/LaTeX plotting helpers for the demo notebooks — pictures of
multivectors (2-D and 3-D) and of transforms acting on them.

The ``create_*`` / ``draw_*`` helpers draw inside a ``with create_graphs():``
block (which sets up a square figure and renders it on exit).  Each takes an
``InvertibleFunction`` transform (default: the identity) and applies it to the
geometry it draws, so the same call shows a shape before or after a transform.
``draw_vectors`` / ``draw_bivector`` / ``draw_angle`` draw vectors, a bivector's
oriented parallelogram and a turn, in 2-D inside ``create_graphs`` or in 3-D inside
``create_graphs_3d``.
Everything is representation-agnostic — it works on any ``MultiVectorBase``
(``Gn``, ``g3.Vector``, …) via the blade-dict interchange.
"""

import contextlib
import contextvars
import math
from collections.abc import Generator, Mapping, Sequence
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import sympy
from IPython import get_ipython
from IPython.display import display
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Polygon
from matplotlib_inline.backend_inline import set_matplotlib_formats
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d.axes3d import Axes3D

from gacalc.base import (
    Blade,
    MultiVectorBase,
    Real,
    blade_latex,
)
from gacalc.gn import (
    InvertibleFunction,
    MultiVector,
    identity,
)

# show_mult lives in the display-only gacalc.nbdisplay (no matplotlib), so the
# book's notebooks can use it; re-exported here for the demo notebooks.
from gacalc.nbdisplay import show_mult as show_mult

# Each figure is emitted as SVG and as PDF. HTML and Jupyter show the SVG; the book's
# LaTeX build takes the PDF, since myst_nb's LaTeX output cannot use SVG and would
# otherwise fall back to the figure's text repr, ``<Figure size … with 1 Axes>``.
# The inline backend is only meaningful inside an IPython/Jupyter session; guarding it
# lets this module import headless (under pytest, or a plain script) instead of
# raising when there is no shell to enable a GUI for.
if get_ipython() is not None:
    set_matplotlib_formats("svg", "pdf")

# These plotting helpers accept an ``InvertibleFunction`` over ANY multivector
# representation (``Gn``, ``g3.Vector``, …) and apply it internally to
# ``MultiVectorBase`` values, so the ``fn`` param is typed ``InvertibleFunction[Any]``:
# ``InvertibleFunction`` is INVARIANT, so a fixed ``[MultiVectorBase]`` would reject the
# concrete-typed transforms callers pass, while a bound TypeVar would reject the
# internal application to ``MultiVectorBase``.  ``Any`` is gradually compatible both
# ways.
_IDENTITY = identity()


def _coord(mv: MultiVectorBase, blade: tuple[int, ...]) -> Real:
    """The coefficient ``mv`` stores on ``blade`` (e.g. (1,) for e_1, (2,) for e_2).

    Reads the value straight from the blade-dict interchange -- the coefficient
    each representation already holds -- rather than recomputing it.
    """
    return mv.to_blade_dict().get(blade, 0)


def _to_xy(mv: MultiVectorBase) -> list[float]:
    """``mv``'s (e_1, e_2) coefficients as a plain ``[x, y]`` for matplotlib.

    Module scope, not inside one helper, because all five ``draw_*`` helpers use it.
    """
    return [float(_coord(mv, (1,))), float(_coord(mv, (2,)))]


extra_lines_multiplier: int = 3


def generategridlines(
    graph_bounds: tuple[int, int],
    interval: int = 1,
    cls: type[MultiVectorBase] = MultiVector,
) -> Generator[tuple[list[MultiVectorBase], int], None, None]:
    """Yield the world-space grid lines of a ``graph_bounds``-sized plane.

    Each item is ``([start, end], thickness)`` — the two endpoint multivectors of
    one line and its line width (the x = 0 and y = 0 axes get a thick line, the
    rest thin).  ``create_basis`` maps these through a transform to draw a
    transformed grid.
    """
    ex: MultiVectorBase = cls.basis_vector(1)
    ey: MultiVectorBase = cls.basis_vector(2)
    x: int
    for x in range(
        -graph_bounds[0] * extra_lines_multiplier,
        graph_bounds[0] * extra_lines_multiplier,
        interval,
    ):
        thickness: int = 4 if np.isclose(x, 0.0) else 1
        yield (
            [
                x * ex + (-graph_bounds[1] * extra_lines_multiplier) * ey,
                x * ex + (graph_bounds[1] * extra_lines_multiplier) * ey,
            ],
            thickness,
        )

    y: int
    for y in range(
        -graph_bounds[1] * extra_lines_multiplier,
        graph_bounds[1] * extra_lines_multiplier,
        interval,
    ):
        thickness: int = 4 if np.isclose(y, 0.0) else 1
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
#: *previous* value, so nested ``create_graphs()`` blocks don't clobber each
#: other (a bare global would leave the outer block with ``None``).  And an unset
#: ContextVar raises at the point of use, which is how ``_current_axes()`` can
#: report the real mistake instead of an ``AttributeError`` further downstream.
_axes: contextvars.ContextVar[Axes] = contextvars.ContextVar("axes")


def _current_axes() -> Axes:
    """The axes of the enclosing ``create_graphs()`` block.

    Raises :class:`RuntimeError` naming the actual mistake if there is no such
    block, in one place rather than an ``assert axes is not None`` per caller.
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
    """Context manager that sets up a square matplotlib figure for the drawing
    helpers to plot into, and renders + displays it on exit.

    Yields the axes (also published for ``draw_*`` via a ``ContextVar``, so those
    helpers need no explicit axes argument). Nestable — nested blocks restore the
    enclosing axes rather than clobbering it.
    """
    fig: Figure
    axes: Axes
    fig, axes = plt.subplots(figsize=graph_bounds)
    token: contextvars.Token[Axes] = _axes.set(axes)
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
    display(fig)
    plt.close()

    return fig


def create_basis(
    fn: InvertibleFunction[Any] = _IDENTITY,
    graph_bounds: tuple[int, int] = (10, 10),
    gridline_interval: int = 1,
    xcolor: tuple[float, float, float] = (0.0, 0.0, 1.0),
    ycolor: tuple[float, float, float] = (1.0, 0.0, 1.0),
    cls: type[MultiVectorBase] = MultiVector,
) -> None:
    """Draw the coordinate grid as faint lines — its image under ``fn`` (identity
    by default), so a transform shows as a deformed grid.
    """
    # plot transformed basis
    vecs: list[MultiVectorBase]
    thickness: int
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
    fn: InvertibleFunction[Any] = _IDENTITY,
    cls: type[MultiVectorBase] = MultiVector,
) -> None:
    """Draw the unit circle — its image under ``fn`` (identity by default), so a
    transform shows as the circle deformed into its image (e.g. an ellipse).
    """
    ex: MultiVectorBase = cls.basis_vector(1)
    ey: MultiVectorBase = cls.basis_vector(2)

    def generate_circle() -> Generator[list[MultiVectorBase], None, None]:
        theta_increment: float = 0.01
        scale_radius: float = 1.0

        θ: float
        for θ in np.arange(0.0, 2 * math.pi, theta_increment):
            yield (
                [
                    scale_radius * (math.cos(θ) * ex + math.sin(θ) * ey),
                    scale_radius
                    * (
                        math.cos(θ + theta_increment) * ex
                        + math.sin(θ + theta_increment) * ey
                    ),
                ]
            )

    # plot transformed basis
    vecs: list[MultiVectorBase]
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
    fn: InvertibleFunction[Any] = _IDENTITY,
    xcolor: tuple[float, float, float] = (0.0, 0.0, 1.0),
    ycolor: tuple[float, float, float] = (1.0, 0.0, 1.0),
    cls: type[MultiVectorBase] = MultiVector,
) -> None:
    """Draw the x and y axes as coloured segments from the origin to e₁ and e₂ —
    their image under ``fn`` (identity by default), so a transform shows where the
    basis vectors land.
    """
    ex: MultiVectorBase = cls.basis_vector(1)
    ey: MultiVectorBase = cls.basis_vector(2)
    origin: MultiVectorBase = cls.zero()
    # x axis
    x_axis: list[MultiVectorBase] = [origin, ex]
    plt.plot(
        [float(_coord(fn(vec), (1,))) for vec in x_axis],
        [float(_coord(fn(vec), (2,))) for vec in x_axis],
        "-",
        lw=1.0,
        color=xcolor,
    )

    # y axis
    y_axis: list[MultiVectorBase] = [origin, ey]
    plt.plot(
        [float(_coord(fn(vec), (1,))) for vec in y_axis],
        [float(_coord(fn(vec), (2,))) for vec in y_axis],
        "-",
        lw=1.0,
        color=ycolor,
    )


def sine(v1: MultiVectorBase, v2: MultiVectorBase) -> Real:
    """The signed sine of the angle from ``v1`` to ``v2``, two vectors in the e₁e₂
    plane: the signed area of their parallelogram (the ``e₁₂`` coefficient of
    ``v1 ∧ v2``) over ``|v1| * |v2|``.  Positive when ``v2`` is a counterclockwise
    turn from ``v1``.  The sine companion to ``MultiVectorBase.cosine``; works for
    ``Gn`` and every representation, as long as both vectors lie in the e₁e₂ plane.

    Raises:
        ValueError: if ``v1`` or ``v2`` is not a vector, is the zero vector (the
            angle is undefined there, as for ``cosine``), or ``v1 ∧ v2`` has a part
            outside the e₁e₂ plane (a signed sine exists only in a plane).
    """
    MultiVectorBase.require_vectors([v1, v2])
    if v1 == type(v1).zero() or v2 == type(v2).zero():
        raise ValueError("sine (the angle) is undefined for the zero vector")
    cls: type[MultiVectorBase] = type(v1)
    e_12: MultiVectorBase = cls.basis_vector(1) ^ cls.basis_vector(2)
    wedge: MultiVectorBase = v1 ^ v2
    signed_area: Real = wedge.coefficient(e_12)
    if wedge != signed_area * e_12:
        raise ValueError(
            "sine: the vectors are not in the e_1 e_2 plane; a signed sine exists "
            "only in a plane"
        )
    return signed_area / (v1.magnitude() * v2.magnitude())


def _draw_labelled_triangle(
    vertex_coefficients: Sequence[tuple[float, float]],
    labels: Sequence[str],
    fn: InvertibleFunction[Any] = _IDENTITY,
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
    axes: Axes = _current_axes()
    ex: MultiVectorBase = cls.basis_vector(1)
    ey: MultiVectorBase = cls.basis_vector(2)
    origin: MultiVectorBase = cls.zero()
    x_prime_direction_world_space: MultiVectorBase = fn(ex) - fn(origin)
    x_world_space: MultiVectorBase = ex
    y_prime_direction_world_space: MultiVectorBase = fn(ey) - fn(origin)
    angle_radians: float = math.atan2(
        float(sine(x_world_space, x_prime_direction_world_space)),
        float(x_world_space.cosine(x_prime_direction_world_space)),
    )
    label_offset: MultiVectorBase = (
        0.0 * x_prime_direction_world_space + 0.20 * y_prime_direction_world_space
    )

    vertices: list[MultiVectorBase] = [
        fn(a * ex + b * ey) for a, b in vertex_coefficients
    ]

    triangle: Polygon = Polygon(
        list(map(_to_xy, vertices)),
        closed=True,
        facecolor="lightblue",
        edgecolor="black",
    )
    axes.add_patch(triangle)

    vertices_as_np: np.ndarray = np.array(list(map(_to_xy, vertices)))
    # Plot dots at the vertices
    axes.scatter(
        vertices_as_np[:, 0], vertices_as_np[:, 1], color="red", s=5, zorder=5
    )  # zorder ensures dots are on top

    # Label each vertex
    i: int
    label: str
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
    fn: InvertibleFunction[Any] = _IDENTITY,
    color: tuple[float, float, float] = (0.0, 0.0, 1.0),
    cls: type[MultiVectorBase] = MultiVector,
) -> None:
    """An isoceles triangle with vertices labelled A, B, C."""
    _draw_labelled_triangle(
        [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)], ["A", "B", "C"], fn, color, cls
    )


def draw_second_right_triangle(
    fn: InvertibleFunction[Any] = _IDENTITY,
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
    fn: InvertibleFunction[Any] = _IDENTITY,
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


def draw_ndc(
    fn: InvertibleFunction[Any] = _IDENTITY,
    color: tuple[float, float, float] = (0.0, 0.0, 1.0),
    cls: type[MultiVectorBase] = MultiVector,
) -> None:
    """Draw the normalized-device-coordinate square [−1, 1]² with labelled corners
    — its image under ``fn`` (identity by default).
    """
    axes: Axes = _current_axes()
    ex: MultiVectorBase = cls.basis_vector(1)
    ey: MultiVectorBase = cls.basis_vector(2)
    origin: MultiVectorBase = cls.zero()
    x_prime_direction_world_space: MultiVectorBase = fn(ex) - fn(origin)
    x_world_space: MultiVectorBase = ex
    y_prime_direction_world_space: MultiVectorBase = fn(ey) - fn(origin)
    angle_radians: float = math.atan2(
        float(sine(x_world_space, x_prime_direction_world_space)),
        float(x_world_space.cosine(x_prime_direction_world_space)),
    )
    label_offset: MultiVectorBase = (
        0.0 * x_prime_direction_world_space + 0.20 * y_prime_direction_world_space
    )

    vertices: list[MultiVectorBase] = [
        fn(v)
        for v in [
            (-1.0) * ex + (-1.0) * ey,
            (1.0) * ex + (-1.0) * ey,
            (1.0) * ex + (1.0) * ey,
            (-1.0) * ex + (1.0) * ey,
        ]
    ]

    square: Polygon = Polygon(
        list(map(_to_xy, vertices)),
        closed=True,
        fc="none",
        edgecolor="black",
    )
    axes.add_patch(square)

    vertices_as_np: np.ndarray = np.array(list(map(_to_xy, vertices)))
    # Plot dots at the vertices
    axes.scatter(
        vertices_as_np[:, 0], vertices_as_np[:, 1], color="red", s=5, zorder=5
    )  # zorder ensures dots are on top

    # Label each vertex
    labels: list[str] = ["(-1,-1)", "(1,-1)", "(1,1)", "(-1,1)"]
    i: int
    label: str
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
    fn: InvertibleFunction[Any] = _IDENTITY,
    color: tuple[float, float, float] = (0.0, 0.0, 1.0),
    cls: type[MultiVectorBase] = MultiVector,
) -> None:
    """Draw a ``width`` × ``height`` grid of pixel cells tiling the NDC square
    [−1, 1]² — their image under ``fn`` (identity by default), i.e. the screen
    raster and how a transform warps it.
    """
    axes: Axes = _current_axes()
    ex: MultiVectorBase = cls.basis_vector(1)
    ey: MultiVectorBase = cls.basis_vector(2)
    d_width: float = 2.0 / width
    d_height: float = 2.0 / height
    x: int
    y: int
    for x in range(width):
        for y in range(height):
            vertices: list[MultiVectorBase] = [
                fn(v)
                for v in [
                    (-1.0 + d_width * x) * ex + (-1.0 + d_height * y) * ey,
                    (-1.0 + d_width * (x + 1)) * ex + (-1.0 + d_height * y) * ey,
                    (-1.0 + d_width * (x + 1)) * ex + (-1.0 + d_height * (y + 1)) * ey,
                    (-1.0 + d_width * (x)) * ex + (-1.0 + d_height * (y + 1)) * ey,
                ]
            ]

            square: Polygon = Polygon(
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


def _coef_as_float(coef: Real) -> float | None:
    """``coef`` as a ``float``, or ``None`` when it is symbolic (not convertible)."""
    try:
        return float(coef)
    except TypeError, ValueError:
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

    Works on any ``MultiVectorBase`` representation (``Gn``, ``G``)
    via the ``to_blade_dict()`` interchange protocol.

    Each row is one basis blade (sorted by grade, then by index). Numeric
    coefficients appear as a dot at their value. Symbolic coefficients are
    placed at a small random x in ``[-symbolic_range, symbolic_range]`` (so
    rows don't all stack at zero); the latex of the symbol labels the dot.
    ``random_seed`` defaults to 0 for reproducibility — pass ``None`` for
    fresh randomness on every call.
    """
    blade_dict: Mapping[Blade, Real] = mv.to_blade_dict()
    blades: list[Blade] = sorted(blade_dict.keys(), key=lambda b: (len(b), b)) or [()]
    n: int = len(blades)

    rng: np.random.Generator = np.random.default_rng(random_seed)

    coefs: list[Real] = [blade_dict.get(b, 0) for b in blades]
    xs: list[float] = []
    for coef in coefs:
        x: float | None = _coef_as_float(coef)
        xs.append(
            x if x is not None else float(rng.uniform(-symbolic_range, symbolic_range))
        )

    xmin: float
    xmax: float
    if x_range is not None:
        xmin, xmax = x_range
    else:
        m: float = max(max(abs(x) for x in xs), 1.0)
        xmin, xmax = -1.2 * m, 1.2 * m

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=figsize or (8, max(2.0, 0.7 * n)))

    i: int
    blade: Blade
    coef: Real
    for i, (blade, coef, x) in enumerate(zip(blades, coefs, xs)):
        y: int = n - 1 - i  # top blade drawn first
        ax.axhline(y, xmin=0.0, xmax=1.0, color="gray", linewidth=0.5, alpha=0.6)
        ax.plot([0], [y], marker="|", color="black", markersize=14, zorder=2)

        is_numeric: bool = _coef_as_float(coef) is not None
        ax.plot(
            [x],
            [y],
            marker="o",
            color="C0" if is_numeric else "C1",
            markersize=10,
            zorder=3,
        )
        label: str = f"{x:g}" if is_numeric else "$" + sympy.latex(coef) + "$"
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
            "$" + blade_latex(blade) + "$",
            ha="right",
            va="center",
            fontsize=12,
        )

    ax.set_xlim(xmin - 0.20 * (xmax - xmin), xmax + 0.05 * (xmax - xmin))
    ax.set_ylim(-0.5, n - 0.5)
    ax.set_yticks([])
    side: str
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)

    ax.set_title(title if title is not None else mv._repr_latex_())

    plt.tight_layout()
    display(fig)
    plt.close(fig)
    return fig


#: One vector to draw: the vector, its label (LaTeX without the ``$``), and its colour.
LabelledVector = tuple[MultiVectorBase, str, str]


def _components(mv: MultiVectorBase, axes: Axes) -> np.ndarray:
    """``mv``'s vector coefficients as floats: e₁ to e₃ on 3-D axes, else e₁, e₂."""
    dimension: int = 3 if isinstance(axes, Axes3D) else 2
    return np.array([float(_coord(mv, (i,))) for i in range(1, dimension + 1)])


@contextlib.contextmanager
def create_graphs_3d(
    bound: float = 3.0,
    title: str | None = None,
    elevation: float = 30.0,
    azimuth: float = -60.0,
) -> Generator[Axes3D, None, Figure]:
    """The 3-D twin of ``create_graphs``: a cube of axes from ``-bound`` to ``bound``.

    ``draw_vectors``, ``draw_bivector`` and ``draw_angle`` inside the block draw in
    3-D. The figure is rendered and displayed on exit.

    Args:
        bound: the half-width of each axis.
        title: the figure's title, if any.
        elevation: the camera's angle above the e₁e₂ plane, in degrees.
        azimuth: the camera's angle around the e₃ axis, in degrees.

    Yields:
        Axes3D: the 3-D axes.
    """
    fig: Figure = plt.figure(figsize=(6, 6))
    axes: Axes3D = Axes3D(fig)
    fig.add_axes(axes)
    token: contextvars.Token[Axes] = _axes.set(axes)
    axes.set_xlim((-bound, bound))
    axes.set_ylim((-bound, bound))
    axes.set_zlim((-bound, bound))
    axes.set_box_aspect((1, 1, 1))
    axes.view_init(elev=elevation, azim=azimuth)
    axes.set_xlabel("$\\vec{\\mathbf{e}}_1$")
    axes.set_ylabel("$\\vec{\\mathbf{e}}_2$")
    axes.set_zlabel("$\\vec{\\mathbf{e}}_3$")
    if title is not None:
        axes.set_title(title)
    try:
        yield axes
    finally:
        _axes.reset(token)
    fig.canvas.draw()
    display(fig)
    plt.close(fig)
    return fig


def _label(axes: Axes, at: np.ndarray, text: str, color: str) -> None:
    """Write ``text`` (LaTeX without the ``$``) at the point ``at``, in ``color``."""
    match axes:
        case Axes3D():
            axes.text(
                x=float(at[0]),
                y=float(at[1]),
                z=float(at[2]),
                s=f"${text}$",
                color=color,
                fontsize=12,
            )
        case _:
            axes.annotate(
                f"${text}$",
                xy=(float(at[0]), float(at[1])),
                xytext=(6, 6),
                textcoords="offset points",
                color=color,
                fontsize=12,
            )


def _arrow(
    axes: Axes,
    tail: np.ndarray,
    head: np.ndarray,
    color: str,
    width: float,
    head_ratio: float = 0.1,
) -> None:
    """Draw an arrow from ``tail`` to ``head``.

    ``head_ratio`` is the 3-D arrowhead's length as a fraction of the arrow's (2-D
    arrowheads have a fixed size).
    """
    match axes:
        case Axes3D():
            axes.quiver(
                *tail,
                *(head - tail),
                color=color,
                linewidth=width,
                arrow_length_ratio=head_ratio,
            )
        case _:
            axes.annotate(
                "",
                xy=(float(head[0]), float(head[1])),
                xytext=(float(tail[0]), float(tail[1])),
                arrowprops={"arrowstyle": "-|>", "color": color, "lw": width},
            )


def draw_vectors(vectors: Sequence[LabelledVector]) -> None:
    """Draw each vector as an arrow from the origin, labelled at its tip.

    Works inside ``create_graphs`` (2-D, the e₁ and e₂ coefficients) and
    ``create_graphs_3d`` (3-D, e₁ to e₃). The coefficients must be numbers.

    Args:
        vectors: ``(vector, label, colour)`` triples; the label is LaTeX without
            the ``$``, and is drawn in the vector's colour.
    """
    axes: Axes = _current_axes()
    vector: MultiVectorBase
    label: str
    color: str
    for vector, label, color in vectors:
        tip: np.ndarray = _components(vector, axes)
        _arrow(axes, tail=np.zeros_like(tip), head=tip, color=color, width=2.0)
        _label(axes, at=tip, text=label, color=color)


def draw_angle(
    from_vector: MultiVectorBase,
    to_vector: MultiVectorBase,
    color: str = "black",
    radius: float | None = None,
) -> None:
    """Draw the arc that turns ``from_vector`` toward ``to_vector``, with an arrowhead.

    The arc lies in the plane of the two vectors and sweeps the angle between them
    (less than a half turn), so it shows which way the plane is oriented. The
    vectors must not be parallel.

    Args:
        from_vector: where the arc starts.
        to_vector: the direction the arc turns toward.
        color: the arc's colour.
        radius: the arc's radius; by default a third of the shorter vector.
    """
    axes: Axes = _current_axes()
    a: np.ndarray = _components(from_vector, axes)
    b: np.ndarray = _components(to_vector, axes)
    a_hat: np.ndarray = a / np.linalg.norm(a)
    # the unit vector in the plane that is perpendicular to a, on b's side
    b_perp: np.ndarray = b - np.dot(b, a_hat) * a_hat
    b_perp_hat: np.ndarray = b_perp / np.linalg.norm(b_perp)
    θ: float = math.atan2(float(np.dot(b, b_perp_hat)), float(np.dot(b, a_hat)))
    r: float = (
        radius
        if radius is not None
        else min(float(np.linalg.norm(a)), float(np.linalg.norm(b))) / 3
    )
    t: np.ndarray = np.linspace(0.0, θ, 40)
    arc: np.ndarray = r * (np.outer(np.cos(t), a_hat) + np.outer(np.sin(t), b_perp_hat))
    axes.plot(*arc.T, color=color, linewidth=1.5)
    _arrow(axes, tail=arc[-4], head=arc[-1], color=color, width=1.5, head_ratio=1.0)


def draw_bivector(
    a: MultiVectorBase,
    b: MultiVectorBase,
    label: str,
    color: str = "tab:green",
) -> None:
    """Draw the bivector ``a ∧ b`` as the oriented parallelogram ``a`` and ``b`` span.

    The shaded parallelogram is the bivector's plane and its area, ``|a ∧ b|``; the
    arc from ``a`` toward ``b`` (``draw_angle``) shows its orientation. Works inside
    ``create_graphs`` and ``create_graphs_3d``.

    Args:
        a: the first side; the orientation arc starts here.
        b: the second side.
        label: LaTeX without the ``$``, drawn at the parallelogram's centre.
        color: the fill and label colour.
    """
    axes: Axes = _current_axes()
    p: np.ndarray = _components(a, axes)
    q: np.ndarray = _components(b, axes)
    corners: np.ndarray = np.array([np.zeros_like(p), p, p + q, q])
    match axes:
        case Axes3D():
            axes.add_collection3d(
                Poly3DCollection([corners], alpha=0.3, facecolor=color, edgecolor=color)
            )
        case _:
            axes.add_patch(
                Polygon(
                    corners, closed=True, alpha=0.3, facecolor=color, edgecolor=color
                )
            )
    centre: np.ndarray = (p + q) / 2
    match axes:
        case Axes3D():
            _label(axes, at=centre, text=label, color=color)
        case _:
            axes.annotate(
                f"${label}$",
                xy=(float(centre[0]), float(centre[1])),
                ha="center",
                va="center",
                color=color,
                fontsize=12,
            )
    draw_angle(from_vector=a, to_vector=b, color=color)
