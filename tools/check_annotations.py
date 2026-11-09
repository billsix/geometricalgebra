#!/usr/bin/env python3
"""Report every place a type annotation is missing or loose.

**When to run it:** after adding or reshaping hand-written Python, to check that
the repo-wide annotation coverage has not regressed.  The known-good floor -- every
row a deliberate exemption -- and the current count live in
``tasks/reference/type-annotation-exemptions.md``.  A row that is not in that list
is a genuine gap -- annotate it, or add it to the list with its reason.

Informational, not a gate: judging whether a row is an exemption needs a human,
so this reports and never fails the build, and no ``make`` target runs it.

Walks the hand-written Python in ``src/``, ``tools/``, ``tests/``, ``notebooks/`` and
the book's companion notebooks ``book/docs/notebooks/`` with the ``ast`` module and
reports, per file:

* ``RET``    -- a ``def`` with no return annotation.
* ``PARAM``  -- a parameter with no annotation (``self``/``cls`` excluded).
* ``LOCAL``  -- an assignment with no annotation, where a concrete type is
  plausibly knowable: to a bare name, or each name of an unpacking
  (``a_1, a_2 = sympy.symbols(...)``, whose names the convention declares on the
  lines above).  Noise-prone by nature, so the report is a *candidate* list to
  read, not a to-do list to apply blindly.
* ``LOOP``   -- an unannotated ``for``-loop target, unpacked names included (it
  cannot be annotated inline; the convention is a declaration on the line
  above).  Comprehension and generator targets are deliberately skipped: they are
  a separate scope and stay inferred.

A name counts as annotated only within its own scope (the module, a class body,
or one ``def``): an annotated ``x`` in one function says nothing about an ``x``
in another.  A parameter's annotation covers rebinds of it in its body.
* ``BARE``   -- a bare generic annotation (``ComposableFunction`` rather than
  ``ComposableFunction[...]``), which silently degrades the parameter to ``Any``.
* ``ANY``    -- an explicit ``typing.Any``/``Any`` in an annotation.
* ``INVAR``  -- an invariant ``dict``/``list``/``set`` *parameter* annotation,
  where a read-only use wants the covariant ``Mapping``/``Sequence``/``AbstractSet``.

The generated ``src/gacalc/g*.py`` are build artifacts owned by the generator and
are excluded; so is anything ``.gitignore``d (asked of ``git ls-files``; outside a
git checkout nothing is filtered).

Run from anywhere::

    python tools/check_annotations.py             # summary counts by kind and file
    python tools/check_annotations.py --full      # every row
    python tools/check_annotations.py --kind RET  # one kind
    python tools/check_annotations.py --path src  # one part of the tree
"""

from __future__ import annotations

import argparse
import ast
import pathlib
import re
import subprocess
import sys
from collections.abc import Iterator

# tools/ -> repo root
REPO: pathlib.Path = pathlib.Path(__file__).resolve().parents[1]

SCOPE_DIRS: tuple[str, ...] = (
    "src",
    "tools",
    "tests",
    "notebooks",
    "book/docs/notebooks",
)

# Build artifacts: the generator owns their annotations (fix tools/, never these).
GENERATED: re.Pattern[str] = re.compile(r"^src/gacalc/g\d+\.py$")

# Generic classes whose bare use degrades a parameter to implicit Any.  Bare
# ``MultiVectorFn`` and the isinstance-check sites are documented exceptions in
# CLAUDE.md, so they are reported and then judged, not auto-flagged as wrong.
GENERIC_NAMES: frozenset[str] = frozenset(
    {"ComposableFunction", "InvertibleFunction", "Linearity", "Generator", "Iterator"}
)

INVARIANT_CONTAINERS: frozenset[str] = frozenset({"dict", "list", "set"})


class Finding:
    """One catalog row: where, what kind, and the name it concerns."""

    def __init__(
        self, path: str, line: int, kind: str, name: str, detail: str = ""
    ) -> None:
        self.path: str = path
        self.line: int = line
        self.kind: str = kind
        self.name: str = name
        self.detail: str = detail

    def __str__(self) -> str:
        tail: str = f"  ({self.detail})" if self.detail else ""
        return f"{self.path}:{self.line}: {self.kind:<5} {self.name}{tail}"


