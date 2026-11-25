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

"""3D graphing calculator -- plot authored ``f(x, y)`` functions as surfaces.

:func:`run` opens a window and plots one of a list of first-class Python
surfaces -- authored in the caller's source -- as a height field over the x-z
ground plane (the function value is the up/y coordinate), shown as a wireframe
and/or a height-coloured solid mesh.  The imgui Controls menu sets the grid
sampling steps **dx** and **dy** (live rebuild) and toggles wireframe/solid;
the Surface menu picks which function; an orbit camera (left-drag / arrows /
scroll) looks around it.  The solid mesh is lit per fragment with the
Blinn-Phong half-vector model (one directional light, set from the Light menu),
or, with the lighting switched off, shaded by height alone.  The normals are
analytic: the cross product of the surface's two tangents, built from the
partial derivatives that sympy takes of ``fn`` at runtime (central differences
stand in when ``fn`` cannot be called on sympy symbols).

The window, imgui and GL context, the orbit camera, the menubar helpers and the
frame steps come from :mod:`gacalc.gl.cayley_gl`; the line and per-vertex-colour
pipelines and the VAO/VBO builders from :mod:`gacalc.gl._pipeline`; the
perspective view from :mod:`gacalc.gl.matrix_stack` (via ``setup_orbit_view``).

The geometry builders are plain numpy and need no GL context; only :func:`run`
opens a window.
"""

import dataclasses
import math
import types
import typing

import glfw
import numpy as np
import OpenGL.GL as GL
import sympy

import gacalc.gl.matrix_stack as ms
from gacalc import g2, g3
from gacalc.base import Real
from gacalc.gl import SHADER_DIR, cayley_gl
from gacalc.gl import _pipeline as _p
from gacalc.gl import labels as _labels

if typing.TYPE_CHECKING:
    from glfw import _GLFWwindowPointerT

    GLFWWindow: typing.TypeAlias = _GLFWwindowPointerT


imgui: types.ModuleType = cayley_gl.imgui

#: An RGB colour in 0..1.
Color: typing.TypeAlias = tuple[float, float, float]


@dataclasses.dataclass(frozen=True)
class Surface:
    """One graphed surface: f(x, y), a label, a colour, and the LaTeX (authored
    in source) that the billboard renderer typesets as its equation caption.

    ``fn`` takes plain numbers.  If it also accepts sympy symbols (no ``float``
    casts), the lit surface's normals come from its exact derivatives."""

    fn: typing.Callable[[Real, Real], Real]
    label: str
    color: Color
    latex: str


DOMAIN_HALF: float = 6.0  # surfaces span [-6, 6] x [-6, 6]
AXIS_LENGTH: float = 7.0
TICK_LENGTH: float = 0.12
AXIS_COLOR: Color = (0.6, 0.6, 0.72)


@dataclasses.dataclass
class View3D:
    """Which surface is shown, the sampling steps, and the draw modes."""

    current: int = 0
    dx: float = 0.5
    dy: float = 0.5
    show_wireframe: bool = True
    show_solid: bool = False  # start as a bare wireframe mesh; solid is opt-in
    show_labels: bool = True
    lit: bool = True  # Blinn-Phong lighting on the solid; off = height colours
    light_azimuth: float = 45.0  # degrees around the up axis, from +z toward +x
    light_elevation: float = 45.0  # degrees above the ground plane
    shininess: float = 64.0  # the specular exponent


@dataclasses.dataclass
class SurfaceMeshes:
    """The rebuildable wireframe + solid meshes for the current surface."""

    wire_vao: int
    wire_vbo: int
    wire_count: int
    solid_vao: int
    solid_pos_vbo: int
    solid_color_vbo: int
    solid_count: int
    lit_vao: int
    solid_normal_vbo: int


# ---------------------------------------------------------------------------
# Height-field geometry.  Domain x -> world x, domain y -> world z (ground
# plane), height f(x, y) -> world y (up).
# ---------------------------------------------------------------------------


def _axis_count(step: float) -> int:
    return max(1, int(round((2.0 * DOMAIN_HALF) / step)))


def _height_color(base: Color, t: float) -> list[float]:
    """Shade ``base`` by normalised height ``t`` in 0..1 (dark low, bright
    high) so the solid surface reads without any lighting."""
    scale: float = 0.3 + 0.7 * t
    return [base[0] * scale, base[1] * scale, base[2] * scale]


