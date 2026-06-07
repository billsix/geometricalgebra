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

"""Generate the specialized G1 / G2 / G3 multivector classes.

These are named-field dataclasses for 𝒢₁, 𝒢₂ and 𝒢₃ whose ``_geometric_product``
is the closed-form product, derived *from the general Gn symbolic product* so the
fast path is provably consistent with the reference implementation.  Common
sub-expressions are factored out with ``sympy.cse``.

Each algebra is written to its own committed module -- ``g1.py``, ``g2.py``,
``g3.py`` -- so a newcomer can import just the one they need
(``from geometricalgebra.g2 import G2``).  Re-run this script by hand when the
algebra changes:

    python tools/gen_specialized.py
"""

import ast
import inspect
import os
import subprocess
import sys
import textwrap
from collections import namedtuple
from itertools import chain, combinations

import sympy

# allow running from the repo root without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from geometricalgebra.base import AbstractMultiVector, BladeCoef  # noqa: E402
from geometricalgebra.gn import Gn  # noqa: E402

# ==========================================================================
# AST emission layer.  Code is assembled as Python `ast` nodes and rendered
# with `ast.unparse`, rather than concatenated as raw strings.  Two helpers do
# the heavy lifting:
#   * `parse_stmts` / `parse_expr` -- "template-splice": parse a source snippet
#     into nodes, the stdlib's nearest thing to a Lisp quasiquote.
#   * `SymbolToAttr` -- rewrites the operand symbols sympy prints (``a_e_1``,
#     ``b_e_12``) into attribute access (``self.e_1``, ``rhs.e_12``).  This is the
#     AST-native replacement for the old regex-on-source rename.
# `ast.unparse` output is canonical (no comments, its own wrapping); ruff then
# formats it.  The file header (copyright + imports) stays raw text -- comments
# cannot be represented in an AST.
# ==========================================================================


def parse_stmts(src: str) -> list[ast.stmt]:
    """Parse a source snippet into a list of statement nodes (template-splice)."""
    return ast.parse(textwrap.dedent(src)).body


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


def expr_to_ast(expr, rename: dict[str, tuple[str, str]]) -> ast.expr:
    """sympy expression -> AST expression with operand symbols as attribute access."""
    tree = parse_expr(sympy.sstr(expr))
    return ast.fix_missing_locations(SymbolToAttr(rename).visit(tree))


# ==========================================================================
# C (hand-built nodes) layer.  Every class / method / statement / expression is
# constructed as explicit `ast` nodes -- no source text for bodies.  These small
# builders keep that tolerable (and, tellingly, start to resemble a quasiquote --
# i.e. B).  The math still flows through `expr_to_ast`; the file header stays raw.
# ==========================================================================

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


def cast_real(value) -> ast.Call:
    return cast(dot("numbers", "Real"), value)


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


def cls(name_, body, bases=("AbstractMultiVector",), decorators=()) -> ast.ClassDef:
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


def method_doc(method_name, indent="        ") -> list[ast.stmt]:
    """The base method's docstring as a leading ``Expr(Constant)``, or ``[]``.

    The Constant value reproduces what the string generator emitted (a leading
    newline + ``indent``-prefixed lines), so the parsed AST matches for parity.
    """
    member = getattr(AbstractMultiVector, method_name, None)
    doc = inspect.getdoc(member) if member is not None else None
    if not doc:
        return []
    body = "\n".join(f"{indent}{line}".rstrip() for line in doc.splitlines())
    return [ast.Expr(value=lit(f"\n{body}\n{indent}"))]


def class_doc(text: str) -> ast.Expr:
    """A class docstring statement -- ``text`` used verbatim."""
    return ast.Expr(value=lit(text))


def coerce_pair_gn() -> list[ast.stmt]:
    """The ``left/right: Gn = Gn.from_blade_dict(self/rhs.to_blade_dict())`` pair."""
    return [
        ann_assign(
            "left",
            nm("Gn"),
            call(dot("Gn", "from_blade_dict"), [call(dot("self", "to_blade_dict"))]),
        ),
        ann_assign(
            "right",
            nm("Gn"),
            call(dot("Gn", "from_blade_dict"), [call(dot("rhs", "to_blade_dict"))]),
        ),
    ]


def eq_method() -> ast.FunctionDef:
    """The shared simplify-aware, cross-representation ``__eq__`` as nodes."""
    diff = ast.BinOp(
        left=call(
            dot("sympy", "sympify"), [call(dot("left", "get"), [nm("blade"), lit(0)])]
        ),
        op=ast.Sub(),
        right=call(
            dot("sympy", "sympify"), [call(dot("right", "get"), [nm("blade"), lit(0)])]
        ),
    )
    gen = ast.GeneratorExp(
        elt=ast.Compare(
            left=call(dot("sympy", "simplify"), [diff]),
            ops=[ast.Eq()],
            comparators=[lit(0)],
        ),
        generators=[
            ast.comprehension(
                target=ast.Name("blade", _STORE),
                iter=ast.BinOp(
                    left=call("set", [call(dot("left", "keys"))]),
                    op=ast.BitOr(),
                    right=call("set", [call(dot("right", "keys"))]),
                ),
                ifs=[],
                is_async=0,
            )
        ],
    )
    body = [
        ast.If(
            test=not_(isinstance_(nm("other"), nm("AbstractMultiVector"))),
            body=[ret(nm("NotImplemented"))],
            orelse=[],
        ),
        assign("left", call(dot("self", "to_blade_dict"))),
        assign("right", call(dot("other", "to_blade_dict"))),
        ret(call("all", [gen])),
    ]
    return fn("__eq__", body, params=[arg("self"), arg("other")], returns=nm("bool"))


SCALAR_DOC = (
    "The grade-0 type -- a scalar, shared across every 𝒢ₙ.\n"
    "\n"
    "    ``Scalar * x`` scales ``x`` and returns x's type; pure-scalar product\n"
    "    results (e.g. Bivector2 * Bivector2) land here.  AUTO-GENERATED by\n"
    "    tools/gen_specialized.py."
)