def not_ignored() -> set[str] | None:
    """Repo-relative paths git does not ignore (tracked or untracked), or None.

    None means git is unavailable here (no ``git``, or not a checkout), and then
    nothing is filtered.
    """
    try:
        listing: subprocess.CompletedProcess[str] = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
        )
    except OSError, subprocess.CalledProcessError:
        return None
    return set(listing.stdout.splitlines())


def in_scope() -> Iterator[pathlib.Path]:
    """Every hand-written .py file under the in-scope directories, minus gitignored."""
    visible: set[str] | None = not_ignored()
    d: str
    for d in SCOPE_DIRS:
        root: pathlib.Path = REPO / d
        if not root.is_dir():
            continue
        p: pathlib.Path
        for p in sorted(root.rglob("*.py")):
            rel: str = p.relative_to(REPO).as_posix()
            if GENERATED.match(rel) or (visible is not None and rel not in visible):
                continue
            yield p


def annotation_names(node: ast.expr | None) -> set[str]:
    """Every bare ``Name`` appearing in an annotation expression."""
    if node is None:
        return set()
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def is_bare_generic(node: ast.expr | None) -> str | None:
    """The generic's name when the annotation is an unsubscripted generic."""
    if isinstance(node, ast.Name) and node.id in GENERIC_NAMES:
        return node.id
    return None


def check_function(
    fn: ast.FunctionDef | ast.AsyncFunctionDef,
    rel: str,
    out: list[Finding],  # an OUT-parameter (appended to), so not widened to Sequence
    is_method: bool = False,
) -> None:
    """Return + parameter annotations for one ``def``.

    ``is_method`` says the ``def`` is lexically inside a ``class`` body, which is
    what makes an unannotated leading ``self`` conventional rather than a finding.
    """
    if fn.returns is None:
        out.append(Finding(rel, fn.lineno, "RET", fn.name))

    args: ast.arguments = fn.args
    positional: list[ast.arg] = (
        list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
    )
    # `cls` is only the conventional unannotated receiver on a @classmethod; as a
    # plain parameter name it is ordinary (pytest's `parametrize("cls", ...)` uses
    # it heavily), so keying off the decorator rather than the name avoids
    # silently under-reporting those.
    decorators: set[str] = {
        d.id for d in fn.decorator_list if isinstance(d, ast.Name)
    } | {d.attr for d in fn.decorator_list if isinstance(d, ast.Attribute)}
    receiver: str | None = (
        "cls" if "classmethod" in decorators else ("self" if is_method else None)
    )
    i: int
    a: ast.arg
    for i, a in enumerate(positional):
        # The receiver is conventionally unannotated -- only as the FIRST
        # positional parameter, so a stray later `self` still gets reported.
        if i == 0 and receiver is not None and a.arg == receiver and a in args.args:
            continue
        if a.annotation is None:
            out.append(Finding(rel, a.lineno, "PARAM", f"{fn.name}({a.arg})"))
            continue
        bare: str | None = is_bare_generic(a.annotation)
        if bare is not None:
            out.append(
                Finding(rel, a.lineno, "BARE", f"{fn.name}({a.arg})", f"bare {bare}")
            )
        if isinstance(a.annotation, ast.Subscript) and isinstance(
            a.annotation.value, ast.Name
        ):
            if a.annotation.value.id in INVARIANT_CONTAINERS:
                out.append(
                    Finding(
                        rel,
                        a.lineno,
                        "INVAR",
                        f"{fn.name}({a.arg})",
                        f"invariant {a.annotation.value.id}",
                    )
                )
        if "Any" in annotation_names(a.annotation):
            out.append(Finding(rel, a.lineno, "ANY", f"{fn.name}({a.arg})"))

    vararg: ast.arg | None
    for vararg in (args.vararg, args.kwarg):
        if vararg is not None and vararg.annotation is None:
            out.append(
                Finding(rel, vararg.lineno, "PARAM", f"{fn.name}(*/**{vararg.arg})")
            )

    if fn.returns is not None and "Any" in annotation_names(fn.returns):
        out.append(Finding(rel, fn.lineno, "ANY", f"{fn.name}() -> Any"))