def _triangle_corners(i: int, j: int) -> list[tuple[int, int]]:
    """The grid indices of cell ``(i, j)``'s two triangles, three corners each
    (counter-clockwise seen from above), in the order the solid mesh emits them.

    >>> _triangle_corners(0, 0)
    [(0, 0), (1, 0), (1, 1), (0, 0), (1, 1), (0, 1)]
    """
    return [(i, j), (i + 1, j), (i + 1, j + 1), (i, j), (i + 1, j + 1), (i, j + 1)]


def build_wireframe(surface: Surface, dx: float, dy: float) -> np.ndarray:
    """Grid lines of the height field as GL_LINES (both grid directions).

    A step of 6 gives a 2 x 2 grid of cells: 3 lines of 2 segments in each
    direction, two vertices per segment:

    >>> white: Color = (1.0, 1.0, 1.0)
    >>> flat: Surface = (
    ...     Surface(fn=lambda x, y: 0.0, label="flat", color=white, latex="0")
    ... )
    >>> build_wireframe(flat, 6.0, 6.0).reshape(-1, 3).shape
    (24, 3)
    """
    nx: int = _axis_count(dx)
    ny: int = _axis_count(dy)
    verts: list[float] = []

    def height(i: int, j: int) -> tuple[float, float, float]:
        x: float = -DOMAIN_HALF + i * (2.0 * DOMAIN_HALF) / nx
        z: float = -DOMAIN_HALF + j * (2.0 * DOMAIN_HALF) / ny
        return x, float(surface.fn(x, z)), z

    i: int
    j: int
    x0: float
    y0: float
    z0: float
    x1: float
    y1: float
    z1: float
    for j in range(ny + 1):
        for i in range(nx):
            x0, y0, z0 = height(i, j)
            x1, y1, z1 = height(i + 1, j)
            verts.extend([x0, y0, z0, x1, y1, z1])
    for i in range(nx + 1):
        for j in range(ny):
            x0, y0, z0 = height(i, j)
            x1, y1, z1 = height(i, j + 1)
            verts.extend([x0, y0, z0, x1, y1, z1])
    return np.array(verts, dtype=np.float32)


def build_solid(
    surface: Surface, dx: float, dy: float
) -> tuple[np.ndarray, np.ndarray]:
    """Two triangles per cell (GL_TRIANGLES) plus a per-vertex colour that
    shades by height.  Returns (positions, colours).

    A step of 6 gives 4 cells, so 8 triangles of 3 vertices, each with a colour:

    >>> white: Color = (1.0, 1.0, 1.0)
    >>> tilt: Surface = Surface(fn=lambda x, y: x, label="tilt", color=white, latex="x")
    >>> positions: np.ndarray
    >>> colors: np.ndarray
    >>> positions, colors = build_solid(tilt, 6.0, 6.0)
    >>> positions.reshape(-1, 3).shape, colors.reshape(-1, 3).shape
    ((24, 3), (24, 3))
    """
    nx: int = _axis_count(dx)
    ny: int = _axis_count(dy)
    grid: list[list[tuple[float, float, float]]] = []
    lo: float = math.inf
    hi: float = -math.inf
    i: int
    j: int
    for i in range(nx + 1):
        row: list[tuple[float, float, float]] = []
        for j in range(ny + 1):
            x: float = -DOMAIN_HALF + i * (2.0 * DOMAIN_HALF) / nx
            z: float = -DOMAIN_HALF + j * (2.0 * DOMAIN_HALF) / ny
            y: float = float(surface.fn(x, z))
            lo = min(lo, y)
            hi = max(hi, y)
            row.append((x, y, z))
        grid.append(row)
    span: float = hi - lo if hi > lo else 1.0

    positions: list[float] = []
    colors: list[float] = []

    def emit(p: tuple[float, float, float]) -> None:
        positions.extend([p[0], p[1], p[2]])
        colors.extend(_height_color(surface.color, (p[1] - lo) / span))

    for i in range(nx):
        for j in range(ny):
            corner_i: int
            corner_j: int
            for corner_i, corner_j in _triangle_corners(i, j):
                emit(grid[corner_i][corner_j])
    return (
        np.array(positions, dtype=np.float32),
        np.array(colors, dtype=np.float32),
    )


