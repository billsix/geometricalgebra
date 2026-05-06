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
from IPython.display import Markdown, Math, display
from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Polygon
from matplotlib_inline.backend_inline import set_matplotlib_formats

from geometricalgebra.multivector import (
    MultiVector,
    e_1,
    e_2,
    identity,
    one,
    rotate_90_degrees,
    zero,
)

set_matplotlib_formats("svg")

_IDENTITY = identity()

extraLinesMultiplier = 3


def generategridlines(graphBounds, interval=1):
    for x in range(
        -graphBounds[0] * extraLinesMultiplier,
        graphBounds[0] * extraLinesMultiplier,
        interval,
    ):
        thickness = 4 if np.isclose(x, 0.0) else 1
        yield (
            [
                x * e_1 + (-graphBounds[1] * extraLinesMultiplier) * e_2,
                x * e_1 + (graphBounds[1] * extraLinesMultiplier) * e_2,
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
                (-graphBounds[0] * extraLinesMultiplier) * e_1 + y * e_2,
                (graphBounds[0] * extraLinesMultiplier) * e_1 + y * e_2,
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
):
    # plot transformed basis
    for vecs, thickness in generategridlines(graph_bounds, interval=gridline_interval):
        plt.plot(
            [float(fn(vec).component(e_1)) for vec in vecs],
            [float(fn(vec).component(e_2)) for vec in vecs],
            "-",
            lw=thickness,
            color=(0.1, 0.2, 0.5),
            alpha=0.3,
        )


def create_unit_circle(
    fn=_IDENTITY,
):
    def generate_circle():
        theta_increment: float = 0.01
        scale_radius: float = 1.0

        for theta in np.arange(0.0, 2 * math.pi, theta_increment):
            yield (
                [
                    scale_radius * (math.cos(theta) * e_1 + math.sin(theta) * e_2),
                    scale_radius
                    * (
                        math.cos(theta + theta_increment) * e_1
                        + math.sin(theta + theta_increment) * e_2
                    ),
                ]
            )

    # plot transformed basis
    for vecs in generate_circle():
        plt.plot(
            [float(fn(vec).component(e_1)) for vec in vecs],
            [float(fn(vec).component(e_2)) for vec in vecs],
            "-",
            lw=1,
            color=(0.0, 0.0, 0.0),
            alpha=0.5,
        )


def create_x_and_y(
    fn=_IDENTITY,
    xcolor=(0.0, 0.0, 1.0),
    ycolor=(1.0, 0.0, 1.0),
):
    # x axis
    x_axis = [zero, e_1]
    plt.plot(
        [float(fn(vec).component(e_1)) for vec in x_axis],
        [float(fn(vec).component(e_2)) for vec in x_axis],
        "-",
        lw=1.0,
        color=xcolor,
    )

    # y axis
    y_axis = [zero, e_2]
    plt.plot(
        [float(fn(vec).component(e_1)) for vec in y_axis],
        [float(fn(vec).component(e_2)) for vec in y_axis],
        "-",
        lw=1.0,
        color=ycolor,
    )


def cosine(v1: MultiVector, v2: MultiVector) -> numbers.Real:
    return (v1.dot(v2) * (abs(v1 * v2) ** (-1))).scalar_part()


def sine(v1: MultiVector, v2: MultiVector) -> numbers.Real:
    return (rotate_90_degrees()(v1).dot(v2) * (abs(v1 * v2) ** (-1))).scalar_part()


def draw_isoceles_triangle(
    fn=_IDENTITY,
    color=(0.0, 0.0, 1.0),
):
    assert axes is not None, "call inside a create_graphs() block"
    x_prime_direction_world_space = fn(e_1) - fn(zero)
    x_world_space = e_1
    y_prime_direction_world_space = fn(e_2) - fn(zero)
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
            zero,
            e_1,
            0.5 * e_1 + e_2,
        ]
    ]

    triangle = Polygon(
        list(map(lambda mv: [mv.component(e_1), mv.component(e_2)], vertices)),
        closed=True,
        facecolor="lightblue",
        edgecolor="black",
    )
    axes.add_patch(triangle)

    vertices_as_np = np.array(
        list(map(lambda mv: [mv.component(e_1), mv.component(e_2)], vertices))
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
                vertices_as_np[i, 0] + label_offset.component(e_1),
                vertices_as_np[i, 1] + label_offset.component(e_2),
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
):
    assert axes is not None, "call inside a create_graphs() block"
    x_prime_direction_world_space = fn(e_1) - fn(zero)
    x_world_space = e_1
    y_prime_direction_world_space = fn(e_2) - fn(zero)
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
            zero,
            (0) * e_1 + (3.0) * e_2,
            (-4.0) * e_1 + (3.0) * e_2,
        ]
    ]

    triangle = Polygon(
        list(map(lambda mv: [mv.component(e_1), mv.component(e_2)], vertices)),
        closed=True,
        facecolor="lightblue",
        edgecolor="black",
    )
    axes.add_patch(triangle)

    vertices_as_np = np.array(
        list(map(lambda mv: [mv.component(e_1), mv.component(e_2)], vertices))
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
                vertices_as_np[i, 0] - label_offset.component(e_1),
                vertices_as_np[i, 1] + label_offset.component(e_2),
            ),
            rotation=math.degrees(angle_radians),
            rotation_mode="anchor",
            zorder=6,
        )


