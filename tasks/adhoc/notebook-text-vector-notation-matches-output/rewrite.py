#!/usr/bin/env python3
"""Rewrite the book's math to typeset vectors the way gacalc's output does.

The output (``blade_latex`` in ``src/gacalc/base.py``) writes a basis vector
``\\vec{\\mathbf{e}}_1`` and a higher blade ``\\mathbf{e}_{12}``. This script rewrites, inside math
only:

- ``\\vec{a}`` to ``\\vec{\\mathbf{a}}`` and ``\\hat{a}`` to ``\\hat{\\mathbf{a}}``;
- ``e_1`` (or ``e_i``) to ``\\vec{\\mathbf{e}}_1``, ``e_{12}`` to ``\\mathbf{e}_{12}``, and the juxtaposed
  ``e_1 e_2`` (the name of a plane) to ``\\mathbf{e}_{12}``;
- in a book notebook's Markdown and figure labels, a bare letter that the notebook binds to a vector
  (``a: Vector = ...``, or a lowercase ``MultiVectorBase``: by the Hestenes naming rule a
  lowercase name holds a vector) to ``\\vec{\\mathbf{a}}``. A letter bound with an index
  (``v_1: Vector``) is a vector also when written with a subscript or superscript (``v_1``,
  ``a^1``); otherwise a subscripted letter is a coordinate (``a_1``) and stays.

Math is ``$...$`` / ``$$...$$`` in notebook Markdown and in figure-label strings, and
``:math:`...``` / ``.. math::`` blocks in ``.rst`` pages. Run from anywhere; paths are taken from
the repository root. Idempotent: text already in the bold form is copied as it is.

Usage: ``python rewrite.py`` (rewrites in place and prints each changed file).
"""

import pathlib
import re
from collections.abc import Callable

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]

# Pages whose juxtaposed e_i e_j are products being slid, not the name of a plane
# (CLAUDE.md's "Math notation for readers" exempts blade-square-sign.rst's diagrams).
KEEP_JUXTAPOSED: frozenset[str] = frozenset({"blade-square-sign.rst"})

# Letters the binding scan gets wrong, per notebook: (extra vectors, not vectors).
OVERRIDES: dict[str, tuple[frozenset[str], frozenset[str]]] = {
    # in_plane's argument v, and translate's input point v.
    "proof-cross.py": (frozenset({"v"}), frozenset()),
    "vector-addition.py": (frozenset({"v"}), frozenset()),
    # The prose's remainder r is a vector; the code's r is a coordinate symbol.
    "frame-qr-2d.py": (frozenset({"r"}), frozenset()),
}

TOKEN: re.Pattern[str] = re.compile(
    r"""
    (?P<done>\\(?:vec|hat)\{\\mathbf\{[^{}]*\}\}|\\mathbf\{e\})
  | (?P<verbatim>\\(?:text|operatorname|mathrm|mathit|textrm|mathbf)\{[^{}]*\})
  | (?P<accent>\\(?P<accent_name>vec|hat)\{(?P<accent_arg>[^{}]*)\})
  | (?P<command>\\[A-Za-z]+)
  | (?P<pair>e_(?P<first>\d)\ +e_(?P<second>\d)(?![\d}]))
  | (?P<blade>e_(?:\{(?P<braced>\d+|[a-z])\}|(?P<single>\d|[a-z](?![A-Za-z]))))
  | (?P<identifier>[A-Za-z]+)
  | (?P<other>.)
    """,
    re.VERBOSE | re.DOTALL,
)