def surface_gradient(
    surface: Surface,
) -> typing.Callable[[float, float], g2.Vector]:
    """``(x, y) -> df/dx * e_1 + df/dy * e_2``, the gradient of the surface's ``fn``.

    The derivatives are exact when ``fn`` can be called on sympy symbols, which
    it can when it is built from gacalc operations (the book's graphs are):
    sympy differentiates the expression once and the result is evaluated at each
    point.  A ``fn`` that cannot be (it casts to ``float``), and a point where
    the derivative is undefined (the tip of a cone), use a central difference.

    >>> white: Color = (1.0, 1.0, 1.0)
    >>> saddle: Surface = Surface(
    ...     fn=lambda x, y: (x * x - y * y) / 8, label="s", color=white, latex="s"
    ... )
    >>> [round(float(c), 6) for c in surface_gradient(saddle)(2.0, 4.0)]
    [0.5, -1.0]
    >>> opaque: Surface = Surface(
    ...     fn=lambda x, y: float(x) * 0.5, label="o", color=white, latex="o"
    ... )
    >>> [round(c, 6) for c in surface_gradient(opaque)(1.0, 1.0)]
    [0.5, 0.0]
    """

    def central_difference(x: float, y: float) -> g2.Vector:
        step: float = 1e-4
        return (
            float(surface.fn(x + step, y) - surface.fn(x - step, y))
            / (2.0 * step)
            * g2.e_1
            + float(surface.fn(x, y + step) - surface.fn(x, y - step))
            / (2.0 * step)
            * g2.e_2
        )

    x_symbol: sympy.Symbol = sympy.Symbol("x", real=True)
    y_symbol: sympy.Symbol = sympy.Symbol("y", real=True)
    try:
        height: sympy.Expr = sympy.sympify(surface.fn(x_symbol, y_symbol))
    except TypeError:
        return central_difference
    partials: typing.Callable[[float, float], tuple[float, float]] = sympy.lambdify(
        (x_symbol, y_symbol),
        (sympy.diff(height, x_symbol), sympy.diff(height, y_symbol)),
        "math",
    )

    def exact(x: float, y: float) -> g2.Vector:
        try:
            df_dx: float
            df_dy: float
            df_dx, df_dy = partials(x, y)
            if math.isfinite(df_dx) and math.isfinite(df_dy):
                return float(df_dx) * g2.e_1 + float(df_dy) * g2.e_2
        except ZeroDivisionError, ValueError:
            pass  # undefined here: fall through to the central difference
        return central_difference(x, y)

    return exact


def surface_normal(
    gradient: typing.Callable[[float, float], g2.Vector],
    x: float,
    y: float,
) -> g3.Vector:
    """The unit normal of the height field at domain point ``(x, y)``, pointing up.

    The height field is the world point ``(x, f(x, y), y)`` (domain y is world z),
    so its tangents are ``(1, df/dx, 0)`` along world x and ``(0, df/dy, 1)``
    along world z, and the normal is their cross product,
    ``(-df/dx, 1, -df/dy)``, normalized.  The tilted plane ``f(x, y) = x`` leans
    its normal away from the rising side:

    >>> rising: g2.Vector = 1.0 * g2.e_1 + 0.0 * g2.e_2
    >>> n: g3.Vector = surface_normal(lambda x, y: rising, 0.0, 0.0)
    >>> [round(float(c), 4) for c in n]
    [-0.7071, 0.7071, 0.0]
    >>> level: g2.Vector = 0.0 * g2.e_1 + 0.0 * g2.e_2
    >>> [round(float(c), 4) for c in surface_normal(lambda x, y: level, 1.0, 2.0)]
    [0.0, 1.0, 0.0]
    """
    slope: g2.Vector = gradient(x, y)
    df_dx: float = float(slope.coefficient(g2.e_1))
    df_dy: float = float(slope.coefficient(g2.e_2))
    along_x: g3.Vector = 1.0 * g3.e_1 + df_dx * g3.e_2 + 0.0 * g3.e_3
    along_z: g3.Vector = 0.0 * g3.e_1 + df_dy * g3.e_2 + 1.0 * g3.e_3
    return along_z.cross(along_x).normalize()