def is_type_definition(value: ast.expr) -> bool:
    """Whether a module-level assignment's right-hand side *defines a type*.

    Type aliases (``Real = int | float | sympy.Expr``, ``Blade = tuple[int, ...]``,
    ``MultiVector = Gn``) and type-system constructors (``TypeVar``, ``NewType``,
    ``ParamSpec``) look like ordinary assignments to ``ast`` but are not
    annotation candidates -- annotating one changes what it means.  Recognized by
    shape: a union, a subscripted generic, a bare capitalized name, or a call to a
    typing constructor.
    """
    if isinstance(value, ast.Call):
        fn: ast.expr = value.func
        target: str = (
            fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
        )
        return target in {"TypeVar", "NewType", "ParamSpec", "TypeAliasType"}
    if isinstance(value, ast.BinOp) and isinstance(value.op, ast.BitOr):
        return True
    if isinstance(value, ast.Subscript):
        return True
    if isinstance(value, ast.Name):
        return value.id[:1].isupper()
    return False


def check_file(path: pathlib.Path) -> list[Finding]:
    """Every finding in one file."""
    rel: str = path.relative_to(REPO).as_posix()
    try:
        tree: ast.Module = ast.parse(path.read_text(), filename=str(path))
    except SyntaxError as exc:  # a notebook percent-script mid-edit, say
        return [Finding(rel, exc.lineno or 0, "PARSE", str(exc))]

    out: list[Finding] = []

    # Assignments in an Enum class body are members, not annotation candidates:
    # ``LINEAR = 0`` declares an enum value, and annotating it would make it a
    # plain class attribute instead.
    enum_members: set[int] = {
        id(stmt)
        for cls in ast.walk(tree)
        if isinstance(cls, ast.ClassDef)
        and any(
            (isinstance(b, ast.Name) and "Enum" in b.id)
            or (isinstance(b, ast.Attribute) and "Enum" in b.attr)
            for b in cls.bases
        )
        for stmt in cls.body
        if isinstance(stmt, ast.Assign)
    }
    module_level: set[str] = {
        t.id
        for stmt in tree.body
        if isinstance(stmt, ast.Assign)
        for t in stmt.targets
        if isinstance(t, ast.Name)
    }

    # Which defs are lexically methods -- collected up front, since ast.walk
    # flattens the tree and loses the enclosing class.
    methods: set[int] = {
        id(child)
        for cls in ast.walk(tree)
        if isinstance(cls, ast.ClassDef)
        for child in cls.body
        if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef)
    }

    fn: ast.AST
    for fn in ast.walk(tree):
        if isinstance(fn, ast.FunctionDef | ast.AsyncFunctionDef):
            check_function(fn, rel, out, is_method=id(fn) in methods)

    # Bindings are judged per scope -- the module, each class body, each def --
    # because a name annotated in one function says nothing about the same name
    # in another.
    scope: ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
    for scope in [tree] + [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
    ]:
        nodes: list[ast.AST] = list(scope_nodes(scope))
        # Names bound by an annotated assignment in this scope; an unannotated
        # rebind of such a name is already typed and is not a finding.  Names
        # declared global/nonlocal belong to an outer scope, so they are skipped.
        annotated: set[str] = {
            n.target.id
            for n in nodes
            if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)
        } | {
            name
            for n in nodes
            if isinstance(n, ast.Global | ast.Nonlocal)
            for name in n.names
        }
        # A parameter carries its type in the signature, so a later rebind of
        # that name inside the body is already typed -- annotating it again
        # would be redundant, and where the rebind narrows a union it would fight
        # the checker's flow analysis (``base.__add__`` rebinding its ``rhs``).
        if isinstance(scope, ast.FunctionDef | ast.AsyncFunctionDef):
            annotated |= {
                a.arg
                for a in (
                    list(scope.args.posonlyargs)
                    + list(scope.args.args)
                    + list(scope.args.kwonlyargs)
                )
                if a.annotation is not None
            }

        node: ast.AST
        for node in nodes:
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    name: str = node.targets[0].id
                    if name in annotated or name.startswith("_"):
                        continue
                    kind: str = (
                        "ALIAS"
                        if (
                            scope is tree
                            and name in module_level
                            and is_type_definition(node.value)
                        )
                        else ("ENUM" if id(node) in enum_members else "LOCAL")
                    )
                    out.append(Finding(rel, node.lineno, kind, name))
                    continue
                # Unpacking (``a, b = ...``) and chained (``a = b = ...``)
                # assignments: each bare name in them needs a declaration above.
                unpacked: list[str] = [
                    t
                    for target in node.targets
                    for t in bound_names(target)
                    if t not in annotated and not t.startswith("_")
                ]
                if unpacked:
                    out.append(Finding(rel, node.lineno, "LOCAL", ", ".join(unpacked)))
            elif isinstance(node, ast.For | ast.AsyncFor):
                # `_` is the conventional discard: the value is never read, so a
                # type for it would be noise, not documentation.
                names: list[str] = [
                    t
                    for t in bound_names(node.target)
                    if t not in annotated and t.strip("_") != ""
                ]
                if names:
                    out.append(Finding(rel, node.lineno, "LOOP", ", ".join(names)))
    return out


