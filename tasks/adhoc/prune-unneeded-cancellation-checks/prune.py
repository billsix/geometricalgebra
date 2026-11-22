#!/usr/bin/env python3
"""Remove the unneeded cancellation displays listed in tasks/prune-unneeded-cancellation-checks.md.

Each entry names a notebook, the first line of the ``show_difference`` call to remove,
and what the markdown cell just before it becomes. The code cell holding the call is
deleted. The markdown cell's last paragraph (the lead-in such as "Their difference:") is
replaced by a plain statement of the claim, or dropped when ``replacement`` is empty.
A cell left with no text is deleted. A notebook left with no ``show_difference`` /
``show_cancellation`` call also loses those names from its ``nbdisplay`` import.

Matching is on the call's text, not a line number. Running it a second time finds
nothing to remove and changes nothing.

Usage: ``python tasks/adhoc/prune-unneeded-cancellation-checks/prune.py``
"""

from __future__ import annotations

import pathlib
import re
import textwrap
from dataclasses import dataclass

REPO: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
PROSE_WIDTH: int = 86  # 88 columns less the leading "# "
CELL_HEADER: re.Pattern[str] = re.compile(r"^# %%", re.MULTILINE)
MARKDOWN_HEADER: str = "# %% [markdown]"
A: str = r"$\vec{\mathbf{a}}$"
B: str = r"$\vec{\mathbf{b}}$"


@dataclass(frozen=True)
class Prune:
    """One cancellation display to remove.

    Attributes:
        notebook: File stem under ``notebooks/``.
        call: The first line(s) of the call, as written at the start of its code cell.
        replacement: New text for the last paragraph of the markdown cell before the
            call; empty means that paragraph is dropped.
    """

    notebook: str
    call: str
    replacement: str


