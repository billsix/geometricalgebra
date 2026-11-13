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
scroll) looks around it.  The solid mesh is unlit; the lit (Blinn-Phong)
version is ``tasks/grapher3d-lit-mesh.md``.

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

import gacalc.gl.matrix_stack as ms
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
    in source) that the billboard renderer typesets as its equation caption."""

    fn: typing.Callable[[float, float], float]
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


def build_wireframe(surface: Surface, dx: float, dy: float) -> np.ndarray:
    """Grid lines of the height field as GL_LINES (both grid directions).

    A step of 6 gives a 2 x 2 grid of cells: 3 lines of 2 segments in each
    direction, two vertices per segment:

    >>> white: Color = (1.0, 1.0, 1.0)
    >>> flat = Surface(fn=lambda x, y: 0.0, label="flat", color=white, latex="0")
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
    >>> tilt = Surface(fn=lambda x, y: x, label="tilt", color=white, latex="x")
    >>> positions, colors = build_solid(tilt, 6.0, 6.0)
    >>> positions.reshape(-1, 3).shape, colors.reshape(-1, 3).shape
    ((24, 3), (24, 3))
    """
    nx: int = _axis_count(dx)
    ny: int = _axis_count(dy)
    grid: list[list[tuple[float, float, float]]] = []
    lo: float = math.inf
    hi: float = -math.inf
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
            a: tuple[float, float, float] = grid[i][j]
            b: tuple[float, float, float] = grid[i + 1][j]
            c: tuple[float, float, float] = grid[i + 1][j + 1]
            d: tuple[float, float, float] = grid[i][j + 1]
            for p in (a, b, c, a, c, d):
                emit(p)
    return (
        np.array(positions, dtype=np.float32),
        np.array(colors, dtype=np.float32),
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
    mesh, ``L`` toggles the TeX labels, F11 toggles fullscreen and Esc quits.
    """
    view: View3D = View3D()
    win_state: cayley_gl.WindowState = cayley_gl.WindowState()
    mouse_prev: tuple[float, float] | None = None

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
        positions: np.ndarray, colors: np.ndarray
    ) -> tuple[int, int, int, int]:
        pos: np.ndarray = np.ascontiguousarray(positions, dtype=np.float32)
        col: np.ndarray = np.ascontiguousarray(colors, dtype=np.float32)
        pos_vbo: int = _p.make_vbo(pos, usage=GL.GL_DYNAMIC_DRAW)
        color_vbo: int = _p.make_vbo(col, usage=GL.GL_DYNAMIC_DRAW)
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
        return vao, pos_vbo, color_vbo, pos.size // _p.floats_per_vertex

    def reupload(vbo: int, verts: np.ndarray) -> int:
        data: np.ndarray = np.ascontiguousarray(verts, dtype=np.float32)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, data.nbytes, data, GL.GL_DYNAMIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        return data.size

    def build_meshes() -> SurfaceMeshes:
        surface: Surface = surfaces[view.current]
        wire: np.ndarray = build_wireframe(surface, view.dx, view.dy)
        positions, colors = build_solid(surface, view.dx, view.dy)
        wire_vao, wire_vbo, wire_n = dynamic_lines(wire)
        solid_vao, pos_vbo, color_vbo, solid_n = dynamic_solid(positions, colors)
        return SurfaceMeshes(
            wire_vao=wire_vao,
            wire_vbo=wire_vbo,
            wire_count=wire_n,
            solid_vao=solid_vao,
            solid_pos_vbo=pos_vbo,
            solid_color_vbo=color_vbo,
            solid_count=solid_n,
        )

    meshes: SurfaceMeshes = build_meshes()
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
        positions, colors = build_solid(surface, view.dx, view.dy)
        meshes.wire_count = reupload(meshes.wire_vbo, wire) // _p.floats_per_vertex
        reupload(meshes.solid_color_vbo, colors)
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
            cayley_gl.menu_action(
                "Labels", "L", toggle_labels, selected=view.show_labels
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
        w, h = cayley_gl.clear_viewport(window)
        frame(w, h)
        cayley_gl.end_frame(window, impl)
    # Release the label textures while the GL context still exists.
    label_renderer.cleanup()
    cayley_gl.shutdown()