def scope_nodes(
    scope: ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
) -> Iterator[ast.AST]:
    """Every node in one scope's body, not descending into nested scopes.

    A nested ``def``/``class``/``lambda`` or a comprehension is its own scope (a
    comprehension's targets stay inferred), so its bindings are not this scope's.
    """
    pending: list[ast.AST] = list(reversed(scope.body))
    while pending:
        node: ast.AST = pending.pop()
        yield node
        if isinstance(
            node,
            ast.FunctionDef
            | ast.AsyncFunctionDef
            | ast.ClassDef
            | ast.Lambda
            | ast.ListComp
            | ast.SetComp
            | ast.DictComp
            | ast.GeneratorExp,
        ):
            continue
        pending.extend(reversed(list(ast.iter_child_nodes(node))))


def bound_names(target: ast.expr) -> list[str]:
    """The bare names an assignment or ``for`` target binds, unpacking included.

    Attribute and subscript targets (``self.x = ...``, ``d[k] = ...``) bind no
    new name, so they contribute nothing.
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


def main() -> int:
    ap: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--full", action="store_true", help="print every row, not a summary"
    )
    ap.add_argument("--kind", help="restrict to one kind (RET, PARAM, LOCAL, ...)")
    ap.add_argument("--path", help="restrict to paths containing this substring")
    args: argparse.Namespace = ap.parse_args()

    findings: list[Finding] = []
    p: pathlib.Path
    for p in in_scope():
        findings.extend(check_file(p))

    if args.kind:
        findings = [f for f in findings if f.kind == args.kind.upper()]
    if args.path:
        findings = [f for f in findings if args.path in f.path]

    by_kind: dict[str, int] = {}
    by_file: dict[str, int] = {}
    f: Finding
    for f in findings:
        by_kind[f.kind] = by_kind.get(f.kind, 0) + 1
        by_file[f.path] = by_file.get(f.path, 0) + 1

    if args.full:
        for f in findings:
            print(  # noqa: T201 -- the report is the tool's output
                f
            )  # noqa: T201
        print(  # noqa: T201 -- the report is the tool's output
        )

    print(  # noqa: T201 -- the report is the tool's output
        "by kind:"
    )
    k: str
    n: int
    for k, n in sorted(by_kind.items(), key=lambda kv: -kv[1]):
        print(  # noqa: T201 -- the report is the tool's output
            f"  {k:<6} {n:>5}"
        )
    print(  # noqa: T201 -- the report is the tool's output
        "\nby file (top 25):"
    )
    path: str
    for path, n in sorted(by_file.items(), key=lambda kv: -kv[1])[:25]:
        print(  # noqa: T201 -- the report is the tool's output
            f"  {n:>5}  {path}"
        )
    print(  # noqa: T201 -- the report is the tool's output
        f"\ntotal: {len(findings)} findings in {len(by_file)} files"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
