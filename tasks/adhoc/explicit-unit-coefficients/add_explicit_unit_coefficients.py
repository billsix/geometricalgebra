#!/usr/bin/env python3
"""Make implicit unit coefficients explicit in GA basis-blade sums, for teaching clarity.

Rewrites a *bare* basis blade that is a **term in a multi-term sum** so its coefficient 1
is written out:

    e_1 + 3 * e_2      ->   1 * e_1 + 3 * e_2
    2 * e_1 + e_2      ->   2 * e_1 + 1 * e_2
    e_1 + e_2          ->   1 * e_1 + 1 * e_2   (all-bare sums too)
    a - e_2            ->   a - 1 * e_2         (negatives kept as the - operator)
    -e_1 + e_2         ->   -1 * e_1 + e_2      (a leading negated term)

It is behaviour-preserving (`1 * e_1 == e_1`) and idempotent (a second run changes nothing).

Scope / what it does NOT touch:
  * only terms inside a multi-term ``+`` / ``-`` sum -- a standalone blade (``[e_1, e_2]``,
    ``project(onto=e_1)``) is left bare (no sibling to be symmetric with);
  * a "basis blade" is a name ``e_<digits>`` (``e_1``, ``e_12``, ``e_123``) or an attribute
    ``<x>.e_<digits>`` (``g2.e_1``, ``Vector.e_1``, ``Bivector.e_12``, ``G.e_123``);
  * non-blade terms (``2 * e_1``, function calls, plain variables) are left alone -- so this
    never touches a non-GA ``+``.

HOW IT WORKS (why AST, not regex or ast.unparse): it parses each file to an AST to tell a
GA sum from any other ``+`` and to locate the exact blade terms, then does *targeted text
insertions* at those source positions -- so every bit of surrounding formatting, comments,
and blank lines is preserved (``ast.unparse`` would reformat the whole file).

USAGE (from the repo root):
    python tasks/adhoc/explicit-unit-coefficients/add_explicit_unit_coefficients.py tests notebooks

Pass files or directories; directories are searched recursively for ``*.py`` (skipping the
gitignored generated modules ``g1``-``g5`` and ``__pycache__``). Prints one line per changed
file with the number of blade terms made explicit. Run it a second time to confirm it is a
no-op (idempotence).
"""

import ast
import re
import sys
from pathlib import Path

# A basis blade is spelled e_<digits>: e_1 (vector), e_12 (bivector), e_123 (trivector), ...
BLADE_NAME = re.compile(r"^e_\d+$")


def blade_node(node: ast.AST) -> ast.AST | None:
    """Return the blade node if ``node`` is a bare basis blade, else None.

    A bare blade is either a Name ``e_1`` or an Attribute ``x.e_1`` -- NOT ``2 * e_1``
    (a BinOp), a call, or a plain variable.
    """
    if isinstance(node, ast.Name) and BLADE_NAME.match(node.id):
        return node
    if isinstance(node, ast.Attribute) and BLADE_NAME.match(node.attr):
        return node
    return None