def build_normals(surface: Surface, dx: float, dy: float) -> np.ndarray:
    """One unit normal per vertex of :func:`build_solid`, in the same order.

    A step of 6 gives 8 triangles of 3 vertices, one normal each; on a flat
    surface every normal is straight up:

    >>> white: Color = (1.0, 1.0, 1.0)
    >>> flat: Surface = Surface(fn=lambda x, y: 0.0, label="f", color=white, latex="0")
    >>> normals: np.ndarray = build_normals(flat, 6.0, 6.0).reshape(-1, 3)
    >>> normals.shape
    (24, 3)
    >>> normals[:, 1].min(), normals[:, 1].max()
    (np.float32(1.0), np.float32(1.0))
    """
    nx: int = _axis_count(dx)
    ny: int = _axis_count(dy)
    gradient: typing.Callable[[float, float], g2.Vector] = surface_gradient(surface)
    grid: list[list[g3.Vector]] = [
        [
            surface_normal(
                gradient,
                -DOMAIN_HALF + i * (2.0 * DOMAIN_HALF) / nx,
                -DOMAIN_HALF + j * (2.0 * DOMAIN_HALF) / ny,
            )
            for j in range(ny + 1)
        ]
        for i in range(nx + 1)
    ]
    normals: list[float] = []
    i: int
    j: int
    corner_i: int
    corner_j: int
    for i in range(nx):
        for j in range(ny):
            for corner_i, corner_j in _triangle_corners(i, j):
                normals.extend(float(c) for c in grid[corner_i][corner_j])
    return np.array(normals, dtype=np.float32)


def light_vector(azimuth: float, elevation: float) -> g3.Vector:
    """The unit world-space direction toward the light, from two angles in degrees.

    The azimuth turns about the up (y) axis from +z toward +x; the elevation
    lifts the light above the ground plane:

    >>> [round(float(c), 4) for c in light_vector(0.0, 90.0)]
    [0.0, 1.0, 0.0]
    >>> [round(float(c), 4) for c in light_vector(90.0, 0.0)]
    [1.0, 0.0, 0.0]
    """
    a: float = math.radians(azimuth)
    e: float = math.radians(elevation)
    return (
        math.cos(e) * math.sin(a) * g3.e_1
        + math.sin(e) * g3.e_2
        + math.cos(e) * math.cos(a) * g3.e_3
    )


def build_axes() -> np.ndarray:
    """The three axes (through the origin) plus tick marks (GL_LINES).

    3 axes plus 12 ticks on each (none at the origin), two vertices per line:

    >>> build_axes().reshape(-1, 3).shape
    (78, 3)
    """
    verts: list[float] = [
        -AXIS_LENGTH,
        0.0,
        0.0,
        AXIS_LENGTH,
        0.0,
        0.0,
        0.0,
        -AXIS_LENGTH,
        0.0,
        0.0,
        AXIS_LENGTH,
        0.0,
        0.0,
        0.0,
        -AXIS_LENGTH,
        0.0,
        0.0,
        AXIS_LENGTH,
    ]
    n: int = int(DOMAIN_HALF)
    i: int
    for i in range(-n, n + 1):
        if i == 0:
            continue
        c: float = float(i)
        # ticks along x (mark up), along z (mark up), along y (mark along x)
        verts.extend([c, -TICK_LENGTH, 0.0, c, TICK_LENGTH, 0.0])
        verts.extend([0.0, -TICK_LENGTH, c, 0.0, TICK_LENGTH, c])
        verts.extend([-TICK_LENGTH, c, 0.0, TICK_LENGTH, c, 0.0])
    return np.array(verts, dtype=np.float32)


# ---------------------------------------------------------------------------
# The program: a window, its GL objects, the input handlers and the loop.
# ---------------------------------------------------------------------------


