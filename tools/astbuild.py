#!/usr/bin/env python
# Copyright (c) 2025-2026 William Emerison Six
# SPDX-License-Identifier: LGPL-2.1-only
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License, version
# 2.1, as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License (the LICENSE file in this repository)
# for more details.

"""Generic Python-`ast` construction helpers for the code generator.

A small DSL for building syntax-tree nodes (``nm``/``dot``/``call``/``cast``/``fn``/
``cls``/``annotated_assign``/...) and rendering them with ``ast.unparse``
(``module_source``).
Knows nothing about geometric algebra -- it only knows the conventions of the code
this generator emits (e.g. ``cast_self``/``cast_coef`` wrap ``typing.cast`` to
``typing.Self``/``Coef`` (the coefficient type)).  Used by tools/gen_specialized.py.
"""

from __future__ import annotations

import ast
import re
import typing
from collections.abc import Iterable, Sequence

# A comment cannot exist in a Python AST, so a doc-region marker is emitted as a
# sentinel *string-literal statement* and rewritten to a ``# comment`` in the
# rendered source (see ``marker`` / ``module_source``).  The delimiters are
# chosen to never occur in real generated code.
_MARKER_OPEN: str = "@@doc-region@@"
_MARKER_CLOSE: str = "@@/doc-region@@"
# Matches the sentinel however ``ast.unparse`` quoted it (bare '...' or, in
# docstring position, triple-quoted), capturing the marker text.
_MARKER_RE: typing.Final = re.compile(
    r"^(?P<indent>[ \t]*)"
    r"""(?:'''|\"\"\"|'|\")"""
    + re.escape(_MARKER_OPEN)
    + r"(?P<text>.*?)"
    + re.escape(_MARKER_CLOSE)
    + r"""(?:'''|\"\"\"|'|\")$""",
    re.MULTILINE,
)


def parse_expr(src: str) -> ast.expr:
    """Parse a source snippet into a single expression node."""
    return ast.parse(src, mode="eval").body


def marker(text: str) -> ast.Expr:
    """A ``doc-region`` marker as a sentinel statement (rendered to a comment).

    Emitted as a bare string-literal ``ast.Expr`` so it survives ``ast.unparse``
    at the correct indentation; ``module_source`` rewrites it to
    ``# <text>``.  ``text`` is e.g. ``"doc-region-begin Vector2 class"``.
    """
    return ast.Expr(ast.Constant(_MARKER_OPEN + text + _MARKER_CLOSE))


def _is_classvar(annotation: ast.expr) -> bool:
    """True if a field annotation is ``typing.ClassVar[...]`` (not an instance var)."""
    if not isinstance(annotation, ast.Subscript):
        return False
    head: ast.expr = annotation.value
    name: str | None = (
        head.attr
        if isinstance(head, ast.Attribute)
        else head.id
        if isinstance(head, ast.Name)
        else None
    )
    return name == "ClassVar"


def _is_overload(node: ast.stmt) -> bool:
    """True if ``node`` is a ``@typing.overload`` (or bare ``@overload``) stub.

    Overload stubs share the implementation's method name, so marking them would
    emit duplicate ``<Class> <method> method`` regions; they are left unmarked and
    only the implementation carries the method's doc-region."""
    if not isinstance(node, ast.FunctionDef):
        return False
    decorator: ast.expr
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Attribute) and decorator.attr == "overload":
            return True
        if isinstance(decorator, ast.Name) and decorator.id == "overload":
            return True
    return False


def _method_label(class_name: str, method: ast.FunctionDef, seen: set[str]) -> str:
    """A unique, prefix-free region label for a method.

    ``<class> <method> method`` normally, but a property **setter** / **deleter**
    shares the getter's name, so it takes an ``<method> setter`` / ``deleter``
    qualifier; any remaining duplicate gets a numeric one.  The qualifier goes
    *before* the trailing ``method`` keyword so names stay prefix-free (``x
    setter method`` does not contain ``x method``).  ``seen`` is mutated to track
    the labels already used in this class.
    """
    decorator: ast.expr
    accessor: str = ""
    for decorator in method.decorator_list:
        if isinstance(decorator, ast.Attribute) and decorator.attr in (
            "setter",
            "deleter",
        ):
            accessor = " " + decorator.attr
    core: str = f"{method.name}{accessor}"
    label: str = f"{class_name} {core} method"
    suffix: int = 2
    while label in seen:
        label = f"{class_name} {core} {suffix} method"
        suffix += 1
    seen.add(label)
    return label