def generate_scalar() -> list[ast.stmt]:
    """The shared grade-0 ``Scalar`` type, hand-built as `ast` nodes (level C)."""
    selfsc = dot("self", "scalar")

    def s(value):  # cast(typing.Self, Scalar(scalar=value))
        return cast_self(construct("Scalar", [("scalar", value)]))

    def sr(value):  # cast(typing.Self, Scalar(scalar=cast(numbers.Real, value)))
        return s(cast_real(value))

    def mul(a, b):
        return ast.BinOp(left=a, op=ast.Mult(), right=b)

    SELF = dot("typing", "Self")
    REAL = dot("numbers", "Real")
    numlike = [nm("int"), nm("float"), dot("sympy", "Expr")]

    body = [
        class_doc(SCALAR_DOC),
        ann_assign("scalar", REAL, cast_real(lit(0))),
        fn(
            "from_blade_dict",
            [
                assign("d", call("dict", [nm("blade_coef")])),
                ret(
                    call(
                        "cls",
                        scalar=cast_real(call(dot("d", "get"), [lit(()), lit(0)])),
                    )
                ),
            ],
            params=[arg("cls"), arg("blade_coef")],
            decorators=[nm("classmethod")],
            returns=SELF,
        ),
        fn(
            "to_blade_dict",
            [
                ret(
                    ast.IfExp(
                        test=ne_zero(selfsc),
                        body=ast.Dict(keys=[lit(())], values=[selfsc]),
                        orelse=ast.Dict(keys=[], values=[]),
                    )
                )
            ],
            returns=nm("BladeCoef"),
        ),
        eq_method(),
        fn(
            "__mul__",
            [
                ast.If(
                    isinstance_(nm("rhs"), numlike),
                    [ret(sr(mul(selfsc, nm("rhs"))))],
                    [],
                ),
                ret(call(dot("self", "_geometric_product"), [nm("rhs")])),
            ],
            params=[arg("self"), arg("rhs")],
            returns=SELF,
        ),
        fn(
            "__rmul__",
            [
                ast.If(
                    isinstance_(nm("lhs"), numlike),
                    [ret(sr(mul(nm("lhs"), selfsc)))],
                    [],
                ),
                ret(call(dot("self", "_geometric_product"), [nm("lhs")])),
            ],
            params=[arg("self"), arg("lhs")],
            returns=SELF,
        ),
        fn(
            "_geometric_product",
            [
                ast.If(
                    isinstance_(nm("rhs"), nm("Scalar")),
                    [ret(sr(mul(selfsc, dot("rhs", "scalar"))))],
                    [],
                ),
                ast.If(
                    isinstance_(nm("rhs"), nm("AbstractMultiVector")),
                    [ret(cast_self(mul(selfsc, nm("rhs"))))],
                    [],
                ),
                ret(sr(mul(selfsc, nm("rhs")))),
            ],
            params=[arg("self"), arg("rhs")],
            returns=SELF,
        ),
        fn(
            "outer_product",
            [ret(call(dot("self", "_geometric_product"), [nm("rhs")]))],
            params=[arg("self"), arg("rhs")],
            returns=SELF,
        ),
        fn(
            "inner_product",
            coerce_pair_gn()
            + [ret(cast_self(call(dot("left", "inner_product"), [nm("right")])))],
            params=[arg("self"), arg("rhs")],
            returns=SELF,
        ),
        fn(
            "__add__",
            [
                ast.If(
                    isinstance_(nm("rhs"), numlike),
                    [ret(sr(ast.BinOp(selfsc, ast.Add(), nm("rhs"))))],
                    [],
                ),
                ast.If(
                    isinstance_(nm("rhs"), nm("Scalar")),
                    [ret(s(ast.BinOp(selfsc, ast.Add(), dot("rhs", "scalar"))))],
                    [],
                ),
                ast.If(
                    isinstance_(nm("rhs"), nm("AbstractMultiVector")),
                    [ret(cast_self(ast.BinOp(nm("rhs"), ast.Add(), nm("self"))))],
                    [],
                ),
                ret(cast_self(nm("NotImplemented"))),
            ],
            params=[arg("self"), arg("rhs")],
            returns=SELF,
        ),
        fn(
            "__radd__",
            [ret(call(dot("self", "__add__"), [nm("lhs")]))],
            params=[arg("self"), arg("lhs")],
            returns=SELF,
        ),
        fn(
            "__sub__",
            [
                ret(
                    ast.BinOp(
                        nm("self"),
                        ast.Add(),
                        mul(ast.UnaryOp(ast.USub(), lit(1)), nm("rhs")),
                    )
                )
            ],
            params=[arg("self"), arg("rhs")],
            returns=SELF,
        ),
        fn(
            "__rsub__",
            [ret(ast.BinOp(ast.UnaryOp(ast.USub(), nm("self")), ast.Add(), nm("lhs")))],
            params=[arg("self"), arg("lhs")],
            returns=SELF,
        ),
        fn("__neg__", [ret(sr(ast.UnaryOp(ast.USub(), selfsc)))], returns=SELF),
        fn("reverse", [ret(s(selfsc))], returns=SELF),
        fn("scalar_part", [ret(selfsc)], returns=REAL),
        fn(
            "grades",
            [
                ret(
                    ast.IfExp(
                        test=ne_zero(selfsc),
                        body=ast.List(elts=[lit(0)], ctx=_LOAD),
                        orelse=ast.List(elts=[], ctx=_LOAD),
                    )
                )
            ],
            returns=subscript(nm("list"), nm("int")),
        ),
        fn(
            "is_close",
            [
                ast.If(
                    not_(isinstance_(nm("other"), nm("Scalar"))),
                    [ret(call(dot(call("super", []), "is_close"), [nm("other")]))],
                    [],
                ),
                ret(
                    call(
                        "bool",
                        [
                            call(
                                dot("np", "isclose"),
                                [
                                    call("float", [selfsc]),
                                    call("float", [dot("other", "scalar")]),
                                ],
                                rtol=lit(1e-5),
                                atol=lit(1e-5),
                            )
                        ],
                    )
                ),
            ],
            params=[arg("self"), arg("other")],
            returns=nm("bool"),
        ),
        fn(
            "__iter__",
            [
                ast.If(
                    ne_zero(selfsc),
                    [ast.Expr(ast.Yield(construct("Scalar", [("scalar", selfsc)])))],
                    [],
                )
            ],
        ),
        fn("even_part", [ret(s(selfsc))], returns=SELF),
        fn("odd_part", [ret(sr(lit(0)))], returns=SELF),
        fn(
            "r_vector_part",
            [
                ast.If(
                    ast.Compare(nm("r"), [ast.Eq()], [lit(0)]),
                    [ret(s(selfsc))],
                    [],
                ),
                ret(sr(lit(0))),
            ],
            params=[arg("self"), arg("r", nm("int"))],
            returns=SELF,
        ),
        fn(
            "dual",
            [
                ast.If(
                    ast.Compare(nm("n"), [ast.Is()], [lit(None)]),
                    [
                        ast.Raise(
                            exc=call(
                                "ValueError",
                                [lit("Scalar.dual needs an explicit dimension n")],
                            ),
                            cause=None,
                        )
                    ],
                    [],
                ),
                ret(
                    cast_self(
                        call(
                            dot(
                                call(
                                    dot("Gn", "from_blade_dict"),
                                    [call(dot("self", "to_blade_dict"))],
                                ),
                                "dual",
                            ),
                            [nm("n")],
                        )
                    )
                ),
            ],
            params=[arg("self"), arg("n", opt_int())],
            defaults=[lit(None)],
            returns=SELF,
        ),
    ]
    return [cls("Scalar", body, decorators=[dataclass_decorator(eq=False)])]


def _is_neg_term(term, rename) -> bool:
    return ast.unparse(expr_to_ast(term, rename)).lstrip().startswith("-")