def rewrite_math(
    math: str,
    vectors: frozenset[str],
    indexed: frozenset[str],
    keep_juxtaposed: bool,
) -> str:
    """Rewrite one math span's vectors and basis blades to the output's notation.

    Args:
        math: the LaTeX between the delimiters.
        vectors: letters that name a vector when written bare.
        indexed: letters that name a vector when written with a subscript or superscript.
        keep_juxtaposed: leave ``e_1 e_2`` as two vectors instead of one blade.

    Returns:
        str: the rewritten LaTeX.
    """
    pieces: list[str] = []
    for match in TOKEN.finditer(math):
        token: str = match.group(0)
        # What follows the letter once its primes are skipped: b''_2 is a coordinate.
        follows: str = math[match.end() :].lstrip("'")[:1]
        after_script: bool = bool(pieces) and pieces[-1] in ("_", "^")
        match match.lastgroup:
            case "accent":
                pieces.append(
                    r"\%s{\mathbf{%s}}"
                    % (match.group("accent_name"), match.group("accent_arg"))
                )
            case "pair" if keep_juxtaposed:
                pieces.append(
                    r"\vec{\mathbf{e}}_%s \vec{\mathbf{e}}_%s"
                    % (match.group("first"), match.group("second"))
                )
            case "pair":
                pieces.append(
                    r"\mathbf{e}_{%s%s}" % (match.group("first"), match.group("second"))
                )
            case "blade" if match.group("single") is not None:
                pieces.append(r"\vec{\mathbf{e}}_" + match.group("single"))
            case "blade" if len(match.group("braced")) == 1:
                pieces.append(r"\vec{\mathbf{e}}_{" + match.group("braced") + "}")
            case "blade":
                pieces.append(r"\mathbf{e}_{" + match.group("braced") + "}")
            case "identifier" if len(token) == 1 and (
                (token in indexed and follows in ("_", "^"))
                or (token in vectors and follows != "_")
            ):
                bold: str = r"\vec{\mathbf{" + token + "}}"
                pieces.append("{" + bold + "}" if after_script else bold)
            case "done" | "verbatim" | "command" | "identifier" | "other":
                pieces.append(token)
            case _:
                raise ValueError(f"unexpected token {token!r} in {math!r}")
    return "".join(pieces)


def notebook_vectors(text: str, name: str) -> tuple[frozenset[str], frozenset[str]]:
    """The letters a notebook binds to vectors: (bare, indexed).

    Args:
        text: the notebook source.
        name: its file name, the key into ``OVERRIDES``.

    Returns:
        tuple[frozenset[str], frozenset[str]]: letters that are vectors bare, and letters
        that are vectors with an index.
    """
    bindings: list[str] = re.findall(
        r"^(\w+): (?:g[23]\.)?(?:Vector|MultiVectorBase)\b", text, re.M
    )
    bare: set[str] = {b for b in bindings if re.fullmatch(r"[a-z]", b)}
    indexed: set[str] = {b[0] for b in bindings if re.fullmatch(r"[a-z]_\d+", b)}
    extra, excluded = OVERRIDES.get(name, (frozenset(), frozenset()))
    return frozenset((bare | extra) - excluded), frozenset(indexed - excluded)


def rewrite_dollars(
    line: str, rewrite: Callable[[str], str], in_display: bool
) -> tuple[str, bool]:
    """Rewrite every ``$...$`` / ``$$...$$`` span of one Markdown line.

    Args:
        line: the line, ``# `` prefix included.
        rewrite: the math rewrite to apply.
        in_display: whether a ``$$`` block opened on an earlier line is still open.

    Returns:
        tuple[str, bool]: the rewritten line, and whether a ``$$`` block is open after it.
    """
    parts: list[str] = re.split(r"(\$\$?)", line)
    out: list[str] = []
    inline: bool = False
    for part in parts:
        match part:
            case "$$":
                in_display = not in_display
                out.append(part)
            case "$" if not in_display:
                inline = not inline
                out.append(part)
            case _ if in_display or inline:
                out.append(rewrite(part))
            case _:
                out.append(part)
    return "".join(out), in_display


STRING: re.Pattern[str] = re.compile(
    r'(?<![A-Za-z])(?P<prefix>[rRfF]{0,2})"(?P<body>[^"\n]*\$[^"\n]*)"'
)


def split_fstring(body: str) -> tuple[str, list[str]]:
    """Unescape an f-string body, putting each format field aside as a placeholder.

    ``{{`` and ``}}`` become literal braces; ``{expression}`` (nesting allowed) becomes
    ``\\x01N\\x02``, the index of the field in the returned list.

    Args:
        body: the f-string's source between its quotes.

    Returns:
        tuple[str, list[str]]: the unescaped text and the fields, braces included.
    """
    text: list[str] = []
    fields: list[str] = []
    i: int = 0
    while i < len(body):
        pair: str = body[i : i + 2]
        if pair in ("{{", "}}"):
            text.append(pair[0])
            i += 2
        elif body[i] == "{":
            depth: int = 0
            j: int = i
            while True:
                depth += {"{": 1, "}": -1}.get(body[j], 0)
                j += 1
                if depth == 0:
                    break
            text.append("\x01" + str(len(fields)) + "\x02")
            fields.append(body[i:j])
            i = j
        else:
            text.append(body[i])
            i += 1
    return "".join(text), fields