def inject_region_markers(body: list[ast.stmt]) -> list[ast.stmt]:
    """Wrap each top-level class -- and, within it, its declaration, its instance
    variables, and each method -- in doc-region markers.

    Regions per class ``C``: ``C class`` (the whole class), ``C declaration`` (the
    ``class`` line, ending before the docstring), ``C instance variables`` (the
    dataclass fields), and ``C <method> method`` for each method.  The trailing
    keyword keeps names **prefix-free** (Sphinx matches the first line *containing*
    the anchor, so ``... magnitude`` would otherwise also match
    ``... magnitude_squared``).

    Most markers are AST siblings placed *around* a node, so a copied docstring
    (which must stay first inside a block, or ``ast.unparse`` renders it as an
    ugly escaped string) is untouched.  The one exception is the ``declaration``
    *end*, which must land after the ``class`` line but before the docstring;
    emitting it here would displace the docstring, so it is inserted at the text
    level in :func:`module_source` instead.
    """
    out: list[ast.stmt] = []
    node: ast.stmt
    for node in body:
        if not isinstance(node, ast.ClassDef):
            out.append(node)
            continue
        field_indices: list[int] = [
            i
            for i, m in enumerate(node.body)
            if isinstance(m, ast.AnnAssign) and not _is_classvar(m.annotation)
        ]
        first_field: int | None = field_indices[0] if field_indices else None
        last_field: int | None = field_indices[-1] if field_indices else None
        new_body: list[ast.stmt] = []
        seen_labels: set[str] = set()
        i: int
        member: ast.stmt
        for i, member in enumerate(node.body):
            if i == first_field:
                new_body.append(
                    marker(f"doc-region-begin {node.name} instance variables")
                )
            if isinstance(member, ast.FunctionDef) and not _is_overload(member):
                label: str = _method_label(node.name, member, seen_labels)
                new_body.append(marker(f"doc-region-begin {label}"))
                new_body.append(member)
                new_body.append(marker(f"doc-region-end {label}"))
            else:
                # non-methods and @overload stubs: emitted without a region
                new_body.append(member)
            if i == last_field:
                new_body.append(
                    marker(f"doc-region-end {node.name} instance variables")
                )
        node.body = new_body
        out.append(marker(f"doc-region-begin {node.name} class"))
        # declaration BEGIN here; its END is inserted after the class line by
        # module_source (see the docstring above for why not here).
        out.append(marker(f"doc-region-begin {node.name} declaration"))
        out.append(node)
        out.append(marker(f"doc-region-end {node.name} class"))
    return out


def _insert_declaration_ends(src: str) -> str:
    """Place each ``doc-region-end <C> declaration`` right after ``C``'s ``class`` line.

    The declaration region's end must fall between the ``class`` line and the
    docstring; doing that in the AST would bump the docstring out of first
    position (rendering it as an escaped one-liner), so it is done here in text.
    Keyed off the ``doc-region-begin <C> declaration`` comment already emitted
    just above each class.
    """
    lines: list[str] = src.split("\n")
    out_lines: list[str] = []
    pending: str | None = None  # class name whose `class` line we're waiting for
    begin_re: typing.Final = re.compile(
        r"^\s*# doc-region-begin (?P<name>\S+) declaration$"
    )
    line: str
    for line in lines:
        out_lines.append(line)
        begin = begin_re.match(line)
        if begin is not None:
            pending = begin.group("name")
            continue
        if pending is not None and re.match(
            rf"^(?P<indent>\s*)class {re.escape(pending)}\b.*:\s*$", line
        ):
            indent: str = line[: len(line) - len(line.lstrip())]
            out_lines.append(f"{indent}    # doc-region-end {pending} declaration")
            pending = None
    return "\n".join(out_lines)


def module_source(body: list[ast.stmt]) -> str:
    """Render top-level statement nodes to source via `ast.unparse`.

    Any ``marker`` sentinels are rewritten to ``# doc-region-...`` comments, and
    each class's ``declaration`` region is closed after its ``class`` line (both
    a no-op when there are no markers).
    """
    module: ast.Module = ast.Module(body=body, type_ignores=[])
    rendered: str = ast.unparse(ast.fix_missing_locations(module))
    commented: str = _MARKER_RE.sub(r"\g<indent># \g<text>", rendered)
    return _insert_declaration_ends(commented)


