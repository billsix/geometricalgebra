"""Render one frame of the 3D grapher's solid surface headless and save it as a PNG.

Usage (inside the container, with DISPLAY set to an Xvfb):
    python tools/grapher3d_render_probe.py OUT.png [lit|unlit] [SURFACE_INDEX]

Runs the real :func:`gacalc.gl.grapher3d.run`, with the solid surface switched on
(and the lighting set as asked) and the Controls state untouched otherwise.
After a few frames it reads the framebuffer with ``glReadPixels`` (a screenshot of
an llvmpipe window is black), writes the PNG and closes the window.
"""

import dataclasses
import importlib.machinery
import importlib.util
import pathlib
import sys
import types
import typing

import glfw
import numpy as np
import OpenGL.GL as GL
from PIL import Image

from gacalc.gl import cayley_gl, grapher3d


def main(out_path: pathlib.Path, lit: bool, surface_index: int) -> None:
    """Run the grapher with the solid on, and save frame 6 as ``out_path``."""
    repo_root: pathlib.Path = pathlib.Path(__file__).resolve().parents[1]
    example_spec: importlib.machinery.ModuleSpec | None = (
        importlib.util.spec_from_file_location(
            "grapher3d_example", repo_root / "examples" / "grapher3d.py"
        )
    )
    assert example_spec is not None and example_spec.loader is not None
    example: types.ModuleType = importlib.util.module_from_spec(example_spec)
    example_spec.loader.exec_module(example)

    start_lit: bool = lit

    @dataclasses.dataclass
    class ProbeView(grapher3d.View3D):
        """The grapher's view state, starting with the solid surface on."""

        current: int = surface_index
        show_solid: bool = True
        show_wireframe: bool = False
        show_labels: bool = False
        lit: bool = start_lit
        dx: float = 0.3
        dy: float = 0.3

    grapher3d.View3D = ProbeView  # ty: ignore[invalid-assignment]
    real_end_frame: typing.Callable[..., None] = cayley_gl.end_frame
    frames: list[int] = [0]

    def end_frame(window: typing.Any, impl: typing.Any) -> None:
        frames[0] += 1
        if frames[0] == 6:
            width: int
            height: int
            width, height = glfw.get_framebuffer_size(window)
            GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 1)
            raw: bytes = GL.glReadPixels(
                0, 0, width, height, GL.GL_RGB, GL.GL_UNSIGNED_BYTE
            )
            image: np.ndarray = np.frombuffer(raw, dtype=np.uint8).reshape(
                height, width, 3
            )
            Image.fromarray(np.flipud(image)).save(out_path)
            lit_pixels: int = int((image.sum(axis=2) > 60).sum())
            sys.stdout.write(
                f"wrote {out_path} ({width}x{height}), {lit_pixels} non-dark pixels\n"
            )
            glfw.set_window_should_close(window, True)
        real_end_frame(window, impl)

    cayley_gl.end_frame = end_frame  # ty: ignore[invalid-assignment]
    grapher3d.run(example.SURFACES, title="probe")


if __name__ == "__main__":
    main(
        out_path=pathlib.Path(sys.argv[1]),
        lit=len(sys.argv) < 3 or sys.argv[2] == "lit",
        surface_index=int(sys.argv[3]) if len(sys.argv) > 3 else 0,
    )