def additive_leaves(node: ast.AST, leaves: list[ast.AST]) -> None:
    """Flatten a chain of ``+`` / ``-`` BinOps into its leaf terms (the operands that
    are not themselves ``+`` / ``-``)."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
        additive_leaves(node.left, leaves)
        additive_leaves(node.right, leaves)
    else:
        leaves.append(node)


def is_additive(node: ast.AST) -> bool:
    return isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub))


# Functions whose arguments are COORDINATE VECTORS (a parallelotope being measured), so
# a bare-blade argument reads inconsistently next to a scaled one -- unlike the
# direction/blade arguments of i()/plane_rotation()/project(onto=)/coefficient(), which
# stay bare.  (content()/signed_content() take a *list*, already covered by the list pass.)
MEASURE_CALLS = frozenset({"area", "volume", "signed_area", "signed_volume"})


def called_name(func: ast.AST) -> str | None:
    """The bare name of a called function -- ``area(...)`` or ``x.area(...)``."""
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def target_blade(term: ast.AST) -> ast.AST | None:
    """The blade node to prepend ``1 * `` to, for a term that is a bare blade or a
    negated bare blade (``-e_1`` -> the inner ``e_1`` so it reads ``-1 * e_1``)."""
    blade = blade_node(term)
    if blade is None and isinstance(term, ast.UnaryOp) and isinstance(term.op, ast.USub):
        blade = blade_node(term.operand)
    return blade


def targets_in_source(source: str) -> list[tuple[int, int]]:
    """Return the (lineno, col_offset) positions where ``1 * `` must be inserted.

    Each position is the start of a bare blade term of a multi-term sum (for a negated
    term ``-e_1`` it is the start of the inner blade, so the result reads ``-1 * e_1``).
    """
    tree = ast.parse(source)
    # Record each node's parent so we can find the TOP of each additive chain (a sum
    # whose parent is not itself a + / - -- flattening only from the top visits each
    # leaf once).
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child.parent = parent  # type: ignore[attr-defined]

    positions: set[tuple[int, int]] = set()
    for node in ast.walk(tree):
        # (a) terms of a multi-term sum -- flatten from the top of each + / - chain.
        if is_additive(node) and not is_additive(getattr(node, "parent", None)):
            leaves: list[ast.AST] = []
            additive_leaves(node, leaves)
            for leaf in leaves:
                blade = target_blade(leaf)
                if blade is not None:
                    positions.add((blade.lineno, blade.col_offset))
        # (b) elements of a list/tuple literal (a bare vector shown among coordinate
        # vectors, e.g. content([e_1, 1 * e_1 + 1 * e_2])).  Call arguments are NOT
        # ast.Tuple/List, so blade *arguments* (project(onto=e_1), coefficient(e_1),
        # cls.i(e_1, e_2)) are left bare.
        if isinstance(node, (ast.List, ast.Tuple)):
            for element in node.elts:
                blade = target_blade(element)
                if blade is not None:
                    positions.add((blade.lineno, blade.col_offset))
        # (c) coordinate-vector ARGUMENTS of a measure call (area/volume/signed_*).  Only
        # the args (not the method receiver, which would need parens -- none are bare).
        if isinstance(node, ast.Call) and called_name(node.func) in MEASURE_CALLS:
            for arg in [*node.args, *(kw.value for kw in node.keywords)]:
                blade = target_blade(arg)
                if blade is not None:
                    positions.add((blade.lineno, blade.col_offset))
    return sorted(positions)


def rewrite(source: str) -> tuple[str, int]:
    """Return (new_source, number_of_insertions)."""
    positions = targets_in_source(source)
    if not positions:
        return source, 0
    lines = source.splitlines(keepends=True)
    # col_offset is a UTF-8 *byte* offset, so edit each line as bytes to stay correct on
    # lines that contain multibyte characters.  Insert right-to-left within a line so
    # earlier offsets are unaffected.
    by_line: dict[int, list[int]] = {}
    for lineno, col in positions:
        by_line.setdefault(lineno, []).append(col)
    for lineno, cols in by_line.items():
        raw = lines[lineno - 1].encode("utf-8")
        for col in sorted(cols, reverse=True):
            raw = raw[:col] + b"1 * " + raw[col:]
        lines[lineno - 1] = raw.decode("utf-8")
    return "".join(lines), len(positions)


# A single-line doctest input: "    >>> a = e_1 + 3 * e_2"
DOCTEST_PROMPT = re.compile(r"^(\s*)>>> (.*)$")


def rewrite_doctests(source: str) -> tuple[str, int]:
    """Apply the same rewrite to the code inside single-line ``>>>`` doctest lines.

    The AST pass above only sees real code, not the ``>>>`` lines inside docstrings.
    Here we re-run the rewriter on each *complete, single-line* ``>>>`` statement (a
    continuation-line ``...`` statement won't parse alone, so it is left untouched --
    none of the repo's blade sums span continuations).  Expected-output lines (no
    ``>>>``) are never matched.
    """
    lines = source.splitlines(keepends=True)
    count = 0
    for i, line in enumerate(lines):
        match = DOCTEST_PROMPT.match(line.rstrip("\n"))
        if match is None:
            continue
        indent, code = match.group(1), match.group(2)
        try:
            ast.parse(code)  # a complete single-line statement?
        except SyntaxError:
            continue  # partial (has a ... continuation) or not parseable alone
        new_code, n = rewrite(code)
        if n:
            newline = "\n" if line.endswith("\n") else ""
            lines[i] = f"{indent}>>> {new_code}{newline}"
            count += n
    return "".join(lines), count


def iter_py_files(argv: list[str]) -> list[Path]:
    out: list[Path] = []
    for arg in argv:
        path = Path(arg)
        candidates = [path] if path.is_file() else sorted(path.rglob("*.py"))
        for candidate in candidates:
            parts = set(candidate.parts)
            if "__pycache__" in parts:
                continue
            # skip the gitignored generated modules g1..g5
            if re.fullmatch(r"g[1-5]", candidate.stem):
                continue
            out.append(candidate)
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: add_explicit_unit_coefficients.py <file-or-dir> ...", file=sys.stderr)
        return 2
    total = 0
    for path in iter_py_files(argv):
        source = path.read_text(encoding="utf-8")
        try:
            new_source, n = rewrite(source)  # real code
        except SyntaxError as exc:
            print(f"SKIP (parse error) {path}: {exc}", file=sys.stderr)
            continue
        new_source, n_doctest = rewrite_doctests(new_source)  # >>> lines in docstrings
        n += n_doctest
        if n:
            path.write_text(new_source, encoding="utf-8")
            print(f"{path}: {n} unit coefficient(s) made explicit")
            total += n
    print(f"total: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
