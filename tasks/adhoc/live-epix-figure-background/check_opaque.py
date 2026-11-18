"""Execute the book notebooks that draw live ePiX figures and check every PNG is opaque.

One-shot check for tasks/live-epix-figure-background.md. Run in the container from
the repo root:
    python tasks/adhoc/live-epix-figure-background/check_opaque.py
It converts each notebook with jupytext, executes it with nbconvert, and asks
ImageMagick whether each image/png output is fully opaque with a #f2f2f2 corner.
"""

import base64
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import typing

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
NOTEBOOKS: list[str] = [
    "bootstrap-product",
    "bootstrap-projection",
    "bootstrap-projection-from-product",
    "bootstrap-rotation",
    "bootstrap-rotation-from-product",
    "bootstrap-rotation-from-projection",
    "frame-qr-2d",
    "frame-qr-3d",
]


def identify(png: bytes, fmt: str) -> str:
    """ImageMagick's ``identify -format fmt`` for the PNG bytes."""
    magick: str = shutil.which("magick") or "convert"
    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        f.write(png)
        f.flush()
        return subprocess.run(
            [magick, "identify", "-format", fmt, f.name],
            check=True,
            capture_output=True,
            text=True,
        ).stdout


def main() -> int:
    """Check every notebook; print one line each; return 1 on any transparent PNG."""
    status: int = 0
    name: str
    for name in NOTEBOOKS:
        source: pathlib.Path = ROOT / "book/docs/notebooks" / f"{name}.py"
        # beside its source (book/docs/notebooks/*.ipynb is gitignored), so the
        # notebook's relative sys.path entry finds the figure helpers
        ipynb: pathlib.Path = source.with_suffix(".ipynb")
        subprocess.run(
            ["jupytext", "--to", "ipynb", "-o", str(ipynb), str(source)],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                "--inplace",
                "--ExecutePreprocessor.timeout=1800",
                str(ipynb),
            ],
            check=True,
            capture_output=True,
            cwd=source.parent,
        )
        cells: list[dict[str, typing.Any]] = json.loads(ipynb.read_text())["cells"]
        pngs: list[bytes] = [
            base64.b64decode(output["data"]["image/png"])
            for cell in cells
            for output in cell.get("outputs", [])
            if "image/png" in output.get("data", {})
        ]
        bad: list[int] = [
            i
            for i, png in enumerate(pngs)
            if identify(png, "%[opaque]") != "True"
            or not identify(png, "%[hex:p{0,0}]").upper().startswith("F2F2F2")
        ]
        print(f"{name}: {len(pngs)} figures, {len(bad)} not opaque #f2f2f2 {bad}")  # noqa: T201 -- the report
        if bad or not pngs:
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
