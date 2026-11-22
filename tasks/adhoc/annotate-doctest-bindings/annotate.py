#!/usr/bin/env python3
"""Give the untyped bindings of docstring examples a type, read from a run of the example.

For each hand-written module named in ``MODULES`` the script finds every docstring, runs its
``>>>`` examples in order in a copy of the module's namespace (as ``pytest --doctest-modules``
does), and for every bare ``name = expr`` it records the runtime type of ``name``. It then
rewrites the source:

- ``>>> name = expr`` becomes ``>>> name: T = expr``;
- ``>>> a, b = expr`` keeps its line and gains ``>>> a: T`` / ``>>> b: T`` lines above it.

``T`` is the class name when the example's namespace binds it (``Vector``), a module-qualified
name when the namespace binds only the module (``g3.Bivector``), and ``sympy.Symbol`` /
``sympy.Expr`` for sympy values. A value the script cannot name (a function, a generic
container of mixed types, a ``ComposableFunction``) is printed as UNRESOLVED and left alone,
to be typed by hand. A type whose name the example's namespace lacks fails the doctest, so
``make test`` after the run finds it.

Run from the repository root (needs ``src/gacalc/g2.py``, ``g3.py``: ``make generate``). Running
it again finds nothing bare and changes nothing.

Usage: ``python tasks/adhoc/annotate-doctest-bindings/annotate.py``
"""

from __future__ import annotations

import ast
import doctest
import importlib
import pathlib
import sys
import types
from dataclasses import dataclass
from typing import Any

REPO: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

MODULES: tuple[str, ...] = (
    "gacalc.base",
    "gacalc.transforms",
    "gacalc.functions",
    "gacalc.measure",
    "gacalc.frame",
    "gacalc.nbdisplay",
    "gacalc.standardposition",
    "gacalc.vectorcalc",
    "gacalc.gn",
    "gacalc.cayley.cayleygraph",
    "gacalc.cayley.cayleyscene",
)


# Bindings the run cannot name: a plain function, a dict, a container of a type the example
# never imports. Each is written by hand, with the type the code around it would use.
MANUAL: tuple[tuple[str, str, str], ...] = (
    (
        "src/gacalc/base.py",
        '>>> ijk = {(1,): r"\\mathbf{i}", (2,): r"\\mathbf{j}"}',
        '>>> ijk: dict[Blade, str] = {(1,): r"\\mathbf{i}", (2,): r"\\mathbf{j}"}',
    ),
    (
        "src/gacalc/transforms.py",
        ">>> f = projection_rotation(e_1, e_2)",
        ">>> f: MultiVectorFn = projection_rotation(e_1, e_2)",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> turn = bivector_rotation(Vector.i(Vector.e_1, Vector.e_2))",
        ">>> turn: typing.Callable[[Real], InvertibleFunction[MultiVectorBase]] = (\n"
        "        ...     bivector_rotation(Vector.i(Vector.e_1, Vector.e_2))\n"
        "        ... )",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> turn = plane_rotation(Vector.e_1, Vector.e_2)",
        ">>> turn: typing.Callable[[Real], InvertibleFunction[Vector]] = plane_rotation(\n"
        "        ...     Vector.e_1, Vector.e_2\n"
        "        ... )",
    ),
    (
        "src/gacalc/gl/grapher3d.py",
        '>>> flat = Surface(fn=lambda x, y: 0.0, label="flat", color=white, latex="0")',
        '>>> flat: Surface = Surface(fn=lambda x, y: 0.0, label="flat", color=white, latex="0")',
    ),
    (
        "src/gacalc/gl/grapher3d.py",
        '>>> tilt = Surface(fn=lambda x, y: x, label="tilt", color=white, latex="x")\n'
        "    >>> positions, colors = build_solid(tilt, 6.0, 6.0)",
        '>>> tilt: Surface = Surface(fn=lambda x, y: x, label="tilt", color=white, latex="x")\n'
        "    >>> positions: np.ndarray\n"
        "    >>> colors: np.ndarray\n"
        "    >>> positions, colors = build_solid(tilt, 6.0, 6.0)",
    ),
    (
        "tools/gen_specialized.py",
        ">>> a = Gn.from_blade_dict(",
        ">>> a: Gn = Gn.from_blade_dict(",
    ),
    (
        "tools/gen_specialized.py",
        ">>> b = Gn.from_blade_dict(",
        ">>> b: Gn = Gn.from_blade_dict(",
    ),
    (
        "tools/gen_specialized.py",
        "    >>> d = (a * b).to_blade_dict()",
        "    >>> from gacalc.base import Blade, Real\n"
        "    >>> d: dict[Blade, Real] = (a * b).to_blade_dict()",
    ),
)