def summed_value(expr, rename) -> ast.expr:
    """A constructor field value: grade-ordered sum of terms (≈ format_assignment).

    Constants are cast to ``numbers.Real``; sums fold left-assoc as ``BinOp`` in
    ``term_grade_key`` order, subtracting negative terms -- so the node tree matches
    the string baseline's operand order.
    """
    expr = sympy.sympify(expr)
    if not expr.free_symbols:
        return cast_real(expr_to_ast(expr, rename))
    terms = (
        sorted(expr.as_ordered_terms(), key=term_grade_key) if expr.is_Add else [expr]
    )
    node = expr_to_ast(terms[0], rename)
    for term in terms[1:]:
        if _is_neg_term(term, rename):
            node = ast.BinOp(left=node, op=ast.Sub(), right=expr_to_ast(-term, rename))
        else:
            node = ast.BinOp(left=node, op=ast.Add(), right=expr_to_ast(term, rename))
    return node


def result_value(expr, rename) -> ast.expr:
    """Constructor field value for the graded dispatch (mirrors result_block)."""
    e = sympy.sympify(expr)
    if e.is_Mul and (-e).is_Symbol:
        return cast_real(expr_to_ast(e, rename))
    return summed_value(e, rename)


def unary_value(expr, rename) -> ast.expr:
    """Constructor field value for unary results (mirrors unary_return)."""
    e = sympy.sympify(expr)
    return expr_to_ast(e, rename) if e.is_Symbol else cast_real(expr_to_ast(e, rename))


def rename_map(blades_self, blades_rhs) -> dict[str, tuple[str, str]]:
    """Operand-symbol rename map for ``expr_to_ast`` (a_<f>->self, b_<f>->rhs)."""
    r: dict[str, tuple[str, str]] = {}
    for b in blades_self:
        r["a_" + field_name(b)] = ("self", field_name(b))
    for b in blades_rhs:
        r["b_" + field_name(b)] = ("rhs", field_name(b))
    return r


def result_return(name_, pairs) -> list[ast.stmt]:
    """``result: Name = Name(...); return cast(Self, result)`` as nodes."""
    return [
        ann_assign("result", nm(name_), construct(name_, pairs)),
        ret(cast_self(nm("result"))),
    ]


def field_decls(blades) -> list[ast.stmt]:
    """``<field>: numbers.Real = cast(numbers.Real, 0)`` per blade."""
    return [
        ann_assign(field_name(b), dot("numbers", "Real"), cast_real(lit(0)))
        for b in blades
    ]


def dimension_decl(n) -> ast.stmt:
    """``DIMENSION: typing.ClassVar[int] = <n>``."""
    return ann_assign(
        "DIMENSION", subscript(dot("typing", "ClassVar"), nm("int")), lit(n)
    )


def from_blade_dict_method(blades) -> ast.stmt:
    """The ``from_blade_dict`` classmethod over the given blades."""
    keywords = [
        ast.keyword(
            arg=field_name(b),
            value=cast_real(call(dot("d", "get"), [lit(b), lit(0)])),
        )
        for b in blades
    ]
    body = [
        assign("d", call("dict", [nm("blade_coef")])),
        ret(ast.Call(func=nm("cls"), args=[], keywords=keywords)),
    ]
    return fn(
        "from_blade_dict",
        body,
        params=[arg("cls"), arg("blade_coef")],
        decorators=[nm("classmethod")],
        returns=dot("typing", "Self"),
    )


def to_blade_dict_method(blades) -> ast.stmt:
    """The ``to_blade_dict`` dict-comprehension method over the given blades."""
    pairs_iter = ast.Tuple(
        elts=[
            ast.Tuple(elts=[lit(b), dot("self", field_name(b))], ctx=_LOAD)
            for b in blades
        ],
        ctx=_LOAD,
    )
    comp = ast.comprehension(
        target=ast.Tuple(
            elts=[ast.Name("blade", _STORE), ast.Name("coef", _STORE)], ctx=_STORE
        ),
        iter=pairs_iter,
        ifs=[ne_zero(nm("coef"))],
        is_async=0,
    )
    dictcomp = ast.DictComp(key=nm("blade"), value=nm("coef"), generators=[comp])
    return fn("to_blade_dict", [ret(dictcomp)], returns=nm("BladeCoef"))


def bool_or(tests) -> ast.expr:
    """``a or b or ...`` (a single test is returned bare, matching the string gen)."""
    return tests[0] if len(tests) == 1 else ast.BoolOp(op=ast.Or(), values=tests)


def bool_and(tests) -> ast.expr:
    """``a and b and ...`` (a single test is returned bare)."""
    return tests[0] if len(tests) == 1 else ast.BoolOp(op=ast.And(), values=tests)


def isclose_call(field, other="other") -> ast.expr:
    """``np.isclose(float(self.<f>), float(other.<f>), rtol=1e-5, atol=1e-5)``."""
    return call(
        dot("np", "isclose"),
        [call("float", [dot("self", field)]), call("float", [dot(other, field)])],
        rtol=lit(1e-5),
        atol=lit(1e-5),
    )


def super_call(method, args) -> ast.expr:
    """``super().<method>(<args>)``."""
    return call(dot(call("super", []), method), args)


def dim_or_n(owner="self") -> ast.expr:
    """``<owner>.DIMENSION if n is None else n``."""
    return ast.IfExp(
        test=ast.Compare(nm("n"), [ast.Is()], [lit(None)]),
        body=dot(owner, "DIMENSION"),
        orelse=nm("n"),
    )


def out_path(filename: str) -> str:
    return os.path.join(
        os.path.dirname(__file__), "..", "src", "geometricalgebra", filename
    )


def blades_for_dim(n: int) -> list[tuple[int, ...]]:
    """All 2**n basis blades of 𝒢ₙ in canonical (grade, then index) order."""
    idx = list(range(1, n + 1))
    powerset = chain.from_iterable(combinations(idx, r) for r in range(n + 1))
    return sorted(powerset, key=lambda b: (len(b), b))


def field_name(blade: tuple[int, ...]) -> str:
    """() -> 'scalar', (1,) -> 'e_1', (1, 2) -> 'e_12', (1, 2, 3) -> 'e_123'."""
    if blade == ():
        return "scalar"
    return "e_" + "".join(str(i) for i in blade)


def blade_of_field(field: str) -> tuple[int, ...]:
    """Inverse of ``field_name``: 'scalar'->(), 'e_1'->(1,), 'e_12'->(1, 2).

    Assumes single-digit basis indices (n < 10), which the field naming already
    requires (``e_12`` is otherwise ambiguous).
    """
    if field == "scalar":
        return ()
    return tuple(int(c) for c in field[2:])