def draw_right_triangle(
    fn=_IDENTITY,
    color=(0.0, 0.0, 1.0),
):
    assert axes is not None, "call inside a create_graphs() block"
    x_prime_direction_world_space = fn(e_1) - fn(zero)
    x_world_space = e_1
    y_prime_direction_world_space = fn(e_2) - fn(zero)
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
            zero,
            (3.0) * e_1 + (0.0) * e_2,
            (3.0) * e_1 + (4.0) * e_2,
        ]
    ]

    triangle = Polygon(
        list(map(lambda mv: [mv.component(e_1), mv.component(e_2)], vertices)),
        closed=True,
        facecolor="lightblue",
        edgecolor="black",
    )
    axes.add_patch(triangle)

    vertices_as_np = np.array(
        list(map(lambda mv: [mv.component(e_1), mv.component(e_2)], vertices))
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
                vertices_as_np[i, 0] + label_offset.component(e_1),
                vertices_as_np[i, 1] + label_offset.component(e_2),
            ),
            rotation=math.degrees(angle_radians),
            rotation_mode="anchor",
            zorder=6,
        )


def draw_ndc(
    fn=_IDENTITY,
    color=(0.0, 0.0, 1.0),
):
    assert axes is not None, "call inside a create_graphs() block"
    x_prime_direction_world_space = fn(e_1) - fn(zero)
    x_world_space = e_1
    y_prime_direction_world_space = fn(e_2) - fn(zero)
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
            (-1.0) * e_1 + (-1.0) * e_2,
            (1.0) * e_1 + (-1.0) * e_2,
            (1.0) * e_1,
            +(1.0) * e_2,
            (-1.0) * e_1 + (1.0) * e_2,
        ]
    ]

    square = Polygon(
        list(map(lambda mv: [mv.component(e_1), mv.component(e_2)], vertices)),
        closed=True,
        fc="none",
        edgecolor="black",
    )
    axes.add_patch(square)

    vertices_as_np = np.array(
        list(map(lambda mv: [mv.component(e_1), mv.component(e_2)], vertices))
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
                vertices_as_np[i, 0] + label_offset.component(e_1),
                vertices_as_np[i, 1] + label_offset.component(e_2),
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
):
    assert axes is not None, "call inside a create_graphs() block"
    d_width = 2.0 / width
    d_height = 2.0 / height
    for x in range(width):
        for y in range(height):
            vertices = [
                fn(v)
                for v in [
                    (-1.0 + d_width * x) * e_1 + (-1.0 + d_height * y) * e_2,
                    (-1.0 + d_width * (x + 1)) * e_1 + (-1.0 + d_height * y) * e_2,
                    (-1.0 + d_width * (x + 1)) * e_1
                    + (-1.0 + d_height * (y + 1)) * e_2,
                    (-1.0 + d_width * (x)) * e_1 + (-1.0 + d_height * (y + 1)) * e_2,
                ]
            ]

            square = Polygon(
                list(
                    map(
                        lambda mv: [mv.component(e_1), mv.component(e_2)],
                        vertices,
                    )
                ),
                closed=True,
                fc="none",
                edgecolor="black",
            )
            axes.add_patch(square)


def show_mult(a: MultiVector, b: MultiVector):
    display(Markdown("**We want to evaluate**"))
    # print the values as latex before they are multiplied
    display(Math("$($" + a._repr_latex_() + "$)*($" + b._repr_latex_() + "$)$"))
    display(Markdown("**Multivector Multiplication is distributive over additon**"))

    data: list = list(itertools.product(a, b))
    result = [
        (left, "*", right, "=", math.prod((left, right), start=one))
        for left, right in data
    ]
    df = pd.DataFrame(
        result,
        columns=pd.Index(["Left Component", "*", "Right Component", "=", "Product"]),
    )
    # Convert to markdown string and display
    df_latex = df.map(lambda x: x._repr_latex_() if hasattr(x, "_repr_latex_") else x)
    display(Markdown(df_latex.to_markdown(index=False)))
    display(Markdown("**Summing all the products up, we get**"))
    display(Math("$" + (a * b)._repr_latex_() + "$"))