PRUNES: tuple[Prune, ...] = (
    Prune(
        "vector-addition",
        "show_difference(a + b, b + a)",
        "Each coordinate is the same two numbers added in the other order, so the two sums are equal.",
    ),
    Prune(
        "vector-addition",
        "show_difference((a - b) + b, a)",
        f"Subtracting {B} and adding it back gives {A} again.",
    ),
    Prune("vector-addition", "show_difference(a - b, a + (-b))", ""),
    Prune("vector-addition", "show_difference(t(a), a + b)", ""),
    Prune(
        "vector-addition",
        "show_difference(t.inverse(t(a)), a)",
        f"The inverse undoes the slide, so it gives back {A}.",
    ),
    Prune(
        "vector-addition",
        "show_difference(t.at(0.5)(a), a + b * 0.5)",
        "It is the same point.",
    ),
    Prune(
        "geometry-from-vectors",
        "show_difference(at_values(segment_point, [(t, 0)]), a)",
        f"That is {A}, where the segment starts.",
    ),
    Prune(
        "geometry-from-vectors",
        "show_difference(at_values(segment_point, [(t, 1)]), b)",
        f"That is {B}, where the segment ends.",
    ),
    Prune(
        "canonical-form",
        "show_difference(sympy.sqrt(8), 4 / sympy.sqrt(2))",
        r"Both come out as $2\sqrt{2}$, so they are equal.",
    ),
    Prune(
        "geometric-product",
        "show_difference((a + b) * R, a * R + b * R)",
        "Multiplying a sum by $R$ is the same as multiplying each part by it.",
    ),
    Prune(
        "relative-graph-paper",
        "show_difference(f.inverse(f(p)), p)",
        "and the inverse function reads them back: given a spot in standard coordinates, "
        "it says where that spot is on the carried sheet. Applied to the carried spot, "
        "it returns $(x, y)$.",
    ),
    Prune(
        "reflection",
        "show_difference(a.reflected_across(b), reflection)",
        "gacalc's `reflected_across` is defined as the projection minus the rejection, "
        "which the cell above showed equal to the reflection built by rotating.",
    ),
    Prune(
        "reflection",
        "show_difference(reflection.magnitude_squared(), a.magnitude_squared())",
        "The two squared lengths are equal, so the reflection keeps the length.",
    ),
    Prune(
        "reflection-3d",
        "show_difference(v.reflected_across(a), across_a)",
        "gacalc's `reflected_across(a)` is defined as this projection minus this rejection.",
    ),
    Prune(
        "reflection-3d",
        "show_difference(v.reflected_across(B), mirror)",
        "gacalc's `reflected_across(B)` is defined as this projection minus this rejection.",
    ),
    Prune(
        "dual-3d",
        "show_difference(b.projected_onto(a) + r, b)",
        r"The projection plus the rejection is $\vec{\mathbf{b}}$.",
    ),
    Prune("dual-3d", "show_difference(product_r, swapped_r)", ""),
    Prune(
        "defining-g2",
        "show_difference(A.r_vector_part(0) + A.r_vector_part(1)",
        "The parts add back up to $A$.",
    ),
    Prune(
        "displayg2",
        "show_difference(e_12, e_1 * e_2)",
        r"It is $-1$, exactly like the imaginary number $i$. So the plain numbers together "
        r"with $\mathbf{e}_{12}$ behave like the complex numbers. The class names that piece "
        r"of plane `e_12`; it is the same value as the product $\mathbf{e}_1 * \mathbf{e}_2$.",
    ),
    Prune(
        "displayg3",
        "show_difference(e_123, e_1 * e_2 * e_3)",
        r"It is $-1$, like the plane's $\mathbf{e}_{12}$ in `displayg2.py`. The class names it "
        r"`e_123`, the same value as the product of the three arrows.",
    ),
    Prune(
        "displayg2areas",
        "show_difference(area(a, b), abs(signed_area(a, b)))",
        "and the unsigned area is its absolute value.",
    ),
    Prune(
        "displayg3measures",
        "show_difference(area(a_vec, b_vec), area(b_vec, a_vec))",
        "An area has no direction, so swapping the sides changes nothing.",
    ),
    Prune(
        "displaymv",
        "show_difference(\n    MultiVector.i(sym_vec2_1, sym_vec2_2)",
        r"Wedging two vectors just to *name the plane they span* is common enough to have "
        r"helpers: `bivector_from_vectors(a, b)` is exactly "
        r"$\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$, and `i(a, b)` is that plane's *unit* "
        r"bivector ($i * i = -1$), the same as $\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$ "
        r"divided by its size.",
    ),
    Prune(
        "bootstrap-rotation",
        "show_difference(v.rotate(theta).rotate(-theta), v)",
        r"Turning by $\theta$ and then by $-\theta$ gives $\vec{\mathbf{v}}$ back.",
    ),
    Prune(
        "bootstrap-rotation-from-projection",
        "show_difference(rotated.magnitude_squared(), v.magnitude_squared())",
        "The two are equal: the rotation keeps the length.",
    ),
    Prune(
        "bootstrap-rotation-from-projection",
        "show_difference(rotated_sum, sum_of_rotated)",
        "The two are equal, so the rotation of a sum is the sum of the rotations.",
    ),
    Prune(
        "bootstrap-rotation-from-projection",
        "show_difference(rotated_multiple, Scalar(k) * rotated)",
        "The two are equal, so the rotation of a multiple is the multiple of the rotation.",
    ),
    Prune(
        "bootstrap-projection-from-product",
        "show_difference(projection + rejection, b)",
        f"The projection and the rejection add back up to {B}.",
    ),
    Prune(
        "bootstrap-projection-from-product",
        "show_difference(projection, b.projected_onto(a))",
        "It is the same as the product's.",
    ),
    Prune(
        "bootstrap-projection-from-product",
        "show_difference(rejection, b.rejected_away_from(a))",
        "It is the same as the product's.",
    ),
    Prune(
        "frame-qr-2d", "show_difference(g(x), y)", r"That is $\vec{\mathbf{y}}$ again."
    ),
    Prune(
        "frame-qr-3d", "show_difference(f(x), y)", r"That is $\vec{\mathbf{y}}$ again."
    ),
    Prune(
        "proof-reciprocal-frame",
        "show_difference(by_peel.inverse(by_peel(x)), x)",
        r"The round trip gives $\vec{\mathbf{x}}$ back.",
    ),
    Prune(
        "proof-reciprocal-frame",
        "show_difference(by_peel(by_peel.inverse(y)), y)",
        r"The round trip gives $\vec{\mathbf{y}}$ back.",
    ),
    Prune(
        "proof-reciprocal-frame",
        "show_difference(space_by_peel.inverse(space_by_peel(z)), z)",
        r"The round trip gives $\vec{\mathbf{z}}$ back.",
    ),
    Prune(
        "proof-reciprocal-frame",
        "show_difference(space_by_peel(space_by_peel.inverse(z)), z)",
        r"The round trip gives $\vec{\mathbf{z}}$ back.",
    ),
    Prune(
        "bootstrap-rotation-from-product",
        "show_difference(unit_product * v, rotation_by_projection(b, a, v))",
        "It is the same rotation.",
    ),
)