def run(
    surfaces: typing.Sequence[Surface],
    title: str = "3D Graphing Calculator",
) -> None:
    """Open a window plotting ``surfaces``, one at a time, and run until the
    window is closed.

    Controls: left-drag / arrows orbit, the mouse wheel zooms, the Surface
    menu picks the function, ``W`` / ``S`` toggle the wireframe and the solid
    mesh, ``T`` toggles the lighting, the Light menu sets the light's
    direction and the highlight's sharpness, ``L`` toggles the TeX labels, F11
    toggles fullscreen and Esc quits.
    """
    view: View3D = View3D()
    win_state: cayley_gl.WindowState = cayley_gl.WindowState()
    mouse_prev: tuple[float, float] | None = None

    window: "GLFWWindow"
    impl: "cayley_gl.GlfwRenderer"
    imguiio: "cayley_gl.imgui.IO"
    window, impl, imguiio = cayley_gl.setup(title)
    GL.glClearColor(0.07, 0.07, 0.09, 1.0)
    GL.glEnable(GL.GL_DEPTH_TEST)
    camera: _p.Camera = cayley_gl.make_camera(r=22.0)
    cayley_gl.install_scroll(window, imguiio, camera)

    line_pipeline: _p.Pipeline = _p.build_pipeline(
        "uniform_color.vert",
        "passthrough.frag",
        shader_dir=SHADER_DIR,
        color=True,
    )
    surface_pipeline: _p.Pipeline = _p.build_pipeline(
        "per_vertex_color.vert",
        "passthrough.frag",
        shader_dir=SHADER_DIR,
        per_vertex_color=True,
    )
    lit_pipeline: _p.Pipeline = _p.build_pipeline(
        "lit_surface.vert", "lit_surface.frag", shader_dir=SHADER_DIR
    )
    u_light: int = GL.glGetUniformLocation(lit_pipeline.program, "light_direction")
    u_material: int = GL.glGetUniformLocation(lit_pipeline.program, "material_color")
    u_shininess: int = GL.glGetUniformLocation(lit_pipeline.program, "shininess")
    # Runtime TeX billboard labels (no-op if texExpToPng is not on PATH).
    label_renderer: _labels.LabelRenderer = _labels.LabelRenderer(SHADER_DIR)

    def dynamic_lines(verts: np.ndarray) -> tuple[int, int, int]:
        data: np.ndarray = np.ascontiguousarray(verts, dtype=np.float32)
        vbo: int = _p.make_vbo(data, usage=GL.GL_DYNAMIC_DRAW)
        vao: int = _p.make_vao(
            [
                _p.AttribSpec(
                    vbo=vbo,
                    location=line_pipeline.attr_position,
                    size=_p.floats_per_vertex,
                    layout=(0, 0),
                )
            ]
        )
        return vao, vbo, data.size // _p.floats_per_vertex

    def dynamic_solid(
        positions: np.ndarray, colors: np.ndarray, normals: np.ndarray
    ) -> tuple[int, int, int, int, int, int]:
        pos: np.ndarray = np.ascontiguousarray(positions, dtype=np.float32)
        col: np.ndarray = np.ascontiguousarray(colors, dtype=np.float32)
        nor: np.ndarray = np.ascontiguousarray(normals, dtype=np.float32)
        pos_vbo: int = _p.make_vbo(pos, usage=GL.GL_DYNAMIC_DRAW)
        color_vbo: int = _p.make_vbo(col, usage=GL.GL_DYNAMIC_DRAW)
        normal_vbo: int = _p.make_vbo(nor, usage=GL.GL_DYNAMIC_DRAW)
        vao: int = _p.make_vao(
            [
                _p.AttribSpec(
                    vbo=pos_vbo,
                    location=surface_pipeline.attr_position,
                    size=_p.floats_per_vertex,
                    layout=(0, 0),
                ),
                _p.AttribSpec(
                    vbo=color_vbo,
                    location=surface_pipeline.attr_color,
                    size=3,
                    layout=(0, 0),
                ),
            ]
        )
        lit_vao: int = _p.make_vao(
            [
                _p.AttribSpec(
                    vbo=pos_vbo,
                    location=lit_pipeline.attr_position,
                    size=_p.floats_per_vertex,
                    layout=(0, 0),
                ),
                _p.AttribSpec(
                    vbo=normal_vbo,
                    location=GL.glGetAttribLocation(lit_pipeline.program, "normal_in"),
                    size=3,
                    layout=(0, 0),
                ),
            ]
        )
        return (
            vao,
            pos_vbo,
            color_vbo,
            pos.size // _p.floats_per_vertex,
            lit_vao,
            normal_vbo,
        )

    def reupload(vbo: int, verts: np.ndarray) -> int:
        data: np.ndarray = np.ascontiguousarray(verts, dtype=np.float32)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, data.nbytes, data, GL.GL_DYNAMIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        return data.size

    def build_meshes() -> SurfaceMeshes:
        surface: Surface = surfaces[view.current]
        wire: np.ndarray = build_wireframe(surface, view.dx, view.dy)
        positions: np.ndarray
        colors: np.ndarray
        wire_vao: int
        wire_vbo: int
        wire_n: int
        solid_vao: int
        pos_vbo: int
        color_vbo: int
        solid_n: int
        lit_vao: int
        normal_vbo: int
        positions, colors = build_solid(surface, view.dx, view.dy)
        wire_vao, wire_vbo, wire_n = dynamic_lines(wire)
        solid_vao, pos_vbo, color_vbo, solid_n, lit_vao, normal_vbo = dynamic_solid(
            positions, colors, build_normals(surface, view.dx, view.dy)
        )
        return SurfaceMeshes(
            wire_vao=wire_vao,
            wire_vbo=wire_vbo,
            wire_count=wire_n,
            solid_vao=solid_vao,
            solid_pos_vbo=pos_vbo,
            solid_color_vbo=color_vbo,
            solid_count=solid_n,
            lit_vao=lit_vao,
            solid_normal_vbo=normal_vbo,
        )

    meshes: SurfaceMeshes = build_meshes()
    axes_vao: int
    axes_count: int
    axes_vao, axes_count = _p.make_lines_vao(build_axes(), line_pipeline.attr_position)
    # (current, dx, dy) the meshes were last built at -- rebuild when it changes.
    built_key: tuple[int, float, float] = (view.current, view.dx, view.dy)

    def rebuild_meshes_if_needed() -> None:
        nonlocal built_key
        key: tuple[int, float, float] = (view.current, view.dx, view.dy)
        if key == built_key:
            return
        surface: Surface = surfaces[view.current]
        wire: np.ndarray = build_wireframe(surface, view.dx, view.dy)
        positions: np.ndarray
        colors: np.ndarray
        positions, colors = build_solid(surface, view.dx, view.dy)
        meshes.wire_count = reupload(meshes.wire_vbo, wire) // _p.floats_per_vertex
        reupload(meshes.solid_color_vbo, colors)
        reupload(meshes.solid_normal_vbo, build_normals(surface, view.dx, view.dy))
        meshes.solid_count = (
            reupload(meshes.solid_pos_vbo, positions) // _p.floats_per_vertex
        )
        built_key = key

    def draw_lines(vao: int, count: int, color: Color) -> None:
        GL.glUseProgram(line_pipeline.program)
        GL.glBindVertexArray(vao)
        GL.glUniform3f(line_pipeline.u_color, *color)
        _p.set_uniforms(line_pipeline.u_m, line_pipeline.u_v, line_pipeline.u_p)
        GL.glDrawArrays(GL.GL_LINES, 0, count)

    def draw_lit_solid() -> None:
        GL.glUseProgram(lit_pipeline.program)
        GL.glBindVertexArray(meshes.lit_vao)
        _p.set_uniforms(lit_pipeline.u_m, lit_pipeline.u_v, lit_pipeline.u_p)
        GL.glUniform3f(u_light, *light_vector(view.light_azimuth, view.light_elevation))
        GL.glUniform3f(u_material, *surfaces[view.current].color)
        GL.glUniform1f(u_shininess, view.shininess)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, meshes.solid_count)

    def draw_solid() -> None:
        GL.glUseProgram(surface_pipeline.program)
        GL.glBindVertexArray(meshes.solid_vao)
        _p.set_uniforms(
            surface_pipeline.u_m, surface_pipeline.u_v, surface_pipeline.u_p
        )
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, meshes.solid_count)

    def select(index: int) -> None:
        view.current = index

    def toggle_wire() -> None:
        view.show_wireframe = not view.show_wireframe

    def toggle_solid() -> None:
        view.show_solid = not view.show_solid

    def toggle_lit() -> None:
        view.lit = not view.lit

    def toggle_labels() -> None:
        view.show_labels = not view.show_labels

    def imgui_menubar() -> None:
        if not imgui.begin_main_menu_bar():
            return
        if imgui.begin_menu("File", True):
            cayley_gl.menu_action(
                "Quit", "Esc", lambda: glfw.set_window_should_close(window, True)
            )
            imgui.end_menu()
        if imgui.begin_menu("Surface", True):
            idx: int
            surface: Surface
            for idx, surface in enumerate(surfaces):
                cayley_gl.menu_action(
                    surface.label,
                    "",
                    lambda i=idx: select(i),
                    selected=(idx == view.current),
                )
            imgui.end_menu()
        if imgui.begin_menu("Controls", True):
            _, view.dx = imgui.slider_float("Grid step dx", view.dx, 0.2, 2.0)
            _, view.dy = imgui.slider_float("Grid step dy", view.dy, 0.2, 2.0)
            cayley_gl.menu_action(
                "Wireframe", "W", toggle_wire, selected=view.show_wireframe
            )
            cayley_gl.menu_action(
                "Solid surface", "S", toggle_solid, selected=view.show_solid
            )
            cayley_gl.menu_action("Lighting", "T", toggle_lit, selected=view.lit)
            cayley_gl.menu_action(
                "Labels", "L", toggle_labels, selected=view.show_labels
            )
            imgui.end_menu()
        if imgui.begin_menu("Light", True):
            _, view.light_azimuth = imgui.slider_float(
                "Azimuth (deg)", view.light_azimuth, -180.0, 180.0
            )
            _, view.light_elevation = imgui.slider_float(
                "Elevation (deg)", view.light_elevation, 0.0, 90.0
            )
            _, view.shininess = imgui.slider_float(
                "Shininess", view.shininess, 1.0, 256.0
            )
            imgui.end_menu()
        if imgui.begin_menu("View", True):
            cayley_gl.menu_action(
                "Fullscreen",
                "F11",
                lambda: cayley_gl.toggle_fullscreen(window, win_state),
                selected=win_state.fullscreen,
            )
            imgui.end_menu()
        imgui.end_main_menu_bar()

    def on_key(
        window: "GLFWWindow", key: int, scancode: int, action: int, mods: int
    ) -> None:
        cayley_gl.common_key(window, win_state, key, action)
        if action != glfw.PRESS:
            return
        match key:
            case glfw.KEY_W:
                toggle_wire()
            case glfw.KEY_S:
                toggle_solid()
            case glfw.KEY_T:
                toggle_lit()
            case glfw.KEY_L:
                toggle_labels()
            case _:
                pass  # every other key is handled by common_key or ignored

    def draw_labels(w: int, h: int) -> None:
        """Billboard LaTeX labels: the x/y/z axis tips (domain x -> world x,
        domain y -> world z, height -> world y) and the current surface's
        equation above the plot."""
        v_m: np.ndarray = ms.get_current_matrix(ms.MatrixStack.view)
        p_m: np.ndarray = ms.get_current_matrix(ms.MatrixStack.projection)
        label_renderer.begin(v_m, p_m, (w, h))
        label_renderer.draw("x", (AXIS_LENGTH + 0.4, 0.0, 0.0))
        label_renderer.draw("y", (0.0, 0.0, AXIS_LENGTH + 0.4))
        label_renderer.draw("z", (0.0, AXIS_LENGTH + 0.4, 0.0))
        label_renderer.draw(surfaces[view.current].latex, (0.0, AXIS_LENGTH + 1.6, 0.0))
        label_renderer.end()

    def frame(w: int, h: int) -> None:
        nonlocal mouse_prev
        rebuild_meshes_if_needed()
        mouse_prev = cayley_gl.orbit_input(window, imguiio, camera, mouse_prev)
        cayley_gl.setup_orbit_view(camera, w, h)
        draw_lines(axes_vao, axes_count, AXIS_COLOR)
        if view.show_solid:
            if view.lit:
                draw_lit_solid()
            else:
                draw_solid()
        if view.show_wireframe:
            draw_lines(meshes.wire_vao, meshes.wire_count, surfaces[view.current].color)
        if view.show_labels and label_renderer.available:
            draw_labels(w, h)

    # The event loop.  The key callback goes in after cayley_gl.setup created
    # the GlfwRenderer, so it replaces imgui's key handling.  The menubar is
    # drawn after begin_frame and before the clear.
    glfw.set_key_callback(window, on_key)
    t_prev: float = glfw.get_time()
    while not glfw.window_should_close(window):
        t_prev = cayley_gl.begin_frame(impl, t_prev)
        imgui_menubar()
        w: int
        h: int
        w, h = cayley_gl.clear_viewport(window)
        frame(w, h)
        cayley_gl.end_frame(window, impl)
    # Release the label textures while the GL context still exists.
    label_renderer.cleanup()
    cayley_gl.shutdown()
