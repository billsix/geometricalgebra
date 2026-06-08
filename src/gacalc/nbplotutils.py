# Copyright (c) 2018-2026 William Emerison Six
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.


import contextlib
import itertools
import math
import numbers
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
from matplotlib.patches import Polygon
from matplotlib_inline.backend_inline import set_matplotlib_formats

from gacalc.base import AbstractMultiVector, BladeCoef
from gacalc.gn import (
    MultiVector,
    identity,
)

# The inline SVG backend is only meaningful inside an IPython/Jupyter session;
# guarding it lets this module import headless (under pytest, or a plain script)
# instead of raising when there is no shell to enable a GUI for.
if get_ipython() is not None:
    set_matplotlib_formats("svg")

_IDENTITY = identity()

extraLinesMultiplier = 3


def generategridlines(
    graphBounds, interval=1, cls: type[AbstractMultiVector] = MultiVector
):
    ex = cls.basis_vector(1)
    ey = cls.basis_vector(2)
    for x in range(
        -graphBounds[0] * extraLinesMultiplier,
        graphBounds[0] * extraLinesMultiplier,
        interval,
    ):
        thickness = 4 if np.isclose(x, 0.0) else 1
        yield (
            [
                x * ex + (-graphBounds[1] * extraLinesMultiplier) * ey,
                x * ex + (graphBounds[1] * extraLinesMultiplier) * ey,
            ],
            thickness,
        )

    for y in range(
        -graphBounds[1] * extraLinesMultiplier,
        graphBounds[1] * extraLinesMultiplier,
        interval,
    ):
        thickness = 4 if np.isclose(y, 0.0) else 1
        yield (
            [
                (-graphBounds[0] * extraLinesMultiplier) * ex + y * ey,
                (graphBounds[0] * extraLinesMultiplier) * ex + y * ey,
            ],
            thickness,
        )


axes: Axes | None = None


@contextlib.contextmanager
def create_graphs(graph_bounds=(3, 3), title=None, filename=None):
    global axes
    fig, axes = plt.subplots(figsize=graph_bounds)
    axes.set_xlim((-graph_bounds[0], graph_bounds[0]))
    axes.set_ylim((-graph_bounds[1], graph_bounds[1]))

    plt.tight_layout()

    yield axes

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
    fn=_IDENTITY,
    graph_bounds=(10, 10),
    gridline_interval=1,
    xcolor=(0.0, 0.0, 1.0),
    ycolor=(1.0, 0.0, 1.0),
    cls: type[AbstractMultiVector] = MultiVector,
):
    ex = cls.basis_vector(1)
    ey = cls.basis_vector(2)
    # plot transformed basis
    for vecs, thickness in generategridlines(
        graph_bounds, interval=gridline_interval, cls=cls
    ):
        plt.plot(
            [float(fn(vec).component(ex)) for vec in vecs],
            [float(fn(vec).component(ey)) for vec in vecs],
            "-",
            lw=thickness,
            color=(0.1, 0.2, 0.5),
            alpha=0.3,
        )


def create_unit_circle(
    fn=_IDENTITY,
    cls: type[AbstractMultiVector] = MultiVector,
):
    ex = cls.basis_vector(1)
    ey = cls.basis_vector(2)

    def generate_circle():
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
            [float(fn(vec).component(ex)) for vec in vecs],
            [float(fn(vec).component(ey)) for vec in vecs],
            "-",
            lw=1,
            color=(0.0, 0.0, 0.0),
            alpha=0.5,
        )


def create_x_and_y(
    fn=_IDENTITY,
    xcolor=(0.0, 0.0, 1.0),
    ycolor=(1.0, 0.0, 1.0),
    cls: type[AbstractMultiVector] = MultiVector,
):
    ex = cls.basis_vector(1)
    ey = cls.basis_vector(2)
    origin = cls.zero()
    # x axis
    x_axis = [origin, ex]
    plt.plot(
        [float(fn(vec).component(ex)) for vec in x_axis],
        [float(fn(vec).component(ey)) for vec in x_axis],
        "-",
        lw=1.0,
        color=xcolor,
    )

    # y axis
    y_axis = [origin, ey]
    plt.plot(
        [float(fn(vec).component(ex)) for vec in y_axis],
        [float(fn(vec).component(ey)) for vec in y_axis],
        "-",
        lw=1.0,
        color=ycolor,
    )


