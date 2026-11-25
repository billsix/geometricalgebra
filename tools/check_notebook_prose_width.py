#!/usr/bin/env python3
"""Notebook prose stays within 88 columns -- check or fix.

The notebooks (``notebooks/``) and the figure scripts are exempt from ruff's E501
(``pyproject.toml``): their Markdown math writes vectors as ``\\vec{\\mathbf{a}}``, so
one inline ``$...$`` span or a heading can pass 88 columns and cannot be broken. This
tool checks the rest of the prose. Within a ``# %% [markdown]`` cell, a paragraph is a
run of ``# `` lines; a list item (``# - ``, ``# 1. ``) with its indented continuation
lines is a paragraph of its own. Headings, tables, ``$$`` display lines and blank ``#``
lines are not paragraphs.

A paragraph is reported when one of its lines passes the limit and rewrapping the whole
paragraph would change it. The rewrap never breaks inside a ``$...$`` or backticked
span, so a paragraph whose only long line is such a span on a line of its own is already
as narrow as it can be, and is not reported. ``--fix`` rewraps each reported paragraph
as a whole (never just the long line), which is idempotent: a second run reports
nothing.

Usage: ``python tools/check_notebook_prose_width.py [--fix] [PATH ...]``
(default: ``notebooks/*.py`` and ``book/figures/epix/*.py``). Exit 1 if any paragraph
is reported (after ``--fix``, if any could not be fixed).
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
import textwrap
from collections.abc import Sequence
from dataclasses import dataclass

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_GLOBS: tuple[str, ...] = (
    "notebooks/*.py",
    "book/figures/epix/*.py",
)
LIMIT: int = 88
# Stands in for a space inside an unbreakable span while textwrap runs.
GLUE: str = "\x00"
ITEM: re.Pattern[str] = re.compile(r"# (\s*)(- |\d+\. )")
UNBREAKABLE: re.Pattern[str] = re.compile(r"\$[^$]+\$|`[^`]+`")


@dataclass(frozen=True)
class Paragraph:
    """One Markdown paragraph of a percent-format file.

    Attributes:
        first_line: its 1-based line number.
        lines: its lines, ``# `` prefixes and newlines included.
    """

    first_line: int
    lines: list[str]


def split(text: str) -> list[Paragraph | str]:
    """Split a percent-format file into Markdown paragraphs and the lines between them.

    Args:
        text: the file's source.

    Returns:
        list[Paragraph | str]: the file in order; joining the paragraphs' lines and the
        strings gives the source back.
    """
    pieces: list[Paragraph | str] = []
    current: list[str] = []
    start: int = 0
    markdown: bool = False

    def flush() -> None:
        if current:
            pieces.append(Paragraph(first_line=start, lines=list(current)))
            current.clear()

    number: int
    line: str
    for number, line in enumerate(text.splitlines(keepends=True), start=1):
        body: str = line.rstrip("\n")
        if line.startswith("# %%"):
            markdown = "[markdown]" in line
        is_text: bool = (
            markdown
            and body.startswith("# ")
            and not body.startswith(("# #", "# |", "# %%"))
            and "$$" not in body
        )
        if is_text and (ITEM.match(line) or not current):
            flush()
            start = number
            current.append(line)
        elif is_text:
            current.append(line)
        else:
            flush()
            pieces.append(line)
    flush()
    return pieces


def check_file(path: pathlib.Path, fix: bool) -> list[str]:
    """Check one file, rewriting it when ``fix`` is set.

    Args:
        path: the file.
        fix: rewrap the reported paragraphs in place.

    Returns:
        list[str]: one ``path:line: message`` per paragraph still too wide.
    """

    def rewrap(lines: Sequence[str]) -> list[str]:
        """Rewrap a paragraph to the limit, as a whole, keeping its list-item indent.

        Args:
            lines: the paragraph's lines, ``# `` prefixes and newlines included.

        Returns:
            list[str]: the rewrapped lines.
        """
        item: re.Match[str] | None = ITEM.match(lines[0])
        first: str = "# " if item is None else "# " + item.group(1) + item.group(2)
        rest: str = (
            "# " if item is None else "# " + item.group(1) + " " * len(item.group(2))
        )
        words: str = " ".join(
            [lines[0][len(first) :].strip()]
            + [line[len(rest) :].strip() for line in lines[1:]]
        )
        glued: str = UNBREAKABLE.sub(lambda m: m.group(0).replace(" ", GLUE), words)
        return [
            line.replace(GLUE, " ") + "\n"
            for line in textwrap.wrap(
                glued,
                width=LIMIT,
                initial_indent=first,
                subsequent_indent=rest,
                break_long_words=False,
                break_on_hyphens=False,
            )
        ]

    def needs_rewrap(paragraph: Paragraph) -> bool:
        """Whether a paragraph has a line over the limit that rewrapping would change.

        Args:
            paragraph: the paragraph.

        Returns:
            bool: ``True`` when it should be reported.
        """
        return any(len(line.rstrip("\n")) > LIMIT for line in paragraph.lines) and (
            rewrap(paragraph.lines) != paragraph.lines
        )

    pieces: list[Paragraph | str] = split(path.read_text())
    reported: list[Paragraph] = [
        piece
        for piece in pieces
        if isinstance(piece, Paragraph) and needs_rewrap(piece)
    ]
    if fix and reported:
        path.write_text(
            "".join(
                "".join(rewrap(piece.lines) if needs_rewrap(piece) else piece.lines)
                if isinstance(piece, Paragraph)
                else piece
                for piece in pieces
            )
        )
        return check_file(path, fix=False)
    return [
        f"{path.relative_to(ROOT)}:{paragraph.first_line}: paragraph passes {LIMIT} "
        "columns; rewrap it (--fix)"
        for paragraph in reported
    ]


def main(argv: Sequence[str] | None = None) -> int:
    """Check (or fix) the given files, or the notebooks and figure scripts.

    Args:
        argv: the command-line arguments (``None`` reads ``sys.argv``).

    Returns:
        int: 0 when every paragraph fits, else 1.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0]
    )
    parser.add_argument("--fix", action="store_true", help="rewrap in place")
    parser.add_argument("paths", nargs="*", type=pathlib.Path)
    args: argparse.Namespace = parser.parse_args(argv)
    paths: list[pathlib.Path] = [path.resolve() for path in args.paths] or sorted(
        path for pattern in DEFAULT_GLOBS for path in ROOT.glob(pattern)
    )
    problems: list[str] = [
        problem for path in paths for problem in check_file(path, fix=args.fix)
    ]
    problem: str
    for problem in problems:
        print(problem)  # noqa: T201 -- the report is this tool's output
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