def term_grade_key(term) -> tuple[int, tuple[int, ...], int, tuple[int, ...]]:
    """Grade-ordering key for one additive term ``self.<L> * rhs.<R>``.

    Orders by ``(grade(L), indices(L), grade(R), indices(R))`` so the generated
    sums read scalar -> vector -> bivector -> ... (instead of sympy's roughly
    lexicographic-by-name order, where e.g. ``e_12`` sorts before ``e_2``).  The
    term is a product of one ``a_<field>`` (self) and one ``b_<field>`` (rhs)
    symbol.  A term carrying neither (e.g. a future ``cse`` temporary -- the
    products produce none today) sorts last.
    """
    sentinel = (99, ())
    left = right = None
    for sym in term.free_symbols:
        if sym.name.startswith("a_"):
            blade = blade_of_field(sym.name[2:])
            left = (len(blade), blade)
        elif sym.name.startswith("b_"):
            blade = blade_of_field(sym.name[2:])
            right = (len(blade), blade)
    left = left if left is not None else sentinel
    right = right if right is not None else sentinel
    return (left[0], left[1], right[0], right[1])


def _sub(k: int) -> str:
    return "".join("₀₁₂₃₄₅₆₇₈₉"[int(d)] for d in str(k))


def _sup(k: int) -> str:
    return "".join("⁰¹²³⁴⁵⁶⁷⁸⁹"[int(d)] for d in str(k))


def generic_docstring(n: int) -> str:
    """Standard class docstring for any dimension (fallback for unknown n)."""
    bl: list[tuple[int, ...]] = blades_for_dim(n)
    grades = "\n".join(
        f"        {', '.join(field_name(b) for b in bl if len(b) == g)}  (grade {g})"
        for g in range(n + 1)
    )
    return (
        f"An element (multivector) of 𝒢{_sub(n)}, the geometric algebra of\n"
        f"    {n}-dimensional Euclidean space ℝ{_sup(n)} (Hestenes' notation).\n"
        "\n"
        f"    𝒢{_sub(n)} has 2{_sup(n)} = {2**n} basis blades,"
        " stored as named fields:\n"
        f"{grades}\n"
        "\n"
        f"    A specialized, performant representation of 𝒢{_sub(n)}; see Gn for the\n"
        f"    general 𝒢ₙ case.  Terminology: 𝒢{_sub(n)} denotes the *algebra*; an\n"
        "    instance of this class is an *element of* it.\n"
        "\n"
        "    Coefficients are NOT eagerly simplified (unlike Gn); they are simplified\n"
        "    lazily, on equality.  AUTO-GENERATED by tools/gen_specialized.py."
    )


def docstring_for(n: int) -> str:
    """Hand-written docstring for 1/2/3, else a generic generated one."""
    return DOCSTRINGS.get(n, generic_docstring(n))


DOCSTRINGS = {
    1: (
        "An element (multivector) of 𝒢₁, the geometric algebra of the Euclidean\n"
        "    line ℝ¹ (Hestenes' notation) -- the simplest geometric algebra.\n"
        "\n"
        "    𝒢₁ has 2¹ = 2 basis blades, stored as named fields:\n"
        "        scalar          grade 0 (scalar)\n"
        "        e_1             grade 1 (the lone vector / pseudoscalar)\n"
        "\n"
        "    A specialized, performant representation of 𝒢₁; see Gn for the general\n"
        "    𝒢ₙ case.  Terminology: 𝒢₁ denotes the *algebra*; an instance of this\n"
        "    class is an *element of* 𝒢₁.\n"
        "\n"
        "    Coefficients are NOT eagerly simplified (unlike Gn); they are simplified\n"
        "    lazily, on equality.  AUTO-GENERATED by tools/gen_specialized.py."
    ),
    2: (
        "An element (multivector) of 𝒢₂, the geometric algebra of the Euclidean\n"
        "    plane ℝ² (Hestenes' notation).\n"
        "\n"
        "    𝒢₂ has 2² = 4 basis blades, stored as named fields:\n"
        "        scalar          grade 0 (scalar)\n"
        "        e_1, e_2        grade 1 (vectors)\n"
        "        e_12            grade 2 (bivector / pseudoscalar)\n"
        "\n"
        "    A specialized, performant representation of 𝒢₂; see Gn for the general\n"
        "    𝒢ₙ case.  Terminology: 𝒢₂ denotes the *algebra*; an instance of this\n"
        "    class is an *element of* 𝒢₂.\n"
        "\n"
        "    Coefficients are NOT eagerly simplified (unlike Gn); they are simplified\n"
        "    lazily, on equality.  AUTO-GENERATED by tools/gen_specialized.py."
    ),
    3: (
        "An element (multivector) of 𝒢₃, the geometric algebra of 3D Euclidean\n"
        '    space ℝ³ (Hestenes\' "algebra of physical space"; the Pauli algebra).\n'
        "\n"
        "    𝒢₃ has 2³ = 8 basis blades, stored as named fields:\n"
        "        scalar                  grade 0 (scalar)\n"
        "        e_1, e_2, e_3           grade 1 (vectors)\n"
        "        e_12, e_13, e_23        grade 2 (bivectors)\n"
        "        e_123                   grade 3 (trivector / pseudoscalar)\n"
        "\n"
        "    A specialized, performant representation of 𝒢₃; see Gn for the general\n"
        "    𝒢ₙ case.  Terminology: 𝒢₃ denotes the *algebra*; an instance of this\n"
        "    class is an *element of* 𝒢₃.\n"
        "\n"
        "    Coefficients are NOT eagerly simplified (unlike Gn); they are simplified\n"
        "    lazily, on equality.  AUTO-GENERATED by tools/gen_specialized.py."
    ),
}


# ==========================================================================
# Graded subtypes (Phase 2): per-dimension type registry + closure resolution.
#
# A "type" is a class over a *subset* of blades.  TypeSpec.kind is one of
# "scalar" (the shared grade-0 type), "graded" (Vector/Bivector/.../Rotor), or
# "full" (the existing all-blades G_n).  The geometric/inner/outer product of two
# typed operands is dispatched by a structural ``match`` on the rhs type; the
# *return type* is decided here, symbolically, by ``resolve``: the smallest
# registered type whose blade-set covers the support of the symbolic result.
# ==========================================================================

TypeSpec = namedtuple("TypeSpec", "name blades dim kind")

# the shared grade-0 type (the same scalar lives in every dimension)
SCALAR = TypeSpec("Scalar", ((),), 0, "scalar")


def graded_specs(n: int) -> list[TypeSpec]:
    """The graded (grade-pure + even/Rotor) types of 𝒢ₙ, per the Phase 1 registry."""
    bl: list[tuple[int, ...]] = blades_for_dim(n)

    def by_grade(g: int) -> tuple:
        return tuple(b for b in bl if len(b) == g)

    specs: list[TypeSpec] = [TypeSpec(f"Vector{n}", by_grade(1), n, "graded")]
    if n >= 2:
        specs.append(TypeSpec(f"Bivector{n}", by_grade(2), n, "graded"))
    if n >= 3:
        specs.append(TypeSpec(f"Trivector{n}", by_grade(3), n, "graded"))
    if n >= 2:  # even subalgebra (Rotor); for n==1 the even part is just the scalar
        even: tuple[tuple[int, ...], ...] = tuple(b for b in bl if len(b) % 2 == 0)
        specs.append(TypeSpec(f"Rotor{n}", even, n, "graded"))
    return specs