NBDISPLAY_IMPORT: re.Pattern[str] = re.compile(
    r"^from gacalc\.nbdisplay import (?P<names>[^\n(]+)\n", re.MULTILINE
)
CALL_PATTERN: re.Pattern[str] = re.compile(
    r"^show_(difference|cancellation)\(", re.MULTILINE
)


def split_cells(text: str) -> tuple[str, list[str], list[str]]:
    """Split a jupytext percent file into its preamble, its cells and the gaps after them.

    Args:
        text: The whole file.

    Returns:
        tuple[str, list[str], list[str]]: the text before the first ``# %%`` line, each
            cell from its ``# %%`` line to its last non-blank line, and the blank-line
            run that followed each cell (so a file's own spacing is kept).
    """
    starts: list[int] = [m.start() for m in CELL_HEADER.finditer(text)]
    preamble: str = text[: starts[0]]
    bounds: list[int] = [*starts, len(text)]
    chunks: list[str] = [text[bounds[i] : bounds[i + 1]] for i in range(len(starts))]
    cells: list[str] = [chunk.rstrip("\n") for chunk in chunks]
    gaps: list[str] = [chunk[len(cell) :] for chunk, cell in zip(chunks, cells)]
    return preamble, cells, gaps


def join_cells(preamble: str, cells: list[str], gaps: list[str]) -> str:
    """Rebuild a file from `split_cells`' output.

    Args:
        preamble: The text before the first cell.
        cells: The cells.
        gaps: The blank-line run after each cell.

    Returns:
        str: the file text.
    """
    return preamble + "".join(cell + gap for cell, gap in zip(cells, gaps))


def rewrite_markdown(cell: str, replacement: str) -> str | None:
    """Replace the last paragraph of a markdown cell.

    Args:
        cell: A ``# %% [markdown]`` cell.
        replacement: New text for its last paragraph; empty drops the paragraph.

    Returns:
        str | None: the new cell, or None when no text is left.
    """
    lines: list[str] = cell.split("\n")[1:]
    split_at: int = len(lines)
    for index in range(len(lines) - 1, -1, -1):
        if lines[index].strip() == "#":
            split_at = index + 1
            break
        split_at = index
    kept: list[str] = lines[:split_at]
    while kept and kept[-1].strip() == "#":
        kept.pop()
    wrapped: list[str] = []
    if replacement:
        wrapped = [
            "# " + line
            for line in textwrap.wrap(
                replacement,
                width=PROSE_WIDTH,
                break_long_words=False,
                break_on_hyphens=False,
            )
        ]
        if kept:
            kept.append("#")
    body: list[str] = kept + wrapped
    if not body:
        return None
    return "\n".join([MARKDOWN_HEADER, *body])


