"""Wrap symbolic coefficients in the algebra's scalar constructor.

For each statement pyright flagged in ``data/expr-sites-before.tsv`` (the snapshot
``discover.sh`` wrote before the rewrite), find every product ``coefficient * basis``
whose right operand is a basis blade or the unit (``e_1``, ``g2.Vector.e_2``,
``Bivector.e_12``, ``gn.one`` ...) and whose left operand is not a number literal, and
wrap the left operand:

- ``Scalar(s_1) * e_1`` when the blade comes from a graded module (``gacalc.g2`` /
  ``gacalc.g3``), spelled ``g2.Scalar(...)`` when the file reaches the module as ``g2``;
- ``Gn.from_real(s_1) * e_1`` when it comes from ``gacalc.gn``.

The edit is a text splice at the AST node's own offsets, so formatting and comments
survive; ``make format`` reflows afterwards.  A ``Scalar`` the file does not import yet
is added to its ``from gacalc.gN import`` line.  Running it twice changes nothing: an
operand that is already a ``Scalar(...)`` or ``.from_real(...)`` call is left alone.

Usage, from anywhere::

    python3 tasks/adhoc/emacs-pyright-scalar-and-sympy-typing/wrap_coefficients.py
"""

import ast
import pathlib
import re
import sys

HERE: pathlib.Path = pathlib.Path(__file__).resolve().parent
REPO: pathlib.Path = HERE.parents[2]
BLADE: re.Pattern[str] = re.compile(r"^(e_\d+|one)$")


def dotted(node: ast.expr) -> list[str] | None:
    """The parts of a dotted name (``g2.Vector.e_1`` → ``["g2", "Vector", "e_1"]``).

    Args:
        node: an expression node.

    Returns:
        list[str] | None: the parts, or ``None`` for anything but a dotted name.
    """
    match node:
        case ast.Name(id=name):
            return [name]
        case ast.Attribute(value=value, attr=attr):
            head: list[str] | None = dotted(value)
            return None if head is None else [*head, attr]
        case _:
            return None


def imported_modules(tree: ast.Module) -> dict[str, str]:
    """Map each name a file binds from, or as, a gacalc algebra module to that module.

    ``from gacalc.g3 import Vector, e_1`` maps ``Vector`` and ``e_1`` to ``g3``;
    ``import gacalc.g2 as g2`` maps ``g2`` to ``g2``.

    Args:
        tree: the parsed file.

    Returns:
        dict[str, str]: bound name → algebra module (``g2``, ``g3`` or ``gn``).
    """
    bound: dict[str, str] = {}
    node: ast.AST
    for node in ast.walk(tree):
        match node:
            case ast.ImportFrom(module=str(module), names=names) if re.fullmatch(
                r"gacalc\.(g[23]|gn)", module
            ):
                alias: ast.alias
                for alias in names:
                    bound[alias.asname or alias.name] = module.split(".")[1]
            case ast.ImportFrom(module="gacalc", names=names):
                for alias in names:
                    if re.fullmatch(r"g[23]|gn", alias.name):
                        bound[alias.asname or alias.name] = alias.name
            case ast.Import(names=names):
                for alias in names:
                    found: re.Match[str] | None = re.fullmatch(
                        r"gacalc\.(g[23]|gn)", alias.name
                    )
                    if found is not None and alias.asname is not None:
                        bound[alias.asname] = found.group(1)
            case _:
                pass
    return bound


def wrapper_for(parts: list[str], bound: dict[str, str]) -> tuple[str, str | None]:
    """The scalar-constructor spelling for a blade, and the import it needs.

    Args:
        parts: the blade's dotted name.
        bound: the file's ``imported_modules``.

    Returns:
        tuple[str, str | None]: the callable to wrap with, and the module whose
        ``from gacalc.<module> import`` line must gain ``Scalar`` (``None`` if none).

    Raises:
        KeyError: when the blade's module cannot be told from the imports.
    """
    module: str = bound[parts[0]]
    reached_as_module: bool = (
        parts[0] in ("g2", "g3", "gn") and bound.get(parts[0]) == parts[0]
    )
    match module, reached_as_module:
        case "gn", True:
            return f"{parts[0]}.Gn.from_real", None
        case "gn", False:
            return "Gn.from_real", None
        case _, True:
            return f"{parts[0]}.Scalar", None
        case _, False:
            return "Scalar", module
        case _:
            raise KeyError(parts)


def is_wrapped(node: ast.expr) -> bool:
    """Whether an operand is already a scalar-constructor call.

    Args:
        node: the left operand.

    Returns:
        bool: True for ``Scalar(...)``, ``g2.Scalar(...)`` or ``....from_real(...)``.
    """
    match node:
        case ast.Call(func=func):
            name: list[str] | None = dotted(func)
            return name is not None and name[-1] in ("Scalar", "from_real")
        case _:
            return False


def is_number(node: ast.expr) -> bool:
    """Whether an operand is a number literal, possibly negated.

    Args:
        node: the left operand.

    Returns:
        bool: True for ``2``, ``0.5``, ``-1``.
    """
    match node:
        case ast.Constant(value=int() | float()):
            return True
        case ast.UnaryOp(op=ast.USub(), operand=operand):
            return is_number(operand)
        case _:
            return False


