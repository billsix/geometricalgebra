#!/usr/bin/env python
# Copyright (c) 2025-2026 William Emerison Six
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Generic Python-`ast` construction helpers for the code generator.

A small DSL for building syntax-tree nodes (``nm``/``dot``/``call``/``cast``/``fn``/
``cls``/``ann_assign``/...) and rendering them with ``ast.unparse`` (``module_source``).
Knows nothing about geometric algebra -- it only knows the conventions of the code
this generator emits (e.g. ``cast_self``/``cast_coef`` wrap ``typing.cast`` to
``typing.Self``/``Coef`` (the coefficient type)).  Used by tools/gen_specialized.py.
"""

from __future__ import annotations

import ast


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


def nm(ident: str) -> ast.Name:
    return ast.Name(id=ident, ctx=_LOAD)


def dot(value, *parts: str) -> ast.expr:
    node = value if isinstance(value, ast.AST) else nm(value)
    for p in parts:
        node = ast.Attribute(value=node, attr=p, ctx=_LOAD)
    return node


def lit(v) -> ast.Constant:
    return ast.Constant(value=v)


def call(func, args=(), **kwargs) -> ast.Call:
    f = func if isinstance(func, ast.AST) else nm(func)
    return ast.Call(
        func=f,
        args=list(args),
        keywords=[ast.keyword(arg=k, value=v) for k, v in kwargs.items()],
    )


def cast(type_node, value) -> ast.Call:
    return call(dot("typing", "cast"), [type_node, value])


def cast_self(value) -> ast.Call:
    return cast(dot("typing", "Self"), value)


def cast_operand(value) -> ast.Call:
    # cast to the sandwich operand TypeVar ``_OperandT`` (imported from base) --
    # a versor conjugation returns the *operand's* own type, not ``Self``.
    return cast(nm("_OperandT"), value)


def cast_coef(value) -> ast.expr:
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
    return cast(nm("Coef"), value)


def ret(value) -> ast.Return:
    return ast.Return(value=value)


def subscript(value, index) -> ast.Subscript:
    return ast.Subscript(value=value, slice=index, ctx=_LOAD)


def opt_int() -> ast.expr:
    """The annotation ``int | None``."""
    return ast.BinOp(left=nm("int"), op=ast.BitOr(), right=lit(None))


def arg(name_, annotation=None) -> ast.arg:
    return ast.arg(arg=name_, annotation=annotation)


def fn(name_, body, params=None, defaults=(), decorators=(), returns=None):
    """An ``ast.FunctionDef``; ``params`` are ``ast.arg`` (default ``[self]``)."""
    params = [arg("self")] if params is None else params
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
        body=body,
        decorator_list=list(decorators),
        returns=returns,
        type_params=[],
    )


def cls(name_, body, bases=("MultiVectorBase",), decorators=()) -> ast.ClassDef:
    return ast.ClassDef(
        name=name_,
        bases=[nm(b) for b in bases],
        keywords=[],
        body=body,
        decorator_list=list(decorators),
        type_params=[],
    )


def dataclass_decorator(**flags) -> ast.Call:
    return ast.Call(
        func=dot("dataclasses", "dataclass"),
        args=[],
        keywords=[ast.keyword(arg=k, value=lit(v)) for k, v in flags.items()],
    )


def ann_assign(target_name, annotation, value=None) -> ast.AnnAssign:
    return ast.AnnAssign(
        target=ast.Name(id=target_name, ctx=_STORE),
        annotation=annotation,
        value=value,
        simple=1,
    )


def assign(target_name, value) -> ast.Assign:
    return ast.Assign(targets=[ast.Name(id=target_name, ctx=_STORE)], value=value)


def isinstance_(value, types) -> ast.Call:
    type_node = (
        ast.Tuple(elts=list(types), ctx=_LOAD)
        if isinstance(types, (list, tuple))
        else types
    )
    return call("isinstance", [value, type_node])


def not_(node) -> ast.UnaryOp:
    return ast.UnaryOp(op=ast.Not(), operand=node)


def ne_zero(node) -> ast.Compare:
    return ast.Compare(left=node, ops=[ast.NotEq()], comparators=[lit(0)])


def construct(name_, pairs) -> ast.Call:
    """``Name(field=value, ...)`` with keywords in the given order."""
    return ast.Call(
        func=nm(name_),
        args=[],
        keywords=[ast.keyword(arg=f, value=v) for f, v in pairs],
    )


def return_construct(name_, pairs) -> ast.stmt:
    """``return cast(Self, Name(field=value, ...))`` (the no-local return idiom)."""
    return ret(cast_self(construct(name_, pairs)))


def bool_or(tests) -> ast.expr:
    """``a or b or ...`` (a single test is returned bare, matching the string gen)."""
    return tests[0] if len(tests) == 1 else ast.BoolOp(op=ast.Or(), values=tests)


def bool_and(tests) -> ast.expr:
    """``a and b and ...`` (a single test is returned bare)."""
    return tests[0] if len(tests) == 1 else ast.BoolOp(op=ast.And(), values=tests)