class SymbolToAttr(ast.NodeTransformer):
    """Rewrite operand-symbol ``Name`` nodes to attribute access.

    ``rename`` maps a sympy symbol name (e.g. ``a_e_1``) to an ``(object, attr)``
    pair (e.g. ``("self", "e_1")``).  Replaces the old word-boundary regex on
    rendered source with a structural, correct-by-construction transform.
    """

    def __init__(self, rename: dict[str, tuple[str, str]]):
        self.rename = rename

    def visit_Name(self, node: ast.Name) -> ast.AST:
        target: tuple[str, str] | None = self.rename.get(node.id)
        if target is None:
            return node
        obj: str
        attr: str
        obj, attr = target
        # An empty ``attr`` means "bind the symbol to the bare name ``obj``" (not
        # ``obj.attr``) -- used for the number-operand fast path, where a bare
        # scalar ``rhs`` stands in for what would be ``rhs.coeff_scalar``.
        if not attr:
            return ast.Name(id=obj, ctx=ast.Load())
        return ast.Attribute(
            value=ast.Name(id=obj, ctx=ast.Load()), attr=attr, ctx=ast.Load()
        )


_LOAD = ast.Load()

_STORE = ast.Store()


def name_ref(ident: str) -> ast.Name:
    return ast.Name(id=ident, ctx=_LOAD)


def attribute(value: ast.expr | str, *parts: str) -> ast.expr:
    node: ast.expr = value if isinstance(value, ast.AST) else name_ref(value)
    for p in parts:
        node = ast.Attribute(value=node, attr=p, ctx=_LOAD)
    return node


def constant(v: object) -> ast.Constant:
    # ast.Constant accepts any literal value, including the blade tuples used as
    # dict keys (e.g. ``lit(())``), which typeshed's narrower value type omits;
    # cast at the boundary.
    return ast.Constant(value=typing.cast(typing.Any, v))


def call(
    func: ast.expr | str,
    args: Iterable[ast.expr] = (),
    **kwargs: ast.expr,
) -> ast.Call:
    f: ast.expr = func if isinstance(func, ast.AST) else name_ref(func)
    return ast.Call(
        func=f,
        args=list(args),
        keywords=[ast.keyword(arg=k, value=v) for k, v in kwargs.items()],
    )


def cast(type_node: ast.expr, value: ast.expr) -> ast.Call:
    return call(attribute("typing", "cast"), [type_node, value])


def cast_self(value: ast.expr) -> ast.Call:
    return cast(attribute("typing", "Self"), value)


def cast_operand(value: ast.expr) -> ast.Call:
    # cast to the sandwich operand TypeVar ``_OperandT`` (imported from base) --
    # a versor conjugation returns the *operand's* own type, not ``Self``.
    return cast(name_ref("_OperandT"), value)


def cast_coef(value: ast.expr) -> ast.expr:
    # A bare field (``self.coeff_x``) or a negated field (``-self.coeff_x``) is
    # already of type ``Coef``, so casting it is redundant (ty warns).  Only wrap
    # genuinely compound expressions (sums, products, ``d.get(...)``, literals).
    if isinstance(value, (ast.Name, ast.Attribute)):
        return value
    if (
        isinstance(value, ast.UnaryOp)
        and isinstance(value.op, ast.USub)
        and isinstance(value.operand, (ast.Name, ast.Attribute))
    ):
        return value
    return cast(name_ref("Coef"), value)


def return_stmt(value: ast.expr | None) -> ast.Return:
    return ast.Return(value=value)


def subscript(value: ast.expr, index: ast.expr) -> ast.Subscript:
    return ast.Subscript(value=value, slice=index, ctx=_LOAD)


def opt_int() -> ast.expr:
    """The annotation ``int | None``."""
    return ast.BinOp(left=name_ref("int"), op=ast.BitOr(), right=constant(None))


def argument(name_: str, annotation: ast.expr | None = None) -> ast.arg:
    return ast.arg(arg=name_, annotation=annotation)