def cosine(v1: AbstractMultiVector, v2: AbstractMultiVector) -> numbers.Real:
    return (v1.dot(v2) * (abs(v1 * v2) ** (-1))).scalar_part()


def sine(v1: AbstractMultiVector, v2: AbstractMultiVector) -> numbers.Real:
    # rotate v1 by 90 degrees in the e_1 e_2 plane (v1 * e_1 e_2), then project on v2
    rot90: AbstractMultiVector = v1 * type(v1).from_blade_dict({(1, 2): 1})
    return (rot90.dot(v2) * (abs(v1 * v2) ** (-1))).scalar_part()


def draw_isoceles_triangle(
    fn=_IDENTITY,
    color=(0.0, 0.0, 1.0),
    cls: type[AbstractMultiVector] = MultiVector,
):
    assert axes is not None, "call inside a create_graphs() block"
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
            origin,
            ex,
            0.5 * ex + ey,
        ]
    ]

    triangle = Polygon(
        list(map(lambda mv: [mv.component(ex), mv.component(ey)], vertices)),
        closed=True,
        facecolor="lightblue",
        edgecolor="black",
    )
    axes.add_patch(triangle)

    vertices_as_np = np.array(
        list(map(lambda mv: [mv.component(ex), mv.component(ey)], vertices))
    )
    # Plot dots at the vertices
    axes.scatter(
        vertices_as_np[:, 0], vertices_as_np[:, 1], color="red", s=5, zorder=5
    )  # zorder ensures dots are on top

    # Label each vertex
    labels = ["A", "B", "C"]
    for i, label in enumerate(labels):
        # Use plt.annotate to place the label near the point
        plt.annotate(
            label,
            xy=(vertices_as_np[i, 0], vertices_as_np[i, 1]),
            xytext=(
                vertices_as_np[i, 0] + label_offset.component(ex),
                vertices_as_np[i, 1] + label_offset.component(ey),
            ),
            rotation=math.degrees(angle_radians),
            rotation_mode="anchor",
            zorder=6,
        )


#         # Annotate with a 45-degree rotation
# ax.annotate('Rotated Annotation', xy=(0.5, 0.5), xytext=(0.7, 0.3),
#             arrowprops=dict(facecolor='black', shrink=0.05),
#             rotation=45)


def draw_second_right_triangle(
    fn=_IDENTITY,
    color=(0.0, 0.0, 1.0),
    cls: type[AbstractMultiVector] = MultiVector,
):
    assert axes is not None, "call inside a create_graphs() block"
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
            origin,
            (0) * ex + (3.0) * ey,
            (-4.0) * ex + (3.0) * ey,
        ]
    ]

    triangle = Polygon(
        list(map(lambda mv: [mv.component(ex), mv.component(ey)], vertices)),
        closed=True,
        facecolor="lightblue",
        edgecolor="black",
    )
    axes.add_patch(triangle)

    vertices_as_np = np.array(
        list(map(lambda mv: [mv.component(ex), mv.component(ey)], vertices))
    )
    # Plot dots at the vertices
    axes.scatter(
        vertices_as_np[:, 0], vertices_as_np[:, 1], color="red", s=5, zorder=5
    )  # zorder ensures dots are on top

    # Label each vertex
    labels = ["(0,0)", "(0,3)", "(-4,3)"]
    for i, label in enumerate(labels):
        # Use plt.annotate to place the label near the point
        plt.annotate(
            label,
            xy=(vertices_as_np[i, 0], vertices_as_np[i, 1]),
            xytext=(
                vertices_as_np[i, 0] - label_offset.component(ex),
                vertices_as_np[i, 1] + label_offset.component(ey),
            ),
            rotation=math.degrees(angle_radians),
            rotation_mode="anchor",
            zorder=6,
        )


