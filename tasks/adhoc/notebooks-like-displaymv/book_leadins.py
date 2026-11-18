"""Give every bare code cell of the book notebooks a Markdown lead-in.

A code cell is bare when the cell before it is also code. Rules, in order:

* a live-figure cell (it opens an ePiX scene) gets "Drawn at the plot values:";
* a cell defining and showing a vector, ``name: Vector = ...`` then ``name``, continues the
  previous sentence: "and $\\vec{\\mathbf{name}}$:" (a ``v_2`` becomes ``\\vec{\\mathbf{v}}_2``);
* the cells listed in ``MANUAL`` get the text given there.

Any other bare cell stops the script with its file and first line, so nothing is skipped
silently. Re-running finds no bare cells, so the script is idempotent.

Usage: python book_leadins.py   (from the repository root)
"""

import pathlib
import re
import sys

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
DEFINES: re.Pattern[str] = re.compile(
    r"^([a-z])(?:_(\d))?: (?:g3\.)?(?:Vector|MultiVectorBase) = "
)
MANUAL: dict[tuple[str, str], str] = {
    ("proof-projection.py", "b"): "and $\\vec{\\mathbf{b}}$:",
    ("proof-projection.py", "y"): "and its $y$-coordinate:",
    ("proof-projection.py", "at_values(y, values)"): "and $y$ at the plot values:",
    ("proof-projection-3d.py", "across_part: Vector = ("): "and the part across it:",
    ("proof-reciprocal-frame.py", "frame: list[MultiVectorBase] = [a_1, a_2]"): (
        "A vector $\\vec{\\mathbf{y}}$ in the frame, with coordinates $x_1$ and $x_2$:"
    ),
}


def lead_in(name: str, cell: str) -> str:
    """The Markdown lead-in for one bare code cell of notebook ``name``."""
    body: list[str] = [line for line in cell.splitlines()[1:] if line.strip()]
    if any("scene_" in line or "epix.figure" in line for line in body):
        return "Drawn at the plot values:"
    key: tuple[str, str] = (name, body[0])
    if key in MANUAL:
        return MANUAL[key]
    match: re.Match[str] | None = DEFINES.match(body[0])
    if match is not None:
        index: str = f"_{match.group(2)}" if match.group(2) else ""
        return f"and $\\vec{{\\mathbf{{{match.group(1)}}}}}{index}$:"
    sys.exit(f"{name}: no lead-in rule for {body[0]!r}")


def main() -> None:
    path: pathlib.Path
    for path in sorted((ROOT / "book/docs/notebooks").glob("*.py")):
        cells: list[str] = re.split(r"(?=^# %%)", path.read_text(), flags=re.M)
        out: list[str] = []
        added: int = 0
        i: int
        cell: str
        for i, cell in enumerate(cells):
            bare: bool = (
                i > 2
                and not cell.startswith("# %% [markdown]")
                and not cells[i - 1].startswith("# %% [markdown]")
                and cell.strip() != "# %%"
            )
            if bare:
                out.append(f"# %% [markdown]\n# {lead_in(path.name, cell)}\n\n")
                added += 1
            out.append(cell)
        if added:
            path.write_text("".join(out))
            print(f"{path.name}: {added} lead-ins")


if __name__ == "__main__":
    main()