def full_spec(n: int, full_name: str) -> TypeSpec:
    return TypeSpec(full_name, tuple(blades_for_dim(n)), n, "full")


def registry_for_dim(n: int, full_name: str) -> list[TypeSpec]:
    """Scalar + graded types + the full G_n -- every type a result can resolve to."""
    return [SCALAR, *graded_specs(n), full_spec(n, full_name)]


def resolve(support, n: int, full_name: str) -> TypeSpec:
    """Smallest registered type covering ``support`` (the full G_n always does)."""
    want: set[tuple[int, ...]] = set(support)
    candidates: list[TypeSpec] = [
        t for t in registry_for_dim(n, full_name) if want <= set(t.blades)
    ]
    return min(
        candidates,
        key=lambda t: (len(t.blades), 0 if t.kind == "scalar" else 1, t.name),
    )


def product_result(t1: TypeSpec, t2: TypeSpec, gn_op, n: int, full_name: str):
    """(result_spec, output exprs over result's blades) for t1 <op> t2."""
    a_syms: dict[tuple[int, ...], sympy.Symbol] = {
        b: sympy.Symbol("a_" + field_name(b)) for b in t1.blades
    }
    b_syms: dict[tuple[int, ...], sympy.Symbol] = {
        b: sympy.Symbol("b_" + field_name(b)) for b in t2.blades
    }
    result_mv: Gn = gn_op(Gn.from_blade_dict(a_syms), Gn.from_blade_dict(b_syms))
    rd: BladeCoef = result_mv.to_blade_dict()
    support: list[tuple[int, ...]] = [
        b for b in blades_for_dim(n) if sympy.sympify(rd.get(b, 0)) != 0
    ]
    rspec: TypeSpec = resolve(support, n, full_name)
    out_exprs: list[sympy.Expr] = [sympy.sympify(rd.get(b, 0)) for b in rspec.blades]
    return rspec, out_exprs


def unary_result(t1: TypeSpec, gn_fn, n: int, full_name: str):
    """(result_spec, output exprs) for a unary op (dual / grade projection)."""
    a_syms: dict[tuple[int, ...], sympy.Symbol] = {
        b: sympy.Symbol("a_" + field_name(b)) for b in t1.blades
    }
    result_mv: Gn = gn_fn(Gn.from_blade_dict(a_syms))
    rd: BladeCoef = result_mv.to_blade_dict()
    support: list[tuple[int, ...]] = [
        b for b in blades_for_dim(n) if sympy.sympify(rd.get(b, 0)) != 0
    ]
    rspec: TypeSpec = resolve(support, n, full_name)
    out_exprs: list[sympy.Expr] = [sympy.sympify(rd.get(b, 0)) for b in rspec.blades]
    return rspec, out_exprs


