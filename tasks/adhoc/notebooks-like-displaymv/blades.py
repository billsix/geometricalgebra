"""Rewrite basis blades in the Markdown math of percent-format notebooks to the bold notation.

Inside ``$...$`` / ``$$...$$`` spans of ``# %% [markdown]`` cells only:
``e_1`` / ``e_{1}`` / ``e_i`` become ``\\vec{\\mathbf{e}}_1`` (a basis vector, also ``e_{i_1}``), and ``e_{12}`` /
``e_{123}`` blades become ``\\mathbf{e}_{12}``. Text inside
``\\text{...}`` is left alone, and an already bold ``\\mathbf{e}`` is not touched, so the script is
idempotent (run it twice: the second run changes nothing). Vector letters (``a``, ``v``) need
judgment and are converted by hand.

Usage: python blades.py NOTEBOOK.py ...
"""

import pathlib
import re
import sys

MATH: re.Pattern[str] = re.compile(r"\$\$.*?\$\$|\$[^$]+\$", re.S)
TEXT: re.Pattern[str] = re.compile(r"\\text\{[^}]*\}")
# not preceded by a letter, backslash or brace-closing bold (\mathbf{e})
MULTI: re.Pattern[str] = re.compile(r"(?<![A-Za-z\\{])e_\{(\d{2,})\}")
# a basis vector whose index is itself subscripted, e_{i_1}
SUBSCRIPTED: re.Pattern[str] = re.compile(r"(?<![A-Za-z\\{])e_\{([a-z]_[0-9a-z]+)\}")
SINGLE: re.Pattern[str] = re.compile(r"(?<![A-Za-z\\{])e_(?:\{([0-9a-z])\}|([0-9a-z]))(?![0-9a-z_])")


def convert_math(span: str) -> str:
    """Convert the blades of one math span, leaving ``\\text{}`` pieces alone."""
    pieces: list[str] = []
    last: int = 0
    m: re.Match[str]
    for m in TEXT.finditer(span):
        pieces.append(convert_plain(span[last : m.start()]))
        pieces.append(m.group(0))
        last = m.end()
    pieces.append(convert_plain(span[last:]))
    return "".join(pieces)


def convert_plain(text: str) -> str:
    """The blade rewrite on math text with no ``\\text{}``."""
    text = MULTI.sub(lambda m: r"\mathbf{e}_{" + m.group(1) + "}", text)
    text = SUBSCRIPTED.sub(lambda m: r"\vec{\mathbf{e}}_{" + m.group(1) + "}", text)
    return SINGLE.sub(lambda m: r"\vec{\mathbf{e}}_" + (m.group(1) or m.group(2)), text)


def convert_markdown_cell(cell: str) -> str:
    """Convert every math span in one Markdown cell (comment-prefixed lines)."""
    return MATH.sub(lambda m: convert_math(m.group(0)), cell)


def main() -> None:
    path: str
    for path in sys.argv[1:]:
        p: pathlib.Path = pathlib.Path(path)
        source: str = p.read_text()
        cells: list[str] = re.split(r"(?=^# %%)", source, flags=re.M)
        out: str = "".join(
            convert_markdown_cell(c) if c.startswith("# %% [markdown]") else c for c in cells
        )
        changed: int = sum(a != b for a, b in zip(source.splitlines(), out.splitlines()))
        p.write_text(out)
        print(f"{path}: {changed} lines changed")


if __name__ == "__main__":
    main()


def bold_vectors(path: str, letters: str) -> None:
    """Rewrite the given single-letter vectors in a notebook's Markdown math as
    ``\\vec{\\mathbf{x}}``. A letter is left alone when it is part of a longer name
    or command (``\\sin``), already bold, or a coordinate (followed by ``_``)."""
    letter: re.Pattern[str] = re.compile(
        r"(?<![A-Za-z\\{])([" + letters + r"])(?![A-Za-z_{}(])"
    )

    def convert(span: str) -> str:
        pieces: list[str] = []
        last: int = 0
        m: re.Match[str]
        for m in TEXT.finditer(span):
            pieces.append(letter.sub(r"\\vec{\\mathbf{\1}}", span[last : m.start()]))
            pieces.append(m.group(0))
            last = m.end()
        pieces.append(letter.sub(r"\\vec{\\mathbf{\1}}", span[last:]))
        return "".join(pieces)

    p: pathlib.Path = pathlib.Path(path)
    source: str = p.read_text()
    cells: list[str] = re.split(r"(?=^# %%)", source, flags=re.M)
    p.write_text(
        "".join(
            MATH.sub(lambda m: convert(m.group(0)), c)
            if c.startswith("# %% [markdown]")
            else c
            for c in cells
        )
    )