def flagged_statements(tree: ast.Module, lines: set[int]) -> list[ast.stmt]:
    """The innermost simple statement holding each flagged line.

    pyright flags the line of the offending expression, which can sit inside a
    statement that starts earlier (a call spread over several lines).

    Args:
        tree: the parsed file.
        lines: the 1-based line numbers pyright flagged in it.

    Returns:
        list[ast.stmt]: the distinct statements found.
    """
    compound: tuple[type[ast.stmt], ...] = (
        ast.FunctionDef,
        ast.ClassDef,
        ast.For,
        ast.While,
        ast.If,
        ast.With,
        ast.Try,
        ast.Match,
    )
    simple: list[ast.stmt] = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.stmt) and not isinstance(node, compound)
    ]
    found: dict[int, ast.stmt] = {}
    line: int
    for line in lines:
        holding: list[ast.stmt] = [
            node
            for node in simple
            if node.end_lineno is not None and node.lineno <= line <= node.end_lineno
        ]
        if holding:
            innermost: ast.stmt = min(
                holding, key=lambda node: (node.end_lineno or 0) - node.lineno
            )
            found[id(innermost)] = innermost
    return list(found.values())


def rewrite(path: pathlib.Path, lines: set[int]) -> int:
    """Wrap the coefficients in one file's flagged statements.

    Args:
        path: the file.
        lines: the flagged line numbers.

    Returns:
        int: how many coefficients were wrapped.
    """
    source: str = path.read_text()
    tree: ast.Module = ast.parse(source)
    bound: dict[str, str] = imported_modules(tree)
    offsets: list[int] = [0]
    line_text: str
    for line_text in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line_text.encode()))
    data: bytes = source.encode()
    # (byte offset, text) insertions, applied from the end so offsets stay valid.
    inserts: list[tuple[int, str]] = []
    needed_imports: set[str] = set()
    statement: ast.stmt
    for statement in flagged_statements(tree, lines):
        node: ast.AST
        for node in ast.walk(statement):
            match node:
                case ast.BinOp(left=left, op=ast.Mult(), right=right):
                    parts: list[str] | None = dotted(right)
                    if (
                        parts is None
                        or BLADE.match(parts[-1]) is None
                        or is_number(left)
                        or is_wrapped(left)
                    ):
                        continue
                    if parts[0] not in bound:
                        # A local name (``e_1 = cls.basis_vector(1)``) or the module
                        # defining the blade: fixed by hand.
                        continue
                    wrapper: str
                    module: str | None
                    wrapper, module = wrapper_for(parts, bound)
                    if module is not None:
                        needed_imports.add(module)
                    assert left.end_lineno is not None
                    assert left.end_col_offset is not None
                    start: int = offsets[left.lineno - 1] + left.col_offset
                    end: int = offsets[left.end_lineno - 1] + left.end_col_offset
                    inserts.append((end, ")"))
                    inserts.append((start, wrapper + "("))
                case _:
                    pass
    if not inserts:
        return 0
    offset: int
    text: str
    for offset, text in sorted(inserts, key=lambda pair: pair[0], reverse=True):
        data = data[:offset] + text.encode() + data[offset:]
    result: str = data.decode()
    for module in sorted(needed_imports):
        result = add_scalar_import(result, module)
    path.write_text(result)
    return len(inserts) // 2


def add_scalar_import(source: str, module: str) -> str:
    """Add ``Scalar`` to a file's ``from gacalc.<module> import`` statement.

    Args:
        source: the file's text.
        module: ``g2`` or ``g3``.

    Returns:
        str: the text with ``Scalar`` imported (unchanged if it already was).
    """
    tree: ast.Module = ast.parse(source)
    node: ast.stmt
    for node in tree.body:
        match node:
            case ast.ImportFrom(module=found, names=names) if (
                found == f"gacalc.{module}"
            ):
                if any(alias.name == "Scalar" for alias in names):
                    return source
                lines: list[str] = source.splitlines(keepends=True)
                head: str = lines[node.lineno - 1]
                lines[node.lineno - 1] = (
                    head.replace(" import (", " import (Scalar, ", 1)
                    if " import (" in head
                    else head.replace(" import ", " import Scalar, ", 1)
                )
                return "".join(lines)
            case _:
                pass
    raise KeyError(f"no 'from gacalc.{module} import' line")


def main() -> None:
    """Rewrite every file the snapshot names and report the counts."""
    by_file: dict[str, set[int]] = {}
    row: str
    for row in (HERE / "data" / "expr-sites-before.tsv").read_text().splitlines():
        name: str
        line: str
        name, line, _ = row.split("\t", 2)
        by_file.setdefault(name, set()).add(int(line))
    total: int = 0
    name: str
    for name, flagged in sorted(by_file.items()):
        count: int = rewrite(REPO / name, flagged)
        total += count
        sys.stdout.write(f"{count:3d}  {name}\n")
    sys.stdout.write(f"{total:3d}  total\n")


if __name__ == "__main__":
    main()