def draw_right_triangle(
    fn=_IDENTITY,
    color=(0.0, 0.0, 1.0),
    cls: type[AbstractMultiVector] = MultiVector,
):
    assert axes is not None, "call inside a create_graphs() block"
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
            origin,
            (3.0) * ex + (0.0) * ey,
            (3.0) * ex + (4.0) * ey,
        ]
    ]

    triangle = Polygon(
        list(map(lambda mv: [mv.component(ex), mv.component(ey)], vertices)),
        closed=True,
        facecolor="lightblue",
        edgecolor="black",
    )
    axes.add_patch(triangle)

    vertices_as_np = np.array(
        list(map(lambda mv: [mv.component(ex), mv.component(ey)], vertices))
    )
    # Plot dots at the vertices
    axes.scatter(
        vertices_as_np[:, 0], vertices_as_np[:, 1], color="red", s=5, zorder=5
    )  # zorder ensures dots are on top

    # Label each vertex
    labels = ["(0,0)", "(3,0)", "(3,4)"]
    for i, label in enumerate(labels):
        # Use plt.annotate to place the label near the point
        plt.annotate(
            label,
            xy=(vertices_as_np[i, 0], vertices_as_np[i, 1]),
            xytext=(
                vertices_as_np[i, 0] + label_offset.component(ex),
                vertices_as_np[i, 1] + label_offset.component(ey),
            ),
            rotation=math.degrees(angle_radians),
            rotation_mode="anchor",
            zorder=6,
        )


def draw_ndc(
    fn=_IDENTITY,
    color=(0.0, 0.0, 1.0),
    cls: type[AbstractMultiVector] = MultiVector,
):
    assert axes is not None, "call inside a create_graphs() block"
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
        list(map(lambda mv: [mv.component(ex), mv.component(ey)], vertices)),
        closed=True,
        fc="none",
        edgecolor="black",
    )
    axes.add_patch(square)

    vertices_as_np = np.array(
        list(map(lambda mv: [mv.component(ex), mv.component(ey)], vertices))
    )
    # Plot dots at the vertices
    axes.scatter(
        vertices_as_np[:, 0], vertices_as_np[:, 1], color="red", s=5, zorder=5
    )  # zorder ensures dots are on top

    # Label each vertex
    labels = ["(-1,-1)", "(-1,1)", "(1,1)", "(-1,1)"]
    for i, label in enumerate(labels):
        # Use plt.annotate to place the label near the point
        plt.annotate(
            label,
            xy=(vertices_as_np[i, 0], vertices_as_np[i, 1]),
            xytext=(
                vertices_as_np[i, 0] + label_offset.component(ex),
                vertices_as_np[i, 1] + label_offset.component(ey),
            ),
            rotation=math.degrees(angle_radians),
            rotation_mode="anchor",
            zorder=6,
        )


def draw_screen(
    width,
    height,
    fn=_IDENTITY,
    color=(0.0, 0.0, 1.0),
    cls: type[AbstractMultiVector] = MultiVector,
):
    assert axes is not None, "call inside a create_graphs() block"
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
                        lambda mv: [mv.component(ex), mv.component(ey)],
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


def _coef_as_float(coef) -> float | None:
    try:
        return float(coef)
    except (TypeError, ValueError):
        return None


def plot_multivector(
    mv: AbstractMultiVector,
    x_range: tuple[float, float] | None = None,
    title: str | None = None,
    figsize: tuple[float, float] | None = None,
    symbolic_range: float = 0.8,
    random_seed: int | None = 0,
):
    """Plot each blade of ``mv`` on its own horizontal number line, stacked vertically.

    Works on any ``AbstractMultiVector`` representation (``Gn``, ``G1``/``G2``/``G3``)
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


def _blade_terms(mv: AbstractMultiVector) -> list:
    """The single-blade multivectors that sum to ``mv`` (its product-table terms).

    ``__iter__`` now yields a multivector's coefficient *values*, so the
    component-by-component product breakdown decomposes via ``to_blade_dict``.
    """
    return [
        type(mv).from_blade_dict({blade: coef})
        for blade, coef in mv.to_blade_dict().items()
    ]


def show_mult(a: AbstractMultiVector, b: AbstractMultiVector):
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
        lambda x: x._repr_latex_() if hasattr(x, "_repr_latex_") else x
    )
    display(Markdown(df_latex.to_markdown(index=False)))
    display(Markdown("**Summing all the products up, we get**"))
    display(Math("$" + (a * b)._repr_latex_() + "$"))