def generate_class(n: int, name: str) -> list[ast.stmt]:
    """The full all-blades G_n class, hand-built as `ast` nodes (level C)."""
    blades = blades_for_dim(n)
    fields = [field_name(b) for b in blades]
    rename = rename_map(blades, blades)
    a_mv = Gn.from_blade_dict({b: sympy.Symbol("a_" + field_name(b)) for b in blades})
    b_mv = Gn.from_blade_dict({b: sympy.Symbol("b_" + field_name(b)) for b in blades})
    by_grade = {g: [b for b in blades if len(b) == g] for g in range(n + 1)}
    SELF = dot("typing", "Self")

    def bilinear(method, cross_node, result_mv):
        rd = result_mv.to_blade_dict()
        replacements, reduced = sympy.cse([sympy.sympify(rd.get(b, 0)) for b in blades])
        body = method_doc(method) + [
            ast.If(
                not_(isinstance_(nm("rhs"), nm(name))),
                coerce_pair_gn() + [ret(cast_self(cross_node))],
                [],
            )
        ]
        body += [assign(str(t), expr_to_ast(e, rename)) for t, e in replacements]
        pairs = [
            (field_name(b), summed_value(e, rename)) for b, e in zip(blades, reduced)
        ]
        body += result_return(name, pairs)
        return fn(method, body, params=[arg("self"), arg("rhs")], returns=SELF)

    def linear(method, op_cls, gn_op_cls):
        return fn(
            method,
            [
                ast.If(
                    not_(isinstance_(nm("rhs"), nm(name))),
                    coerce_pair_gn()
                    + [ret(cast_self(ast.BinOp(nm("left"), gn_op_cls(), nm("right"))))],
                    [],
                ),
                *result_return(
                    name,
                    [
                        (f, ast.BinOp(dot("self", f), op_cls(), dot("rhs", f)))
                        for f in fields
                    ],
                ),
            ],
            params=[arg("self"), arg("rhs")],
            returns=SELF,
        )

    grades_body: list[ast.stmt] = [
        ann_assign("present", subscript(nm("list"), nm("int")), ast.List([], _LOAD))
    ]
    for g in range(n + 1):
        grades_body.append(
            ast.If(
                bool_or([ne_zero(dot("self", field_name(b))) for b in by_grade[g]]),
                [ast.Expr(call(dot("present", "append"), [lit(g)]))],
                [],
            )
        )
    grades_body.append(ret(nm("present")))

    rvp_cases = [
        ast.match_case(
            pattern=ast.MatchValue(lit(g)),
            body=result_return(
                name, [(field_name(b), dot("self", field_name(b))) for b in by_grade[g]]
            ),
        )
        for g in range(n + 1)
    ]
    rvp_cases.append(
        ast.match_case(
            pattern=ast.MatchAs(pattern=None, name=None), body=result_return(name, [])
        )
    )

    rev_pairs = []
    for b in blades:
        f = field_name(b)
        sign = (-1) ** ((len(b) * (len(b) - 1)) // 2)
        rev_pairs.append(
            (
                f,
                dot("self", f)
                if sign == 1
                else cast_real(ast.UnaryOp(ast.USub(), dot("self", f))),
            )
        )

    def grade_copy(parity):
        return [
            (field_name(b), dot("self", field_name(b)))
            for b in blades
            if len(b) % 2 == parity
        ]

    body = [
        class_doc(docstring_for(n)),
        dimension_decl(n),
        *field_decls(blades),
        from_blade_dict_method(blades),
        to_blade_dict_method(blades),
        eq_method(),
        bilinear(
            "_geometric_product",
            ast.BinOp(nm("left"), ast.Mult(), nm("right")),
            a_mv * b_mv,
        ),
        bilinear(
            "inner_product",
            call(dot("left", "inner_product"), [nm("right")]),
            a_mv.inner_product(b_mv),
        ),
        bilinear(
            "outer_product",
            call(dot("left", "outer_product"), [nm("right")]),
            a_mv.outer_product(b_mv),
        ),
        linear("__add__", ast.Add, ast.Add),
        linear("__sub__", ast.Sub, ast.Sub),
        fn(
            "__neg__",
            result_return(
                name,
                [
                    (f, cast_real(ast.UnaryOp(ast.USub(), dot("self", f))))
                    for f in fields
                ],
            ),
            returns=SELF,
        ),
        fn(
            "scalar_part",
            method_doc("scalar_part") + [ret(dot("self", "scalar"))],
            returns=dot("numbers", "Real"),
        ),
        fn("grades", grades_body, returns=subscript(nm("list"), nm("int"))),
        fn(
            "r_vector_part",
            method_doc("r_vector_part") + [ast.Match(subject=nm("r"), cases=rvp_cases)],
            params=[arg("self"), arg("r", nm("int"))],
            returns=SELF,
        ),
        fn(
            "reverse",
            method_doc("reverse") + result_return(name, rev_pairs),
            returns=SELF,
        ),
        fn(
            "even_part",
            method_doc("even_part") + result_return(name, grade_copy(0)),
            returns=SELF,
        ),
        fn(
            "odd_part",
            method_doc("odd_part") + result_return(name, grade_copy(1)),
            returns=SELF,
        ),
        fn(
            "is_close",
            [
                ast.If(
                    not_(isinstance_(nm("other"), nm(name))),
                    [ret(super_call("is_close", [nm("other")]))],
                    [],
                ),
                ret(call("bool", [bool_and([isclose_call(f) for f in fields])])),
            ],
            params=[arg("self"), arg("other")],
            returns=nm("bool"),
        ),
        fn(
            "__iter__",
            [
                ast.If(
                    ne_zero(dot("self", field_name(b))),
                    [
                        ast.Expr(
                            ast.Yield(
                                construct(
                                    name, [(field_name(b), dot("self", field_name(b)))]
                                )
                            )
                        )
                    ],
                    [],
                )
                for b in blades
            ],
        ),
        fn(
            "dual",
            method_doc("dual") + [ret(super_call("dual", [dim_or_n("self")]))],
            params=[arg("self"), arg("n", opt_int())],
            defaults=[lit(None)],
            returns=SELF,
        ),
        fn(
            "unit_pseudoscalar",
            method_doc("unit_pseudoscalar")
            + [ret(super_call("unit_pseudoscalar", [dim_or_n("cls")]))],
            params=[arg("cls"), arg("n", opt_int())],
            defaults=[lit(None)],
            decorators=[nm("classmethod")],
            returns=SELF,
        ),
        fn(
            "unit_pseudoscalar_squared",
            [ret(super_call("unit_pseudoscalar_squared", [dim_or_n("cls")]))],
            params=[arg("cls"), arg("n", opt_int())],
            defaults=[lit(None)],
            decorators=[nm("classmethod")],
            returns=SELF,
        ),
        fn(
            "bases",
            [ret(super_call("bases", [dim_or_n("cls")]))],
            params=[arg("cls"), arg("n", opt_int())],
            defaults=[lit(None)],
            decorators=[nm("classmethod")],
            returns=subscript(nm("Generator"), SELF),
        ),
        fn(
            "symbolic_multivector",
            [ret(super_call("symbolic_multivector", [dim_or_n("cls"), nm("prefix")]))],
            params=[arg("cls"), arg("n", opt_int()), arg("prefix", nm("str"))],
            defaults=[lit(None), lit("a")],
            decorators=[nm("classmethod")],
            returns=SELF,
        ),
    ]
    return [cls(name, body, decorators=[dataclass_decorator(eq=False, slots=True)])]


# The simplify-aware, cross-representation __eq__ (shared by every type), as a
# source template at module indent.  Spliced into the class templates as $eq.
def graded_docstring(spec: TypeSpec) -> str:
    grade_words = {0: "scalar", 1: "vector", 2: "bivector", 3: "trivector"}
    fields = ", ".join(field_name(b) for b in spec.blades)
    kind = (
        "the even subalgebra (rotor / spinor)"
        if spec.name.startswith("Rotor")
        else "the grade-%d (%s) part"
        % (len(spec.blades[0]), grade_words.get(len(spec.blades[0]), "k-vector"))
        if len({len(b) for b in spec.blades}) == 1
        else "a graded part"
    )
    return (
        f"An element of {kind}\n"
        f"    of 𝒢{_sub(spec.dim)}.  Stored as the named fields: {fields}.\n\n"
        "    A graded subtype: products dispatch by operand type and return the\n"
        "    grade-correct type (e.g. vector*vector -> the even/Rotor type).  "
        "Results\n    that span grades no graded type covers widen to "
        f"{full_name_for(spec.dim)}.\n    AUTO-GENERATED by tools/gen_specialized.py."
    )


def full_name_for(dim: int) -> str:
    return f"G{dim}"


# --- C node builders for the graded subtypes ---


def scaled_nodes(name_, fields, value_fn) -> ast.stmt:
    """``return cast(Self, Name(field=cast(Real, value_fn(field)), ...))``."""
    return ret(
        cast_self(construct(name_, [(f, cast_real(value_fn(f))) for f in fields]))
    )


def result_block_nodes(rspec, out_exprs, rename) -> list[ast.stmt]:
    """cse temps + ``return cast(Self, RType(...))`` (= result_block, as nodes)."""
    replacements, reduced = sympy.cse(out_exprs)
    stmts: list[ast.stmt] = [
        assign(str(t), expr_to_ast(e, rename)) for t, e in replacements
    ]
    pairs = [
        (field_name(b), result_value(e, rename)) for b, e in zip(rspec.blades, reduced)
    ]
    stmts.append(ret(cast_self(construct(rspec.name, pairs))))
    return stmts


def unary_nodes(rspec, out_exprs, rename) -> ast.stmt:
    """``return cast(Self, RType(...))`` (= unary_return, as nodes)."""
    pairs = [
        (field_name(b), unary_value(e, rename)) for b, e in zip(rspec.blades, out_exprs)
    ]
    return ret(cast_self(construct(rspec.name, pairs)))


def _match_class(cls_node) -> ast.MatchClass:
    return ast.MatchClass(cls=cls_node, patterns=[], kwd_attrs=[], kwd_patterns=[])


def dispatch_nodes(t1, method, gn_op, n, full_name, fallback_node, number_case=False):
    """A method that ``match``es on the rhs type, as `ast` nodes (= dispatch_method)."""
    cases: list[ast.match_case] = []
    if number_case:
        cases.append(
            ast.match_case(
                pattern=ast.MatchOr(
                    patterns=[
                        _match_class(nm("int")),
                        _match_class(nm("float")),
                        _match_class(dot("sympy", "Expr")),
                    ]
                ),
                body=[
                    ret(
                        call(
                            dot("self", method),
                            [construct("Scalar", [("scalar", cast_real(nm("rhs")))])],
                        )
                    )
                ],
            )
        )
    for t2 in [SCALAR, *graded_specs(n)]:
        rspec, out_exprs = product_result(t1, t2, gn_op, n, full_name)
        cases.append(
            ast.match_case(
                pattern=_match_class(nm(t2.name)),
                body=result_block_nodes(
                    rspec, out_exprs, rename_map(t1.blades, t2.blades)
                ),
            )
        )
    cases.append(
        ast.match_case(
            pattern=ast.MatchAs(pattern=None, name=None),
            body=[
                ann_assign(
                    "left", nm(full_name), call("_coerce", [nm("self"), nm(full_name)])
                ),
                ann_assign(
                    "right", nm(full_name), call("_coerce", [nm("rhs"), nm(full_name)])
                ),
                ret(cast_self(fallback_node)),
            ],
        )
    )
    return fn(
        method,
        [ast.Match(subject=nm("rhs"), cases=cases)],
        params=[arg("self"), arg("rhs")],
        returns=dot("typing", "Self"),
    )


PLANE_DOC = (
    "The unit bivector (2-blade) this rotor rotates in.\n"
    "\n"
    "        A rotor is ``cos(t/2) - sin(t/2) * B`` for a unit bivector B --\n"
    "        the oriented plane of rotation.  This returns B, the normalized\n"
    "        bivector part.  In 2D that 2-blade is also the pseudoscalar; in 3D\n"
    "        it is a bivector plane, not the trivector.  Undefined for the\n"
    "        identity rotor (no rotation)."
)


def generate_graded_type(spec: TypeSpec, n: int, full_name: str) -> list[ast.stmt]:
    """A graded subtype (Vector/Bivector/Trivector/Rotor), as nodes (level C)."""
    blades = list(spec.blades)
    fields = [field_name(b) for b in blades]
    has_scalar = () in blades
    unary_rename = rename_map(spec.blades, ())
    numlike = [nm("int"), nm("float"), dot("sympy", "Expr")]
    SELF = dot("typing", "Self")

    def unary_body(thunk) -> ast.stmt:
        rspec, out_exprs = unary_result(spec, thunk, n, full_name)
        return unary_nodes(rspec, out_exprs, unary_rename)

    rev_pairs = []
    for b in blades:
        f = field_name(b)
        sign = (-1) ** ((len(b) * (len(b) - 1)) // 2)
        rev_pairs.append(
            (
                f,
                dot("self", f)
                if sign == 1
                else cast_real(ast.UnaryOp(ast.USub(), dot("self", f))),
            )
        )

    grades_body: list[ast.stmt] = [
        ann_assign("present", subscript(nm("list"), nm("int")), ast.List([], _LOAD))
    ]
    for g in sorted({len(b) for b in blades}):
        grades_body.append(
            ast.If(
                bool_or(
                    [ne_zero(dot("self", field_name(b))) for b in blades if len(b) == g]
                ),
                [ast.Expr(call(dot("present", "append"), [lit(g)]))],
                [],
            )
        )
    grades_body.append(ret(nm("present")))

    rvp_body: list[ast.stmt] = [
        ast.If(
            ast.Compare(nm("r"), [ast.Eq()], [lit(r)]),
            [unary_body(lambda a, r=r: a.r_vector_part(r))],
            [],
        )
        for r in range(n + 1)
    ]
    rvp_body.append(
        ret(cast_self(construct("Scalar", [("scalar", cast_real(lit(0)))])))
    )

    body = [
        class_doc(graded_docstring(spec)),
        dimension_decl(n),
        *field_decls(blades),
        from_blade_dict_method(blades),
        to_blade_dict_method(blades),
        eq_method(),
        # scalar-aware __mul__ / __rmul__ (the ABC versions would drop the scalar
        # for a type with no scalar field, so they are overridden here)
        fn(
            "__mul__",
            [
                ast.If(
                    isinstance_(nm("rhs"), numlike),
                    [
                        scaled_nodes(
                            spec.name,
                            fields,
                            lambda f: ast.BinOp(dot("self", f), ast.Mult(), nm("rhs")),
                        )
                    ],
                    [],
                ),
                ret(call(dot("self", "_geometric_product"), [nm("rhs")])),
            ],
            params=[arg("self"), arg("rhs")],
            returns=SELF,
        ),
        fn(
            "__rmul__",
            [
                ast.If(
                    isinstance_(nm("lhs"), numlike),
                    [
                        scaled_nodes(
                            spec.name,
                            fields,
                            lambda f: ast.BinOp(nm("lhs"), ast.Mult(), dot("self", f)),
                        )
                    ],
                    [],
                ),
                ret(call(dot("self", "_geometric_product"), [nm("lhs")])),
            ],
            params=[arg("self"), arg("lhs")],
            returns=SELF,
        ),
        # the three bilinear products + the two linear ops, each a match on rhs type
        dispatch_nodes(
            spec,
            "_geometric_product",
            lambda a, b: a * b,
            n,
            full_name,
            ast.BinOp(nm("left"), ast.Mult(), nm("right")),
        ),
        dispatch_nodes(
            spec,
            "outer_product",
            lambda a, b: a.outer_product(b),
            n,
            full_name,
            call(dot("left", "outer_product"), [nm("right")]),
        ),
        dispatch_nodes(
            spec,
            "inner_product",
            lambda a, b: a.inner_product(b),
            n,
            full_name,
            call(dot("left", "inner_product"), [nm("right")]),
        ),
        dispatch_nodes(
            spec,
            "__add__",
            lambda a, b: a + b,
            n,
            full_name,
            ast.BinOp(nm("left"), ast.Add(), nm("right")),
            number_case=True,
        ),
        dispatch_nodes(
            spec,
            "__sub__",
            lambda a, b: a - b,
            n,
            full_name,
            ast.BinOp(nm("left"), ast.Sub(), nm("right")),
            number_case=True,
        ),
        fn(
            "__radd__",
            [ret(call(dot("self", "__add__"), [nm("lhs")]))],
            params=[arg("self"), arg("lhs")],
            returns=SELF,
        ),
        fn(
            "__rsub__",
            [
                ret(
                    cast_self(
                        call(
                            dot(ast.UnaryOp(ast.USub(), nm("self")), "__add__"),
                            [nm("lhs")],
                        )
                    )
                )
            ],
            params=[arg("self"), arg("lhs")],
            returns=SELF,
        ),
        fn(
            "__neg__",
            [
                scaled_nodes(
                    spec.name, fields, lambda f: ast.UnaryOp(ast.USub(), dot("self", f))
                )
            ],
            returns=SELF,
        ),
        fn("reverse", [ret(cast_self(construct(spec.name, rev_pairs)))], returns=SELF),
        fn(
            "scalar_part",
            [ret(dot("self", "scalar") if has_scalar else cast_real(lit(0)))],
            returns=dot("numbers", "Real"),
        ),
        fn("grades", grades_body, returns=subscript(nm("list"), nm("int"))),
        fn(
            "is_close",
            [
                ast.If(
                    not_(isinstance_(nm("other"), nm(spec.name))),
                    [ret(super_call("is_close", [nm("other")]))],
                    [],
                ),
                ret(call("bool", [bool_and([isclose_call(f) for f in fields])])),
            ],
            params=[arg("self"), arg("other")],
            returns=nm("bool"),
        ),
        fn(
            "__iter__",
            [
                ast.If(
                    ne_zero(dot("self", field_name(b))),
                    [
                        ast.Expr(
                            ast.Yield(
                                construct(
                                    spec.name,
                                    [(field_name(b), dot("self", field_name(b)))],
                                )
                            )
                        )
                    ],
                    [],
                )
                for b in blades
            ],
        ),
        fn("even_part", [unary_body(lambda a: a.even_part())], returns=SELF),
        fn("odd_part", [unary_body(lambda a: a.odd_part())], returns=SELF),
        fn(
            "r_vector_part",
            rvp_body,
            params=[arg("self"), arg("r", nm("int"))],
            returns=SELF,
        ),
        fn(
            "dual",
            [
                ast.If(
                    bool_or(
                        [
                            ast.Compare(nm("n"), [ast.Is()], [lit(None)]),
                            ast.Compare(nm("n"), [ast.Eq()], [lit(n)]),
                        ]
                    ),
                    [unary_body(lambda a: a.dual(n))],
                    [],
                ),
                ret(
                    cast_self(
                        call(
                            dot(call("_coerce", [nm("self"), nm(full_name)]), "dual"),
                            [nm("n")],
                        )
                    )
                ),
            ],
            params=[arg("self"), arg("n", opt_int())],
            defaults=[lit(None)],
            returns=SELF,
        ),
    ]
    if spec.name.startswith("Rotor"):
        body.append(
            fn(
                "plane_of_rotation",
                [
                    class_doc(PLANE_DOC),
                    ret(
                        call(
                            dot(
                                call(dot("self", "r_vector_part"), [lit(2)]),
                                "normalize",
                            ),
                            [],
                        )
                    ),
                ],
                returns=nm("AbstractMultiVector"),
            )
        )
    return [cls(spec.name, body, decorators=[dataclass_decorator(eq=False)])]


def generate_constants(n: int, name: str) -> list[ast.stmt]:
    """Module-level basis constants for one algebra, hand-built as nodes (level C)."""
    nonempty = [b for b in blades_for_dim(n) if b != ()]
    nodes: list[ast.stmt] = [
        ann_assign("zero", nm(name), call(dot(name, "from_scalar"), [lit(0)])),
        ann_assign("one", nm(name), call(dot(name, "from_scalar"), [lit(1)])),
    ]
    for b in nonempty:
        nodes.append(
            ann_assign(
                field_name(b),
                nm(name),
                call(
                    dot(name, "from_blade_dict"),
                    [ast.Dict(keys=[lit(b)], values=[lit(1)])],
                ),
            )
        )
    exported = [name, "Scalar", *(s.name for s in graded_specs(n)), "zero", "one"]
    exported += [field_name(b) for b in nonempty]
    nodes.append(
        assign("__all__", ast.List(elts=[lit(s) for s in exported], ctx=_LOAD))
    )
    return nodes


def header(name: str, n: int) -> str:
    return f"""# Copyright (c) 2025-2026 William Emerison Six
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

# AUTO-GENERATED by tools/gen_specialized.py -- do not edit by hand.
# Regenerate with:  python tools/gen_specialized.py
#
# {name}: a specialized, performant representation of 𝒢{_sub(n)} -- a named-field
# dataclass whose geometric product is the closed form derived from the general
# Gn symbolic product.

from __future__ import annotations

import dataclasses
import numbers
import typing
from collections.abc import Generator

import numpy as np
import sympy

from geometricalgebra.base import AbstractMultiVector, BladeCoef
from geometricalgebra.gn import Gn
from geometricalgebra.scalar import Scalar


def _coerce(x, cls):
    \"\"\"Coerce a scalar or multivector to ``cls`` (the full type).\"\"\"
    if isinstance(x, AbstractMultiVector):
        return cls.from_blade_dict(x.to_blade_dict())
    if isinstance(x, sympy.Expr):
        return cls.from_sympy_expr(x)
    return cls.from_scalar(x)
"""


SCALAR_HEADER = """# Copyright (c) 2025-2026 William Emerison Six
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

# AUTO-GENERATED by tools/gen_specialized.py -- do not edit by hand.
# Regenerate with:  python tools/gen_specialized.py
#
# Scalar: the shared grade-0 type used by the graded subtypes of every 𝒢ₙ.

from __future__ import annotations

import dataclasses
import numbers
import typing

import numpy as np
import sympy

from geometricalgebra.base import AbstractMultiVector, BladeCoef
from geometricalgebra.gn import Gn
"""


ALGEBRAS = [(1, "G1", "g1.py"), (2, "G2", "g2.py"), (3, "G3", "g3.py")]


def ruff_format(paths: list[str]) -> None:
    """Format the freshly written files with ruff so the committed output is
    already formatted in one step (no separate format.sh pass needed, matching
    its quote style / line wrapping).  Best-effort: if ruff isn't installed, warn
    and leave the files raw rather than failing the generation.
    """
    try:
        # Best-effort lint-fix. Its stdout is suppressed: ``ruff check`` reports
        # not-yet-fixable diagnostics (e.g. E501 long lines) that the following
        # ``ruff format`` pass then resolves by wrapping -- printing them here is
        # misleading noise. The real lint gate is format.sh / CI.
        subprocess.run(
            ["ruff", "check", "--fix", "--quiet", *paths],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["ruff", "format", "--quiet", "--line-length=88", *paths], check=True
        )
    except FileNotFoundError:
        sys.stdout.write("warning: ruff not found; generated files left unformatted\n")
        return
    sys.stdout.write("formatted with ruff\n")


def main() -> None:
    written: list[str] = []
    # Each module's body is assembled as a list of `ast` statement nodes (the
    # per-construct generators return source snippets that we parse into nodes via
    # `parse_stmts`), then rendered with `ast.unparse` (module_source).  The file
    # header -- copyright comment + imports -- stays raw text (comments can't live
    # in an AST) and is prepended.

    # the shared Scalar module first (the graded types import it)
    scalar_nodes = generate_scalar() + parse_stmts('__all__ = ["Scalar"]')
    scalar_source = SCALAR_HEADER + "\n\n" + module_source(scalar_nodes) + "\n"
    with open(out_path("scalar.py"), "w") as f:
        f.write(scalar_source)
    written.append(out_path("scalar.py"))
    sys.stdout.write(f"wrote {os.path.normpath(out_path('scalar.py'))}\n")

    for n, name, filename in ALGEBRAS:
        nodes = generate_class(n, name)
        for spec in graded_specs(n):
            nodes += generate_graded_type(spec, n, name)
        nodes += generate_constants(n, name)
        source = header(name, n) + "\n\n" + module_source(nodes) + "\n"
        with open(out_path(filename), "w") as f:
            f.write(source)
        written.append(out_path(filename))
        sys.stdout.write(f"wrote {os.path.normpath(out_path(filename))}\n")
    ruff_format(written)


if __name__ == "__main__":
    main()
