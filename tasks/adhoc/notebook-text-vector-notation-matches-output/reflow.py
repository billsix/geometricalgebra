#!/usr/bin/env python3
"""Reflow the Markdown paragraphs that ``rewrite.py`` pushed past the line limit.

Works on the percent-format notebooks and figure scripts under ``book/``. Within a
``# %% [markdown]`` cell, a paragraph is a run of ``# `` lines; a list item (``# - ``,
``# 1. ``) with its indented continuation lines is a paragraph of its own. Headings, tables,
``$$`` display lines and blank ``#`` lines are left as they are. Only a paragraph with a line
over the limit is rewrapped, as a whole, and never inside a ``$...$`` span or a backticked
span. Idempotent: a second run finds no long line.

Usage: ``python reflow.py`` (rewrites in place and prints each changed file).
"""

import pathlib
import re
import textwrap

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
LIMIT: int = 88
GLUE: str = "\x00"
ITEM: re.Pattern[str] = re.compile(r"# (\s*)(- |\d+\. )")
UNBREAKABLE: re.Pattern[str] = re.compile(r"\$[^$]+\$|`[^`]+`")


def wrap(lines: list[str]) -> list[str]:
    """Rewrap one paragraph if any of its lines is over the limit.

    Args:
        lines: the paragraph's lines, ``# `` prefixes and newlines included.

    Returns:
        list[str]: the paragraph, rewrapped or as it was.
    """
    if all(len(line.rstrip("\n")) <= LIMIT for line in lines):
        return lines
    item: re.Match[str] | None = ITEM.match(lines[0])
    first: str = "# " if item is None else "# " + item.group(1) + item.group(2)
    rest: str = "# " if item is None else "# " + item.group(1) + " " * len(item.group(2))
    words: str = " ".join(
        [lines[0][len(first) :].strip()] + [line[len(rest) :].strip() for line in lines[1:]]
    )
    glued: str = UNBREAKABLE.sub(lambda m: m.group(0).replace(" ", GLUE), words)
    wrapped: list[str] = textwrap.wrap(
        glued,
        width=LIMIT,
        initial_indent=first,
        subsequent_indent=rest,
        break_long_words=False,
        break_on_hyphens=False,
    )
    return [line.replace(GLUE, " ") + "\n" for line in wrapped]


def reflow(text: str) -> str:
    """Reflow every over-long Markdown paragraph of one percent-format file.

    Args:
        text: the file's source.

    Returns:
        str: the reflowed source.
    """
    out: list[str] = []
    paragraph: list[str] = []
    markdown: bool = False

    def flush() -> None:
        out.extend(wrap(paragraph))
        paragraph.clear()

    for line in text.splitlines(keepends=True):
        body: str = line.rstrip("\n")
        is_text: bool = (
            markdown
            and body.startswith("# ")
            and not body.startswith(("# #", "# |", "# %%"))
            and "$$" not in body
        )
        if line.startswith("# %%"):
            markdown = "[markdown]" in line
        if is_text and ITEM.match(line):
            flush()
            paragraph.append(line)
        elif is_text:
            paragraph.append(line)
        else:
            flush()
            out.append(line)
    flush()
    return "".join(out)


def main() -> None:
    """Reflow the book's notebooks and figure scripts in place."""
    paths: list[pathlib.Path] = sorted(
        [*ROOT.glob("book/docs/notebooks/*.py"), *ROOT.glob("book/figures/epix/*.py")]
    )
    for path in paths:
        old: str = path.read_text()
        new: str = reflow(old)
        if new != old:
            path.write_text(new)
            print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