def prune_notebook(path: pathlib.Path, prunes: list[Prune]) -> int:
    """Apply every prune for one notebook and fix its import.

    Args:
        path: The notebook.
        prunes: The entries naming this notebook.

    Returns:
        int: how many calls were removed.
    """
    original: str = path.read_text()
    preamble, cells, gaps = split_cells(original)
    assert join_cells(preamble, cells, gaps) == original, (
        f"{path}: split does not round-trip"
    )
    removed: int = 0
    for prune in prunes:
        matches: list[int] = [
            index
            for index, cell in enumerate(cells)
            if not cell.startswith(MARKDOWN_HEADER)
            and cell.split("\n", 1)[1].lstrip("\n").startswith(prune.call)
        ]
        if not matches:
            print(f"  already gone: {prune.call.splitlines()[0]}")
            continue
        assert len(matches) == 1, f"{path}: {prune.call!r} matches {len(matches)} cells"
        index: int = matches[0]
        code: str = cells[index].split("\n", 1)[1].strip("\n")
        assert code.count("show_difference(") == 1 and code.endswith(")"), (
            f"{path}: cell is not just the call: {code!r}"
        )
        assert cells[index - 1].startswith(MARKDOWN_HEADER), (
            f"{path}: no lead-in before {code!r}"
        )
        new_lead: str | None = rewrite_markdown(cells[index - 1], prune.replacement)
        if new_lead is None:
            del cells[index - 1 : index + 1]
            del gaps[index - 1 : index + 1]
        else:
            cells[index - 1 : index + 1] = [new_lead]
            gaps[index - 1 : index + 1] = [gaps[index]]
        removed += 1
    text: str = join_cells(preamble, cells, gaps)
    if not CALL_PATTERN.search(text):
        text = drop_unused_names(text)
    if text != original:
        path.write_text(text)
    return removed


def drop_unused_names(text: str) -> str:
    """Remove ``show_difference`` / ``show_cancellation`` from the nbdisplay import.

    Args:
        text: A notebook with no such call left.

    Returns:
        str: the text with the names (and the import line, if empty) removed.
    """
    match: re.Match[str] | None = NBDISPLAY_IMPORT.search(text)
    if match is None:
        return text
    names: list[str] = [n.strip() for n in match.group("names").split(",")]
    left: list[str] = [
        n for n in names if n not in ("show_difference", "show_cancellation")
    ]
    line: str = f"from gacalc.nbdisplay import {', '.join(left)}\n" if left else ""
    return text[: match.start()] + line + text[match.end() :]


def edit_displayg2_grouping() -> None:
    """Replace displayg2's associativity display, which shares a cell with a binding.

    The cell defines ``G2_3`` and calls ``show_cancellation``; nothing else uses
    ``G2_3``, and ``displaymv.py`` shows the same associativity with its Lean twin, so
    the section keeps a sentence pointing there.
    """
    path: pathlib.Path = REPO / "notebooks" / "displayg2.py"
    text: str = path.read_text()
    start: int = text.find("# %% [markdown]\n# Does grouping matter?")
    end: int = text.find("# %% [markdown]\n# Pulling out one kind of part")
    if start < 0 or end < 0:
        print("  already gone: displayg2 associativity display")
        return
    new: str = (
        "# %% [markdown]\n"
        "# Does grouping matter? No\n"
        "# ------------------------\n"
        "#\n"
        "# Take a third general element. Multiplying the first two first, or the last two\n"
        "# first, gives the same answer: that is associativity. `displaymv.py` lays the two\n"
        "# answers out term by term and matches every term of one with a partner in the other,\n"
        "# and because every coefficient is a symbol, that proves it for **every** three\n"
        "# elements.\n"
        "\n"
    )
    text = text[:start] + new + text[end:]
    text = text.replace(
        "from gacalc.nbdisplay import show_cancellation, show_difference, show_mult",
        "from gacalc.nbdisplay import show_difference, show_mult",
    )
    path.write_text(text)


def main() -> None:
    """Prune every listed call, notebook by notebook."""
    by_notebook: dict[str, list[Prune]] = {}
    for prune in PRUNES:
        by_notebook.setdefault(prune.notebook, []).append(prune)
    total: int = 0
    for notebook, prunes in by_notebook.items():
        count: int = prune_notebook(REPO / "notebooks" / f"{notebook}.py", prunes)
        print(f"{notebook}: removed {count}")
        total += count
    edit_displayg2_grouping()
    print(f"removed {total} of {len(PRUNES)}, plus the displayg2 associativity display")


if __name__ == "__main__":
    main()
