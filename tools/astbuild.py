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
``cls``/``ann_assign``/...) and rendering them with ``ast.unparse`` (``module_source``).
Knows nothing about geometric algebra -- it only knows the conventions of the code
this generator emits (e.g. ``cast_self``/``cast_coef`` wrap ``typing.cast`` to
``typing.Self``/``Coef`` (the coefficient type)).  Used by tools/gen_specialized.py.
"""

from __future__ import annotations

import ast
import typing
from collections.abc import Iterable, Sequence


def parse_expr(src: str) -> ast.expr:
    """Parse a source snippet into a single expression node."""
    return ast.parse(src, mode="eval").body


def module_source(body: list[ast.stmt]) -> str:
    """Render top-level statement nodes to source via `ast.unparse`."""
    module = ast.Module(body=body, type_ignores=[])
    return ast.unparse(ast.fix_missing_locations(module))


class SymbolToAttr(ast.NodeTransformer):
    """Rewrite operand-symbol ``Name`` nodes to attribute access.

    ``rename`` maps a sympy symbol name (e.g. ``a_e_1``) to an ``(object, attr)``
    pair (e.g. ``("self", "e_1")``).  Replaces the old word-boundary regex on
    rendered source with a structural, correct-by-construction transform.
    """

    def __init__(self, rename: dict[str, tuple[str, str]]):
        self.rename = rename

    def visit_Name(self, node: ast.Name) -> ast.AST:
        target = self.rename.get(node.id)
        if target is None:
            return node
        obj, attr = target
        return ast.Attribute(
            value=ast.Name(id=obj, ctx=ast.Load()), attr=attr, ctx=ast.Load()
        )


_LOAD = ast.Load()

_STORE = ast.Store()


def name_ref(ident: str) -> ast.Name:
    return ast.Name(id=ident, ctx=_LOAD)


def attribute(value: ast.expr | str, *parts: str) -> ast.expr:
    node = value if isinstance(value, ast.AST) else name_ref(value)
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
    f = func if isinstance(func, ast.AST) else name_ref(func)
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
    arguments = ast.arguments(
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


def ann_assign(
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
    type_node = (
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
    name_: str, pairs: Iterable[tuple[str, ast.expr]], owner: str | None = None
) -> ast.stmt:
    """``return cast(Self, Name(field=value, ...))`` (the no-local return idiom).

    When ``owner`` names the class being generated and the result type equals
    it, emit ``return type(self)(...)`` instead so subclasses get their own
    type back from same-type operations (no cast needed: ``type(self)`` is
    ``type[Self]``)."""
    if owner is not None and owner == name_:
        return return_stmt(construct_type_self(pairs))
    return return_stmt(cast_self(construct(name_, pairs)))


def bool_or(tests: Sequence[ast.expr]) -> ast.expr:
    """``a or b or ...`` (a single test is returned bare, matching the string gen)."""
    return tests[0] if len(tests) == 1 else ast.BoolOp(op=ast.Or(), values=list(tests))


def bool_and(tests: Sequence[ast.expr]) -> ast.expr:
    """``a and b and ...`` (a single test is returned bare)."""
    return tests[0] if len(tests) == 1 else ast.BoolOp(op=ast.And(), values=list(tests))