def rewrite_label(match: re.Match[str], rewrite: Callable[[str], str]) -> str:
    """Rewrite the math in one figure-label string literal of a notebook's code.

    In an f-string the rewrite's braces are doubled and the format fields
    (``{index + 1}``) are kept as they are. A string that now holds a backslash command
    gets an ``r`` prefix, since ``"\\v"`` is an escape; no plain-string label held a
    backslash before the rewrite. A string the rewrite does not change is left as it is.

    Args:
        match: a ``STRING`` match.
        rewrite: the math rewrite to apply.

    Returns:
        str: the rewritten literal.
    """
    prefix: str = match.group("prefix")
    is_f: bool = "f" in prefix.lower()
    text, fields = (
        split_fstring(match.group("body")) if is_f else (match.group("body"), [])
    )
    new: str = re.sub(r"\$[^$]+\$", lambda m: rewrite(m.group(0)), text)
    if new == text:
        return match.group(0)
    if is_f:
        new = new.replace("{", "{{").replace("}", "}}")
        new = re.sub("\x01(\\d+)\x02", lambda m: fields[int(m.group(1))], new)
    if "\\" in new and "r" not in prefix.lower():
        prefix = "r" + prefix
    return prefix + '"' + new + '"'


def rewrite_notebook(path: pathlib.Path) -> str:
    """Rewrite a percent-format notebook's Markdown math and its figure-label math.

    Args:
        path: the notebook.

    Returns:
        str: the rewritten source.
    """
    text: str = path.read_text()
    vectors, indexed = notebook_vectors(text, path.name)

    def prose(math: str) -> str:
        return rewrite_math(math, vectors, indexed, keep_juxtaposed=False)


    out: list[str] = []
    markdown: bool = False
    in_display: bool = False
    for line in text.splitlines(keepends=True):
        if line.startswith("# %%"):
            markdown = "[markdown]" in line
            out.append(line)
        elif markdown:
            rewritten, in_display = rewrite_dollars(line, prose, in_display)
            out.append(rewritten)
        else:
            out.append(STRING.sub(lambda m: rewrite_label(m, prose), line))
    return "".join(out)


def rewrite_figure_script(path: pathlib.Path) -> str:
    """Rewrite the math in a figure script's label strings.

    Args:
        path: the script.

    Returns:
        str: the rewritten source.
    """
    return re.sub(
        r"\$[^$\"\n]+\$",
        lambda m: rewrite_math(m.group(0), frozenset(), frozenset(), False),
        path.read_text(),
    )


def rewrite_rst(path: pathlib.Path) -> str:
    """Rewrite a page's ``:math:`` roles and ``.. math::`` blocks.

    Args:
        path: the page.

    Returns:
        str: the rewritten source.
    """
    keep: bool = path.name in KEEP_JUXTAPOSED

    def math(text: str) -> str:
        return rewrite_math(text, frozenset(), frozenset(), keep)

    out: list[str] = []
    block_indent: int | None = None
    for line in path.read_text().splitlines(keepends=True):
        indent: int = len(line) - len(line.lstrip())
        if block_indent is not None and line.strip() and indent <= block_indent:
            block_indent = None
        if block_indent is not None:
            out.append(math(line))
        else:
            out.append(
                re.sub(
                    r":math:`([^`]*)`",
                    lambda m: ":math:`" + math(m.group(1)) + "`",
                    line,
                )
            )
        if re.match(r"\s*\.\. math::", line):
            block_indent = indent
    return "".join(out)


def main() -> None:
    """Rewrite every book notebook, page and figure script in place."""
    jobs: list[tuple[pathlib.Path, Callable[[pathlib.Path], str]]] = [
        *((p, rewrite_notebook) for p in sorted(ROOT.glob("book/docs/notebooks/*.py"))),
        *((p, rewrite_rst) for p in sorted(ROOT.glob("book/docs/*.rst"))),
        *((p, rewrite_figure_script) for p in sorted(ROOT.glob("book/figures/epix/*.py"))),
    ]
    for path, rewrite in jobs:
        new: str = rewrite(path)
        if new != path.read_text():
            path.write_text(new)
            print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
