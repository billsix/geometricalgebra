# Copyright (c) 2025-2026 William Emerison Six
# SPDX-License-Identifier: LGPL-2.1-only
"""Reflow each Markdown paragraph that has a line over 88 columns (one-shot).

Usage: ``python reflow_long_markdown.py <notebook.py>...``. A paragraph is a run of
``# text`` comment lines; headings, list items and display math (``$$``) are left
alone and printed instead, for a hand fix. Words are never split, and an inline
``$...$`` span is kept on one line.
"""

import pathlib
import sys

WIDTH: int = 88
PREFIX: str = "# "


def is_plain(line: str) -> bool:
    """A Markdown prose line that may be reflowed."""
    if not line.startswith(PREFIX) or line.startswith("# %%"):
        return False
    text: str = line[len(PREFIX) :]
    return not (
        text.startswith(("#", "- ", "$$", ">", "|"))
        or text[:1].isdigit()
        or text.startswith(" ")
    )


def tokens(text: str) -> list[str]:
    """Space-separated words, with each inline ``$...$`` span joined into one token."""
    out: list[str] = []
    pending: list[str] = []
    word: str
    for word in text.split():
        pending.append(word)
        if " ".join(pending).count("$") % 2 == 0:
            out.append(" ".join(pending))
            pending = []
    if pending:
        out.append(" ".join(pending))
    return out


def wrap(words: list[str]) -> list[str]:
    """Greedy fill of ``words`` into ``# ``-prefixed lines of at most ``WIDTH``."""
    lines: list[str] = []
    current: str = PREFIX
    word: str
    for word in words:
        candidate: str = word if current == PREFIX else current + " " + word
        candidate = PREFIX + word if current == PREFIX else candidate
        if len(candidate) > WIDTH and current != PREFIX:
            lines.append(current)
            current = PREFIX + word
        else:
            current = candidate
    lines.append(current)
    return lines


def reflow(lines: list[str], name: str) -> list[str]:
    """``lines`` with every over-long plain paragraph reflowed."""
    out: list[str] = []
    index: int = 0
    while index < len(lines):
        if not is_plain(lines[index]):
            if len(lines[index]) > WIDTH:
                print(f"{name}:{index + 1}: not reflowed, fix by hand")  # noqa: T201
            out.append(lines[index])
            index += 1
            continue
        end: int = index
        while end < len(lines) and is_plain(lines[end]):
            end += 1
        paragraph: list[str] = lines[index:end]
        if any(len(line) > WIDTH for line in paragraph):
            text: str = " ".join(line[len(PREFIX) :] for line in paragraph)
            out.extend(wrap(tokens(text)))
        else:
            out.extend(paragraph)
        index = end
    return out


def main() -> int:
    """Reflow each named notebook in place."""
    argument: str
    for argument in sys.argv[1:]:
        path: pathlib.Path = pathlib.Path(argument)
        lines: list[str] = path.read_text().splitlines()
        path.write_text("\n".join(reflow(lines, path.name)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