def function_def(
    name_: str,
    body: Sequence[ast.stmt],
    params: list[ast.arg] | None = None,
    defaults: Sequence[ast.expr] = (),
    decorators: Sequence[ast.expr] = (),
    returns: ast.expr | None = None,
) -> ast.FunctionDef:
    """An ``ast.FunctionDef``; ``params`` are ``ast.arg`` (default ``[self]``)."""
    params = [argument("self")] if params is None else params
    arguments: ast.arguments = ast.arguments(
        posonlyargs=[],
        args=params,
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=list(defaults),
    )
    return ast.FunctionDef(
        name=name_,
        args=arguments,
        body=list(body),
        decorator_list=list(decorators),
        returns=returns,
        type_params=[],
    )


def class_def(
    name_: str,
    body: Sequence[ast.stmt],
    bases: Sequence[str] = ("MultiVectorBase",),
    decorators: Sequence[ast.expr] = (),
) -> ast.ClassDef:
    return ast.ClassDef(
        name=name_,
        bases=[name_ref(b) for b in bases],
        keywords=[],
        body=list(body),
        decorator_list=list(decorators),
        type_params=[],
    )


def dataclass_decorator(**flags: bool) -> ast.Call:
    return ast.Call(
        func=attribute("dataclasses", "dataclass"),
        args=[],
        keywords=[ast.keyword(arg=k, value=constant(v)) for k, v in flags.items()],
    )


def annotated_assign(
    target_name: str, annotation: ast.expr, value: ast.expr | None = None
) -> ast.AnnAssign:
    return ast.AnnAssign(
        target=ast.Name(id=target_name, ctx=_STORE),
        annotation=annotation,
        value=value,
        simple=1,
    )


def assign(target_name: str, value: ast.expr) -> ast.Assign:
    return ast.Assign(targets=[ast.Name(id=target_name, ctx=_STORE)], value=value)


def isinstance_(value: ast.expr, types: list[ast.expr] | ast.expr) -> ast.Call:
    type_node: ast.expr = (
        ast.Tuple(elts=list(types), ctx=_LOAD) if isinstance(types, list) else types
    )
    return call("isinstance", [value, type_node])


def not_(node: ast.expr) -> ast.UnaryOp:
    return ast.UnaryOp(op=ast.Not(), operand=node)


def ne_zero(node: ast.expr) -> ast.Compare:
    return ast.Compare(left=node, ops=[ast.NotEq()], comparators=[constant(0)])


def construct(name_: str, pairs: Iterable[tuple[str, ast.expr]]) -> ast.Call:
    """``Name(field=value, ...)`` with keywords in the given order."""
    return ast.Call(
        func=name_ref(name_),
        args=[],
        keywords=[ast.keyword(arg=f, value=v) for f, v in pairs],
    )


def construct_type_of(var: str, pairs: Iterable[tuple[str, ast.expr]]) -> ast.Call:
    """``type(<var>)(field=value, ...)`` -- subclass-preserving construction."""
    return ast.Call(
        func=call("type", [name_ref(var)]),
        args=[],
        keywords=[ast.keyword(arg=f, value=v) for f, v in pairs],
    )


def construct_type_self(pairs: Iterable[tuple[str, ast.expr]]) -> ast.Call:
    """``type(self)(field=value, ...)`` -- subclass-preserving construction."""
    return construct_type_of("self", pairs)


def return_construct(
    name_: str,
    pairs: Iterable[tuple[str, ast.expr]],
    owner: str | None = None,
    final: bool = False,
) -> ast.stmt:
    """``return cast(Self, Name(field=value, ...))`` (the no-local return idiom).

    When ``owner`` names the class being generated and the result type equals
    it (a same-type op), emit the class directly: ``return Name(...)`` when the
    class is ``final`` (not subclassable — the concrete class is exact), else
    ``return type(self)(...)`` so a subclass gets its own type back (no cast
    needed either way: for a same-type result the value already is that type)."""
    if owner is not None and owner == name_:
        if final:
            return return_stmt(construct(name_, pairs))
        return return_stmt(construct_type_self(pairs))
    return return_stmt(cast_self(construct(name_, pairs)))


def bool_or(tests: Sequence[ast.expr]) -> ast.expr:
    """``a or b or ...`` (a single test is returned bare, matching the string gen)."""
    return tests[0] if len(tests) == 1 else ast.BoolOp(op=ast.Or(), values=list(tests))


def bool_and(tests: Sequence[ast.expr]) -> ast.expr:
    """``a and b and ...`` (a single test is returned bare)."""
    return tests[0] if len(tests) == 1 else ast.BoolOp(op=ast.And(), values=list(tests))