# The run names a generic by its class only (``InvertibleFunction``), which is a bare generic,
# and cannot tell a result type from a narrower one. Each replacement writes the parameter the
# code around the example would use (the function's declared return type, or the vector type
# the example builds), and fixes the annotations ``ty`` rejected when the examples were
# extracted (``tasks/adhoc/annotate-doctest-bindings/extract_examples.py``). Applied in
# order, the first match only, so two docstrings with the same line can differ.
REFINE: tuple[tuple[str, str, str], ...] = (
    (
        "src/gacalc/functions.py",
        ">>> double: ComposableFunction = ",
        ">>> double: ComposableFunction[float] = ",
    ),
    (
        "src/gacalc/functions.py",
        ">>> double: ComposableFunction = ",
        ">>> double: ComposableFunction[float] = ",
    ),
    (
        "src/gacalc/functions.py",
        ">>> foo: InvertibleFunction = ",
        ">>> foo: InvertibleFunction[float] = ",
    ),
    (
        "src/gacalc/functions.py",
        ">>> foo: InvertibleFunction = ",
        ">>> foo: InvertibleFunction[float] = ",
    ),
    (
        "src/gacalc/functions.py",
        ">>> foo: InvertibleFunction = ",
        ">>> foo: InvertibleFunction[float] = ",
    ),
    (
        "src/gacalc/functions.py",
        ">>> add1: InvertibleFunction = ",
        ">>> add1: InvertibleFunction[float] = ",
    ),
    (
        "src/gacalc/functions.py",
        ">>> add2: InvertibleFunction = ",
        ">>> add2: InvertibleFunction[float] = ",
    ),
    (
        "src/gacalc/functions.py",
        ">>> scale3: InvertibleFunction = ",
        ">>> scale3: InvertibleFunction[float] = ",
    ),
    (
        "src/gacalc/functions.py",
        ">>> fn: InvertibleFunction = ",
        ">>> fn: InvertibleFunction[float] = ",
    ),
    (
        "src/gacalc/functions.py",
        ">>> T: InvertibleFunction = ",
        ">>> T: InvertibleFunction[Vector] = ",
    ),
    (
        "src/gacalc/functions.py",
        ">>> move: InvertibleFunction = ",
        ">>> move: InvertibleFunction[Vector] = ",
    ),
    (
        "src/gacalc/functions.py",
        ">>> f: InvertibleFunction = ",
        ">>> f: InvertibleFunction[Vector] = ",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> add2: InvertibleFunction = ",
        ">>> add2: InvertibleFunction[float] = ",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> add2: InvertibleFunction = ",
        ">>> add2: InvertibleFunction[float] = ",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> scale5: InvertibleFunction = ",
        ">>> scale5: InvertibleFunction[float] = ",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> scale5: InvertibleFunction = ",
        ">>> scale5: InvertibleFunction[float] = ",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> fns: list[InvertibleFunction] = compose_intermediate_fns([add2, scale5])",
        ">>> fns: list[InvertibleFunction[float]] = list(\n"
        "        ...     compose_intermediate_fns([add2, scale5])\n"
        "        ... )",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> P: InvertibleFunction = ",
        ">>> P: InvertibleFunction[MultiVectorBase] = ",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> P: InvertibleFunction = ",
        ">>> P: InvertibleFunction[MultiVectorBase] = ",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> R: InvertibleFunction = line_",
        ">>> R: InvertibleFunction[MultiVectorBase] = line_",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> R: InvertibleFunction = line_",
        ">>> R: InvertibleFunction[MultiVectorBase] = line_",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> R: InvertibleFunction = versor_rotation(",
        ">>> R: InvertibleFunction[Vector] = versor_rotation(",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> quarter_turn: InvertibleFunction = bivector_rotation(",
        ">>> quarter_turn: InvertibleFunction[MultiVectorBase] = bivector_rotation(",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> f: InvertibleFunction = turn(",
        ">>> f: InvertibleFunction[MultiVectorBase] = turn(",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> f: InvertibleFunction = turn(",
        ">>> f: InvertibleFunction[Vector] = turn(",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> quarter_turn: InvertibleFunction = plane_rotation(",
        ">>> quarter_turn: InvertibleFunction[typing.Any] = plane_rotation(",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> perspective: ComposableFunction = ",
        ">>> perspective: ComposableFunction[Vector] = ",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> T: InvertibleFunction = translate(",
        ">>> T: InvertibleFunction[Vector] = translate(",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> M: numpy.ndarray = ",
        ">>> M: numpy.ndarray | sympy.Matrix = ",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> S: numpy.ndarray = ",
        ">>> S: numpy.ndarray | sympy.Matrix = ",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> m = MODEL.fill(100.0, 50.0, 32.0, 16.0)",
        ">>> filled: np.ndarray = MODEL.fill(100.0, 50.0, 32.0, 16.0)",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> [float(x) for x in m[:, 3]]",
        ">>> [float(x) for x in filled[:, 3]]",
    ),
    (
        "src/gacalc/transforms.py",
        ">>> [float(m[i, i]) for i in range(4)]",
        ">>> [float(filled[i, i]) for i in range(4)]",
    ),
    (
        "src/gacalc/frame.py",
        ">>> reciprocal: list[Gn] = ",
        ">>> reciprocal: list[MultiVectorBase] = ",
    ),
    (
        "src/gacalc/frame.py",
        ">>> identity_map: InvertibleFunction = ",
        ">>> identity_map: InvertibleFunction[MultiVectorBase] = ",
    ),
    (
        "src/gacalc/frame.py",
        ">>> stretch: InvertibleFunction = ",
        ">>> stretch: InvertibleFunction[MultiVectorBase] = ",
    ),
    (
        "src/gacalc/frame.py",
        ">>> f: InvertibleFunction = ",
        ">>> f: InvertibleFunction[MultiVectorBase] = ",
    ),
    (
        "src/gacalc/frame.py",
        ">>> g: InvertibleFunction = ",
        ">>> g: InvertibleFunction[MultiVectorBase] = ",
    ),
    (
        "src/gacalc/standardposition.py",
        ">>> R: InvertibleFunction = ",
        ">>> R: InvertibleFunction[g2.Vector] = ",
    ),
    (
        "src/gacalc/standardposition.py",
        ">>> quarter_turn: InvertibleFunction = ",
        ">>> quarter_turn: InvertibleFunction[g2.Vector] = ",
    ),
    (
        "src/gacalc/cayley/cayleygraph.py",
        ">>> graph: CayleyGraph = ",
        ">>> graph: CayleyGraph[Space] = ",
    ),
    (
        "src/gacalc/cayley/cayleyscene.py",
        ">>> import numpy\n    >>> m: numpy.ndarray = ",
        ">>> m: np.ndarray = ",
    ),
    (
        "src/gacalc/frame.py",
        ">>> g: InvertibleFunction[MultiVectorBase] = Frame((2 * e_1, 1 * e_1 + 3 * e_2)).to_invertible_function(\n"
        "            ...     inverse_method=InverseMethod.PEEL\n"
        "            ... )",
        ">>> g: InvertibleFunction[MultiVectorBase] = Frame(\n"
        "            ...     (2 * e_1, 1 * e_1 + 3 * e_2)\n"
        "            ... ).to_invertible_function(inverse_method=InverseMethod.PEEL)",
    ),
    (
        "src/gacalc/base.py",
        ">>> w: Gn = MultiVector.reflect(across=u)(v)",
        ">>> w: MultiVectorBase = MultiVector.reflect(across=u)(v)",
    ),
)


@dataclass(frozen=True)
class Edit:
    """One source change in a file.

    Attributes:
        line: 1-based file line of the ``>>>`` line the change belongs to.
        names: The bare names bound there, in order.
        types: The annotation text for each name.
        unpack: True when the line is a tuple unpack, so each name is declared above it.
        imports: ``>>> import`` lines to add above, for names the example's namespace lacks.
    """

    line: int
    names: tuple[str, ...]
    types: tuple[str, ...]
    unpack: bool
    imports: tuple[str, ...]


def bound_names(target: ast.expr) -> list[str]:
    """The bare names an assignment target binds, unpacking included.

    Args:
        target: An assignment target.

    Returns:
        list[str]: its names.
    """
    match target:
        case ast.Name(id=name):
            return [name]
        case ast.Tuple(elts=elts) | ast.List(elts=elts):
            return [n for e in elts for n in bound_names(e)]
        case ast.Starred(value=value):
            return bound_names(value)
        case _:
            return []


def type_text(value: Any, namespace: dict[str, Any]) -> tuple[str, list[str]] | None:
    """The annotation text for a value, with any import lines it needs, or None.

    Args:
        value: The value an example bound.
        namespace: The example's globals, to see which names it already has.

    Returns:
        tuple[str, list[str]] | None: the text and the ``import`` lines to add, or None
            when the value needs a human.
    """
    kind: type = type(value)
    if kind in (bool, int, float, str, complex):
        return kind.__name__, []
    if kind.__module__.startswith("sympy"):
        sympy: Any = sys.modules["sympy"]
        if kind is sympy.Symbol:
            return "sympy.Symbol", []
        return (
            "sympy.Rational" if isinstance(value, sympy.Rational) else "sympy.Expr"
        ), []
    if kind.__module__ == "numpy" and kind.__name__ == "ndarray":
        return "numpy.ndarray", (
            [] if namespace.get("numpy") is sys.modules["numpy"] else ["import numpy"]
        )
    if isinstance(value, list | tuple) and value:
        parts: list[tuple[str, list[str]] | None] = [
            type_text(i, namespace) for i in value
        ]
        if None in parts:
            return None
        texts: set[str] = {p[0] for p in parts if p is not None}
        if len(texts) != 1:
            return None
        inner: str = next(iter(texts))
        imports: list[str] = [i for p in parts if p is not None for i in p[1]]
        outer: str = (
            f"list[{inner}]" if isinstance(value, list) else f"tuple[{inner}, ...]"
        )
        return outer, sorted(set(imports))
    if kind.__module__.startswith("gacalc"):
        if namespace.get(kind.__name__) is kind:
            return kind.__name__, []
        module: types.ModuleType = sys.modules[kind.__module__]
        alias: str
        for alias, obj in namespace.items():
            if obj is module:
                return f"{alias}.{kind.__name__}", []
        return kind.__name__, [f"from {kind.__module__} import {kind.__name__}"]
    return None


def docstring_nodes(tree: ast.Module) -> list[ast.Expr]:
    """The docstring expression of the module and of every class and function in it.

    Args:
        tree: A parsed module.

    Returns:
        list[ast.Expr]: each docstring's expression node, in source order.
    """
    found: list[ast.Expr] = []
    node: ast.AST
    for node in ast.walk(tree):
        if not isinstance(
            node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
        ):
            continue
        head: ast.stmt | None = node.body[0] if node.body else None
        if (
            isinstance(head, ast.Expr)
            and isinstance(head.value, ast.Constant)
            and isinstance(head.value.value, str)
        ):
            found.append(head)
    return sorted(found, key=lambda e: e.lineno)


def edits_for(module: types.ModuleType, source: str) -> tuple[list[Edit], list[str]]:
    """Run every docstring of ``module`` and collect the edits its bare bindings need.

    Args:
        module: The imported module.
        source: Its source text.

    Returns:
        tuple[list[Edit], list[str]]: the edits, and the unresolved bindings as report lines.
    """
    parser: doctest.DocTestParser = doctest.DocTestParser()
    edits: list[Edit] = []
    unresolved: list[str] = []
    relative: str = pathlib.Path(module.__file__ or "").relative_to(REPO).as_posix()
    head: ast.Expr
    for head in docstring_nodes(ast.parse(source)):
        text: str = str(getattr(head.value, "value", ""))
        namespace: dict[str, Any] = dict(module.__dict__)
        declared: set[str] = set()
        imported: set[str] = set()
        example: doctest.Example
        for example in parser.get_examples(text):
            try:
                statements: list[ast.stmt] = ast.parse(example.source).body
            except SyntaxError:
                continue
            line: int = head.lineno + example.lineno
            try:
                exec(compile(example.source, relative, "exec"), namespace)  # noqa: S102
            except Exception as error:
                if example.exc_msg is not None:
                    continue  # the example expects this exception
                unresolved.append(f"{relative}:{line}: example did not run: {error!r}")
                break
            statement: ast.stmt
            for statement in statements:
                if isinstance(statement, ast.AnnAssign) and isinstance(
                    statement.target, ast.Name
                ):
                    declared.add(statement.target.id)
                    continue
                if not isinstance(statement, ast.Assign):
                    continue
                names: list[str] = [
                    n
                    for t in statement.targets
                    for n in bound_names(t)
                    if n not in declared and not n.startswith("_")
                ]
                if not names:
                    continue
                if len(statements) > 1:
                    unresolved.append(f"{relative}:{line}: several statements: {names}")
                    continue
                results: list[tuple[str, list[str]] | None] = [
                    type_text(namespace[n], namespace) for n in names
                ]
                if None in results:
                    kinds: list[str] = [type(namespace[n]).__name__ for n in names]
                    unresolved.append(
                        f"{relative}:{line}: UNRESOLVED {names} ({kinds})"
                    )
                    declared.update(names)
                    continue
                unpack: bool = not (
                    len(statement.targets) == 1
                    and isinstance(statement.targets[0], ast.Name)
                )
                needed: list[str] = sorted(
                    {i for r in results if r is not None for i in r[1]} - imported
                )
                imported.update(needed)
                edits.append(
                    Edit(
                        line,
                        tuple(names),
                        tuple(r[0] for r in results if r is not None),
                        unpack,
                        tuple(needed),
                    )
                )
                declared.update(names)
    return edits, unresolved


def apply_edits(path: pathlib.Path, edits: list[Edit]) -> None:
    """Rewrite ``path`` with the edits, bottom-up so earlier line numbers stay valid.

    Args:
        path: The source file.
        edits: Its edits.
    """
    lines: list[str] = path.read_text().split("\n")
    edit: Edit
    for edit in sorted(edits, key=lambda e: -e.line):
        index: int = edit.line - 1
        current: str = lines[index]
        prefix: str = current[: current.index(">>> ") + 4]
        import_lines: list[str] = [f"{prefix}{i}" for i in edit.imports]
        if edit.unpack:
            declarations: list[str] = [
                f"{prefix}{n}: {t}" for n, t in zip(edit.names, edit.types, strict=True)
            ]
            lines[index:index] = import_lines + declarations
        else:
            name: str = edit.names[0]
            old: str = f"{prefix}{name} = "
            if not current.startswith(old):
                print(
                    f"  not rewritten (shape): {path.name}:{edit.line}: {current.strip()}"
                )
                continue
            lines[index : index + 1] = [
                *import_lines,
                f"{prefix}{name}: {edit.types[0]} = {current[len(old) :]}",
            ]
    path.write_text("\n".join(lines))


# The examples the generator emits into g1.py / g2.py / g3.py (tools/gen_specialized.py). A
# generated module's namespace has Vector, InvertibleFunction, ComposableFunction and sympy,
# so no import line is needed. Each rule: the text after ``>>> `` that starts a bare binding,
# and the annotation text for each name it binds (several names: an unpack, declared above).
GENERATOR_RULES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ('x, k = sympy.symbols("x k")', (("x", "sympy.Symbol"), ("k", "sympy.Symbol"))),
    (
        'a_1, a_2, b_1, b_2, k = sympy.symbols("a_1 a_2 b_1 b_2 k")',
        tuple((n, "sympy.Symbol") for n in ("a_1", "a_2", "b_1", "b_2", "k")),
    ),
    ('x = sympy.Symbol("x")', (("x", "sympy.Symbol"),)),
    ("v = 3 * Vector.e_1 + 4 * Vector.e_2", (("v", "Vector"),)),
    ("v = 3 * e_1 + 4 * e_2", (("v", "Vector"),)),
    ("x, y = sympy.symbols('x y')", (("x", "sympy.Symbol"), ("y", "sympy.Symbol"))),
    (
        "x, y, theta = sympy.symbols('x y theta')",
        tuple((n, "sympy.Symbol") for n in ("x", "y", "theta")),
    ),
    ("p = Vector.project(onto=Vector.e_1)", (("p", "ComposableFunction[Vector]"),)),
    ("f = Vector.reflect(across=Vector.e_1)", (("f", "InvertibleFunction[Vector]"),)),
    ("turn = rotate_90_degrees()", (("turn", "InvertibleFunction[Vector]"),)),
    ("P = (", (("P", "InvertibleFunction[Vector]"),)),
    ("R = (", (("R", "InvertibleFunction[Vector]"),)),
)


def annotate_generator() -> int:
    """Type the bare bindings of the examples ``tools/gen_specialized.py`` emits.

    Returns:
        int: how many source lines were rewritten.
    """
    path: pathlib.Path = REPO / "tools" / "gen_specialized.py"
    lines: list[str] = path.read_text().split("\n")
    out: list[str] = []
    changed: int = 0
    line: str
    for line in lines:
        rewritten: list[str] = [line]
        start: int = line.find(">>> ")
        if start >= 0:
            body: str = line[start + 4 :]
            rule_text: str
            names: tuple[tuple[str, str], ...]
            for rule_text, names in GENERATOR_RULES:
                if not body.startswith(rule_text.split(" = ")[0] + " = "):
                    continue
                if rule_text.endswith("(") and not body.startswith(rule_text):
                    # P / R: only the line_to_*_projection/rejection examples
                    if "line_" not in body:
                        continue
                if len(names) > 1:
                    head: str = line[: line.index(">>> ")]
                    quote: str = head.rstrip()[-1]
                    rewritten = [f"{head}>>> {n}: {t}\\n{quote}" for n, t in names] + [
                        line
                    ]
                elif f">>> {names[0][0]} = " in line:
                    rewritten = [
                        line.replace(
                            f">>> {names[0][0]} = ",
                            f">>> {names[0][0]}: {names[0][1]} = ",
                            1,
                        )
                    ]
                if rewritten != [line]:
                    changed += 1
                    break
        out.extend(rewritten)
    if changed:
        path.write_text("\n".join(out))
    return changed


WRAP_WIDTH: int = 88
WRAP_FILES: tuple[str, ...] = (
    "src/gacalc/base.py",
    "src/gacalc/frame.py",
    "src/gacalc/functions.py",
    "src/gacalc/transforms.py",
    "src/gacalc/nbdisplay.py",
    "src/gacalc/standardposition.py",
    "src/gacalc/gl/grapher3d.py",
)


def wrap_long_examples() -> int:
    """Wrap each annotated ``>>> name: T = value`` line that passes the line limit.

    A typed binding is longer than the bare one, and ``ruff`` holds docstring lines to 88
    columns. The value goes in parentheses on a ``...`` continuation, a trailing comment after
    the closing parenthesis; a line that already has continuation lines is left alone.

    Returns:
        int: how many lines were wrapped.
    """
    wrapped: int = 0
    file: str
    for file in WRAP_FILES:
        path: pathlib.Path = REPO / file
        lines: list[str] = path.read_text().split("\n")
        out: list[str] = []
        index: int
        for index, line in enumerate(lines):
            following: str = lines[index + 1].lstrip() if index + 1 < len(lines) else ""
            stripped: str = line.lstrip()
            if (
                len(line) > WRAP_WIDTH
                and stripped.startswith(">>> ")
                and ": " in stripped.split(" = ")[0]
                and " = " in stripped
                and not following.startswith("...")
            ):
                indent: str = line[: len(line) - len(stripped)]
                head, value = stripped[4:].split(" = ", 1)
                code, _, comment = value.partition("  #")
                tail: str = f"  #{comment}" if comment else ""
                out.extend(
                    [
                        f"{indent}>>> {head} = (",
                        f"{indent}...     {code.rstrip()}",
                        f"{indent}... ){tail}",
                    ]
                )
                wrapped += 1
            else:
                out.append(line)
        path.write_text("\n".join(out))
    return wrapped


def main() -> None:
    """Annotate every listed module and print what needs a human."""
    report: list[str] = []
    total: int = 0
    name: str
    for name in MODULES:
        module: types.ModuleType = importlib.import_module(name)
        path: pathlib.Path = pathlib.Path(module.__file__ or "")
        edits, unresolved = edits_for(module, path.read_text())
        report.extend(unresolved)
        if edits:
            apply_edits(path, edits)
            total += len(edits)
            print(f"{path.relative_to(REPO)}: {len(edits)} bindings typed")
    print(f"{total} edits")
    print(f"generator: {annotate_generator()} lines")
    file: str
    old: str
    new: str
    for file, old, new in MANUAL:
        target: pathlib.Path = REPO / file
        text: str = target.read_text()
        if old in text:
            target.write_text(text.replace(old, new, 1))
            print(f"by hand: {file}: {old.strip()[:50]}")
    old_text: str
    new_text: str
    for file, old_text, new_text in REFINE:
        target = REPO / file
        text = target.read_text()
        if old_text in text:
            target.write_text(text.replace(old_text, new_text, 1))
    print(f"wrapped: {wrap_long_examples()} lines")
    line: str
    for line in report:
        print(line)


if __name__ == "__main__":
    main()
