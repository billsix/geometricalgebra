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
(``from gacalc.g2 import G2``).  Re-run this script by hand when the
algebra changes:

    python tools/gen_specialized.py
"""

from __future__ import annotations

import ast
import inspect
import os
import subprocess
import sys
from collections import namedtuple
from itertools import chain, combinations

import sympy

# allow running from the repo root without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# the node-builder DSL lives in a sibling module (tools/ is on sys.path as the
# script's own directory); see tools/astbuild.py
from astbuild import (  # noqa: E402
    _LOAD,
    _STORE,
    SymbolToAttr,
    ann_assign,
    arg,
    assign,
    bool_and,
    bool_or,
    call,
    cast_coef,
    cast_operand,
    cast_self,
    cls,
    construct,
    dataclass_decorator,
    dot,
    fn,
    isinstance_,
    lit,
    module_source,
    ne_zero,
    nm,
    not_,
    opt_int,
    parse_expr,
    ret,
    return_construct,
    subscript,
)

from gacalc.base import AbstractMultiVector, BladeCoef  # noqa: E402
from gacalc.gn import Gn  # noqa: E402

# ==========================================================================
# sympy -> ast bridge
# ==========================================================================


def expr_to_ast(expr, rename: dict[str, tuple[str, str]]) -> ast.expr:
    """sympy expression -> AST expression with operand symbols as attribute access."""
    tree = parse_expr(sympy.sstr(expr))
    return ast.fix_missing_locations(SymbolToAttr(rename).visit(tree))


# ==========================================================================
# Geometric-algebra domain utilities
# ==========================================================================


def out_path(filename: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "src", "gacalc", filename)


def blades_for_dim(n: int) -> list[tuple[int, ...]]:
    """All 2**n basis blades of 𝒢ₙ in canonical (grade, then index) order."""
    idx = list(range(1, n + 1))
    powerset = chain.from_iterable(combinations(idx, r) for r in range(n + 1))
    return sorted(powerset, key=lambda b: (len(b), b))


def blade_label(blade: tuple[int, ...]) -> str:
    """The human/blade label: () -> 'scalar', (1,) -> 'e_1', (1, 2) -> 'e_12'.

    Used for docstrings and the internal cse symbol names (``a_e_1``/``b_e_1``).
    The dataclass *field* that stores a blade's coefficient is ``field_name`` (a
    ``coeff_``-prefixed form), kept distinct so the basis-blade names ``e_1`` ...
    stay free to denote the basis-vector constants on each class.
    """
    if blade == ():
        return "scalar"
    return "e_" + "".join(str(i) for i in blade)


def field_name(blade: tuple[int, ...]) -> str:
    """The dataclass field storing a blade's coefficient:
    () -> 'coeff_scalar', (1,) -> 'coeff_e_1', (1, 2) -> 'coeff_e_12'.
    """
    return "coeff_" + blade_label(blade)


def blade_of_label(label: str) -> tuple[int, ...]:
    """Inverse of ``blade_label``: 'scalar'->(), 'e_1'->(1,), 'e_12'->(1, 2).

    Assumes single-digit basis indices (n < 10), which the naming already
    requires (``e_12`` is otherwise ambiguous).
    """
    if label == "scalar":
        return ()
    return tuple(int(c) for c in label[2:])


def term_grade_key(term) -> tuple[int, tuple[int, ...], int, tuple[int, ...]]:
    """Grade-ordering key for one additive term ``self.<L> * rhs.<R>``.

    Orders by ``(grade(L), indices(L), grade(R), indices(R))`` so the generated
    sums read scalar -> vector -> bivector -> ... (instead of sympy's roughly
    lexicographic-by-name order, where e.g. ``e_12`` sorts before ``e_2``).  The
    term is a product of one ``a_<label>`` (self) and one ``b_<label>`` (rhs)
    symbol.  A term carrying neither (e.g. a future ``cse`` temporary -- the
    products produce none today) sorts last.
    """
    sentinel = (99, ())
    left = right = None
    for sym in term.free_symbols:
        if sym.name.startswith("a_"):
            blade = blade_of_label(sym.name[2:])
            left = (len(blade), blade)
        elif sym.name.startswith("b_"):
            blade = blade_of_label(sym.name[2:])
            right = (len(blade), blade)
    left = left if left is not None else sentinel
    right = right if right is not None else sentinel
    return (left[0], left[1], right[0], right[1])


# ==========================================================================
# Docstrings -- text + builders for class and method docstrings
# ==========================================================================


def _sub(k: int) -> str:
    return "".join("₀₁₂₃₄₅₆₇₈₉"[int(d)] for d in str(k))


def _sup(k: int) -> str:
    return "".join("⁰¹²³⁴⁵⁶⁷⁸⁹"[int(d)] for d in str(k))


def generic_docstring(n: int) -> str:
    """Standard class docstring for any dimension (fallback for unknown n)."""
    bl: list[tuple[int, ...]] = blades_for_dim(n)
    grades = "\n".join(
        f"        {', '.join(blade_label(b) for b in bl if len(b) == g)}  (grade {g})"
        for g in range(n + 1)
    )
    return (
        f"An element (multivector) of 𝒢{_sub(n)}, the geometric algebra of\n"
        f"    {n}-dimensional Euclidean space ℝ{_sup(n)} (Hestenes' notation).\n"
        "\n"
        f"    𝒢{_sub(n)} has 2{_sup(n)} = {2**n} basis blades:\n"
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
        "    𝒢₁ has 2¹ = 2 basis blades:\n"
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
        "    𝒢₂ has 2² = 4 basis blades:\n"
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
        "    𝒢₃ has 2³ = 8 basis blades:\n"
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


def graded_docstring(spec: TypeSpec) -> str:
    grade_words = {0: "scalar", 1: "vector", 2: "bivector", 3: "trivector"}
    labels = ", ".join(blade_label(b) for b in spec.blades)
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
        f"    of 𝒢{_sub(spec.dim)}.  Spanning the basis blades: {labels}.\n\n"
        "    A graded subtype: products dispatch by operand type and return the\n"
        "    grade-correct type (e.g. vector*vector -> the even/Rotor type).  "
        "Results\n    that span grades no graded type covers widen to "
        f"{full_name_for(spec.dim)}.\n    AUTO-GENERATED by tools/gen_specialized.py."
    )


def full_name_for(dim: int) -> str:
    return f"G{dim}"


SCALAR_DOC = (
    "The grade-0 type -- a scalar, shared across every 𝒢ₙ.\n"
    "\n"
    "    ``Scalar * x`` scales ``x`` and returns x's type; pure-scalar product\n"
    "    results (e.g. Bivector2 * Bivector2) land here.  AUTO-GENERATED by\n"
    "    tools/gen_specialized.py."
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


def method_doc_stmts(method_name, indent="        ") -> list[ast.stmt]:
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


def class_doc_stmt(text: str) -> ast.Expr:
    """A class docstring statement -- ``text`` used verbatim."""
    return ast.Expr(value=lit(text))


# ==========================================================================
# Type registry + grade-resolution + symbolic op results
# ==========================================================================

TypeSpec = namedtuple("TypeSpec", "name blades dim kind")

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
        b: sympy.Symbol("a_" + blade_label(b)) for b in t1.blades
    }
    b_syms: dict[tuple[int, ...], sympy.Symbol] = {
        b: sympy.Symbol("b_" + blade_label(b)) for b in t2.blades
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
        b: sympy.Symbol("a_" + blade_label(b)) for b in t1.blades
    }
    result_mv: Gn = gn_fn(Gn.from_blade_dict(a_syms))
    rd: BladeCoef = result_mv.to_blade_dict()
    support: list[tuple[int, ...]] = [
        b for b in blades_for_dim(n) if sympy.sympify(rd.get(b, 0)) != 0
    ]
    rspec: TypeSpec = resolve(support, n, full_name)
    out_exprs: list[sympy.Expr] = [sympy.sympify(rd.get(b, 0)) for b in rspec.blades]
    return rspec, out_exprs


def _is_neg_term(term, rename) -> bool:
    return ast.unparse(expr_to_ast(term, rename)).lstrip().startswith("-")


def summed_value(expr, rename) -> ast.expr:
    """A constructor field value: grade-ordered sum of terms (≈ format_assignment).

    Constants are cast to ``Coef``; sums fold left-assoc as ``BinOp`` in
    ``term_grade_key`` order, subtracting negative terms -- so the node tree matches
    the string baseline's operand order.
    """
    expr = sympy.sympify(expr)
    if not expr.free_symbols:
        return cast_coef(expr_to_ast(expr, rename))
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
        return cast_coef(expr_to_ast(e, rename))
    return summed_value(e, rename)


def unary_value(expr, rename) -> ast.expr:
    """Constructor field value for unary results (mirrors unary_return)."""
    e = sympy.sympify(expr)
    return expr_to_ast(e, rename) if e.is_Symbol else cast_coef(expr_to_ast(e, rename))


# ==========================================================================
# Shared class / method builders (used by every generated class)
# ==========================================================================


def rename_map(blades_self, blades_rhs, rhs_name="rhs") -> dict[str, tuple[str, str]]:
    """Operand-symbol rename map for ``expr_to_ast`` (a_<f>->self, b_<f>-><rhs>)."""
    r: dict[str, tuple[str, str]] = {}
    for b in blades_self:
        r["a_" + blade_label(b)] = ("self", field_name(b))
    for b in blades_rhs:
        r["b_" + blade_label(b)] = (rhs_name, field_name(b))
    return r


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


def dimension_decl(n) -> ast.stmt:
    """``DIMENSION: typing.ClassVar[int] = <n>``."""
    return ann_assign(
        "DIMENSION", subscript(dot("typing", "ClassVar"), nm("int")), lit(n)
    )


def field_decls(blades) -> list[ast.stmt]:
    """``<field>: Coef = cast(Coef, 0)`` per blade."""
    return [ann_assign(field_name(b), nm("Coef"), cast_coef(lit(0))) for b in blades]


def basis_classvar_decls(name: str, blades) -> list[ast.stmt]:
    """``e_1: typing.ClassVar[Name]`` ... (annotation only) per nonempty blade.

    Declares the basis-vector class constants so a type checker sees them; the
    *values* are assigned after the class body (a class can't reference itself
    while it is being defined -- see ``basis_constant_assignments``).  As a
    ClassVar these are excluded from the dataclass fields / ``__slots__``.
    """
    return [
        ann_assign(blade_label(b), subscript(dot("typing", "ClassVar"), nm(name)))
        for b in blades
        if b != ()
    ]


def basis_constant_assignments(name: str, blades) -> list[ast.stmt]:
    """``Name.e_1 = Name.from_blade_dict({(1,): 1})`` ... per nonempty blade.

    The basis-vector constants of the class's own type, assigned *after* the
    class so it can reference itself.  Because ``e_1`` is not a (``coeff_``) field,
    both ``Name.e_1`` and ``instance.e_1`` resolve to this one constant.
    """
    return [
        ast.Assign(
            targets=[ast.Attribute(value=nm(name), attr=blade_label(b), ctx=_STORE)],
            value=call(
                dot(name, "from_blade_dict"),
                [ast.Dict(keys=[lit(b)], values=[lit(1)])],
            ),
        )
        for b in blades
        if b != ()
    ]


def from_blade_dict_method(blades) -> ast.FunctionDef:
    """The ``from_blade_dict`` classmethod over the given blades."""
    keywords = [
        ast.keyword(
            arg=field_name(b),
            value=cast_coef(call(dot("d", "get"), [lit(b), lit(0)])),
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


def to_blade_dict_method(blades) -> ast.FunctionDef:
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


def class_header_stmts(doc, n, blades) -> list[ast.stmt]:
    """The common class prefix: docstring, DIMENSION, fields, interchange, __eq__."""
    return [
        class_doc_stmt(doc),
        dimension_decl(n),
        *field_decls(blades),
        from_blade_dict_method(blades),
        to_blade_dict_method(blades),
        eq_method(),
    ]


def is_close_method(name_, fields) -> ast.FunctionDef:
    """``is_close``: defer to the ABC for a foreign type, else np.isclose per field."""
    return fn(
        "is_close",
        [
            ast.If(
                not_(isinstance_(nm("other"), nm(name_))),
                [ret(super_call("is_close", [nm("other")]))],
                [],
            ),
            ret(call("bool", [bool_and([isclose_call(f) for f in fields])])),
        ],
        params=[arg("self"), arg("other")],
        returns=nm("bool"),
    )


def iter_method(blades) -> ast.FunctionDef:
    """``__iter__``: yield the component VALUES, one per field, in blade order.

    A value (vector, rotor, full multivector, ...) reads as the numbers it holds,
    so ``list(v)`` / ``tuple(v)`` / ``np.array([list(v), ...])`` give the
    coefficients -- not one single-blade multivector per term.  All fields are
    yielded (dense, fixed length), so e.g. ``list(Vector2(3, 0)) == [3, 0]``.
    """
    return fn(
        "__iter__",
        [
            *method_doc_stmts("__iter__"),
            *[ast.Expr(ast.Yield(dot("self", field_name(b)))) for b in blades],
        ],
    )


def grades_method(grade_groups) -> ast.FunctionDef:
    """``grades``: append each grade whose fields are not all zero.

    ``grade_groups`` is an ordered list of ``(grade, [field names])``.
    """
    body: list[ast.stmt] = [
        ann_assign("present", subscript(nm("list"), nm("int")), ast.List([], _LOAD))
    ]
    for g, flds in grade_groups:
        body.append(
            ast.If(
                bool_or([ne_zero(dot("self", f)) for f in flds]),
                [ast.Expr(call(dot("present", "append"), [lit(g)]))],
                [],
            )
        )
    body.append(ret(nm("present")))
    return fn("grades", body, returns=subscript(nm("list"), nm("int")))


def result_stmts(name_, pairs) -> list[ast.stmt]:
    """``result: Name = Name(...); return cast(Self, result)`` as nodes."""
    return [
        ann_assign("result", nm(name_), construct(name_, pairs)),
        ret(cast_self(nm("result"))),
    ]


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


def scaled_stmt(name_, fields, value_fn) -> ast.stmt:
    """``return cast(Self, Name(field=cast(Real, value_fn(field)), ...))``."""
    return ret(
        cast_self(construct(name_, [(f, cast_coef(value_fn(f))) for f in fields]))
    )


def result_block_stmts(rspec, out_exprs, rename, cast=cast_self) -> list[ast.stmt]:
    """cse temps + ``return cast(<T>, RType(...))`` (= result_block, as nodes).

    ``cast`` defaults to ``cast_self``; the rotor sandwich passes ``cast_operand``
    so the return is typed as the operand (``_OperandT``), not ``Self``.
    """
    replacements, reduced = sympy.cse(out_exprs)
    stmts: list[ast.stmt] = [
        assign(str(t), expr_to_ast(e, rename)) for t, e in replacements
    ]
    pairs = [
        (field_name(b), result_value(e, rename)) for b, e in zip(rspec.blades, reduced)
    ]
    stmts.append(ret(cast(construct(rspec.name, pairs))))
    return stmts


def unary_stmt(rspec, out_exprs, rename) -> ast.stmt:
    """``return cast(Self, RType(...))`` (= unary_return, as nodes)."""
    pairs = [
        (field_name(b), unary_value(e, rename)) for b, e in zip(rspec.blades, out_exprs)
    ]
    return ret(cast_self(construct(rspec.name, pairs)))


def _match_class(cls_node) -> ast.MatchClass:
    return ast.MatchClass(cls=cls_node, patterns=[], kwd_attrs=[], kwd_patterns=[])


def dispatch_method(
    t1,
    method,
    gn_op,
    n,
    full_name,
    fallback_node,
    number_case=False,
    param_name="rhs",
    return_type=None,
    cast=cast_self,
    param_annotation=None,
) -> ast.FunctionDef:
    """A method that ``match``es on the operand type (the grade product/sum table).

    Defaults emit ``def <method>(self, rhs) -> typing.Self`` casting each case to
    ``Self`` (the products).  The rotor sandwich overrides ``param_name='x'``,
    ``return_type=_OperandT``, ``cast=cast_operand`` so it is a Liskov-compatible
    override of ``AbstractMultiVector.sandwich(self, x: _OperandT) -> _OperandT``
    and is typed as the operand, not ``Self``.
    """
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
                            [
                                construct(
                                    "Scalar",
                                    [(field_name(()), cast_coef(nm(param_name)))],
                                )
                            ],
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
                body=result_block_stmts(
                    rspec, out_exprs, rename_map(t1.blades, t2.blades, param_name), cast
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
                    "right",
                    nm(full_name),
                    call("_coerce", [nm(param_name), nm(full_name)]),
                ),
                ret(cast(fallback_node)),
            ],
        )
    )
    return fn(
        method,
        [ast.Match(subject=nm(param_name), cases=cases)],
        params=[arg("self"), arg(param_name, param_annotation)],
        returns=return_type if return_type is not None else dot("typing", "Self"),
    )


# ==========================================================================
# The four generators (one per emitted construct)
# ==========================================================================


def generate_scalar() -> list[ast.stmt]:
    """The shared grade-0 ``Scalar`` type, hand-built as `ast` nodes (level C)."""
    selfsc = dot("self", field_name(()))

    def s(value):  # cast(typing.Self, Scalar(coeff_scalar=value))
        return cast_self(construct("Scalar", [(field_name(()), value)]))

    def sr(value):  # cast(typing.Self, Scalar(coeff_scalar=cast(Coef, value)))
        return s(cast_coef(value))

    def mul(a, b):
        return ast.BinOp(left=a, op=ast.Mult(), right=b)

    SELF = dot("typing", "Self")
    COEF = nm("Coef")
    numlike = [nm("int"), nm("float"), dot("sympy", "Expr")]

    body = [
        class_doc_stmt(SCALAR_DOC),
        ann_assign(field_name(()), COEF, cast_coef(lit(0))),
        fn(
            "from_blade_dict",
            [
                assign("d", call("dict", [nm("blade_coef")])),
                ret(
                    ast.Call(
                        func=nm("cls"),
                        args=[],
                        keywords=[
                            ast.keyword(
                                arg=field_name(()),
                                value=cast_coef(
                                    call(dot("d", "get"), [lit(()), lit(0)])
                                ),
                            )
                        ],
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
                    [ret(sr(mul(selfsc, dot("rhs", field_name(())))))],
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
                    [ret(s(ast.BinOp(selfsc, ast.Add(), dot("rhs", field_name(())))))],
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
        fn("scalar_part", [ret(selfsc)], returns=COEF),
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
                                    call("float", [dot("other", field_name(()))]),
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
                    [
                        ast.Expr(
                            ast.Yield(construct("Scalar", [(field_name(()), selfsc)]))
                        )
                    ],
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


def generate_class(n: int, name: str) -> list[ast.stmt]:
    """The full all-blades G_n class, hand-built as `ast` nodes (level C)."""
    blades = blades_for_dim(n)
    fields = [field_name(b) for b in blades]
    rename = rename_map(blades, blades)
    a_mv = Gn.from_blade_dict({b: sympy.Symbol("a_" + blade_label(b)) for b in blades})
    b_mv = Gn.from_blade_dict({b: sympy.Symbol("b_" + blade_label(b)) for b in blades})
    by_grade = {g: [b for b in blades if len(b) == g] for g in range(n + 1)}
    SELF = dot("typing", "Self")

    def bilinear(method, cross_node, result_mv):
        rd = result_mv.to_blade_dict()
        replacements, reduced = sympy.cse([sympy.sympify(rd.get(b, 0)) for b in blades])
        body = method_doc_stmts(method) + [
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
        body += result_stmts(name, pairs)
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
                *result_stmts(
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

    rvp_cases = [
        ast.match_case(
            pattern=ast.MatchValue(lit(g)),
            body=result_stmts(
                name, [(field_name(b), dot("self", field_name(b))) for b in by_grade[g]]
            ),
        )
        for g in range(n + 1)
    ]
    rvp_cases.append(
        ast.match_case(
            pattern=ast.MatchAs(pattern=None, name=None), body=result_stmts(name, [])
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
                else cast_coef(ast.UnaryOp(ast.USub(), dot("self", f))),
            )
        )

    def grade_copy(parity):
        return [
            (field_name(b), dot("self", field_name(b)))
            for b in blades
            if len(b) % 2 == parity
        ]

    body = [
        *class_header_stmts(docstring_for(n), n, blades),
        *basis_classvar_decls(name, blades),
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
            result_stmts(
                name,
                [
                    (f, cast_coef(ast.UnaryOp(ast.USub(), dot("self", f))))
                    for f in fields
                ],
            ),
            returns=SELF,
        ),
        fn(
            "scalar_part",
            method_doc_stmts("scalar_part") + [ret(dot("self", field_name(())))],
            returns=nm("Coef"),
        ),
        grades_method(
            [(g, [field_name(b) for b in by_grade[g]]) for g in range(n + 1)]
        ),
        fn(
            "r_vector_part",
            method_doc_stmts("r_vector_part")
            + [ast.Match(subject=nm("r"), cases=rvp_cases)],
            params=[arg("self"), arg("r", nm("int"))],
            returns=SELF,
        ),
        fn(
            "reverse",
            method_doc_stmts("reverse") + result_stmts(name, rev_pairs),
            returns=SELF,
        ),
        fn(
            "even_part",
            method_doc_stmts("even_part") + result_stmts(name, grade_copy(0)),
            returns=SELF,
        ),
        fn(
            "odd_part",
            method_doc_stmts("odd_part") + result_stmts(name, grade_copy(1)),
            returns=SELF,
        ),
        is_close_method(name, fields),
        iter_method(blades),
        fn(
            "dual",
            method_doc_stmts("dual") + [ret(super_call("dual", [dim_or_n("self")]))],
            params=[arg("self"), arg("n", opt_int())],
            defaults=[lit(None)],
            returns=SELF,
        ),
        fn(
            "unit_pseudoscalar",
            method_doc_stmts("unit_pseudoscalar")
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
    return [
        cls(name, body, decorators=[dataclass_decorator(eq=False, slots=True)]),
        *basis_constant_assignments(name, blades),
    ]


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
        return unary_stmt(rspec, out_exprs, unary_rename)

    rev_pairs = []
    for b in blades:
        f = field_name(b)
        sign = (-1) ** ((len(b) * (len(b) - 1)) // 2)
        rev_pairs.append(
            (
                f,
                dot("self", f)
                if sign == 1
                else cast_coef(ast.UnaryOp(ast.USub(), dot("self", f))),
            )
        )

    rvp_body: list[ast.stmt] = [
        ast.If(
            ast.Compare(nm("r"), [ast.Eq()], [lit(r)]),
            [unary_body(lambda a, r=r: a.r_vector_part(r))],
            [],
        )
        for r in range(n + 1)
    ]
    rvp_body.append(return_construct("Scalar", [(field_name(()), cast_coef(lit(0)))]))

    body = [
        *class_header_stmts(graded_docstring(spec), n, blades),
        *basis_classvar_decls(spec.name, blades),
        # scalar-aware __mul__ / __rmul__ (the ABC versions would drop the scalar
        # for a type with no scalar field, so they are overridden here)
        fn(
            "__mul__",
            [
                ast.If(
                    isinstance_(nm("rhs"), numlike),
                    [
                        scaled_stmt(
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
                        scaled_stmt(
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
        dispatch_method(
            spec,
            "_geometric_product",
            lambda a, b: a * b,
            n,
            full_name,
            ast.BinOp(nm("left"), ast.Mult(), nm("right")),
        ),
        dispatch_method(
            spec,
            "outer_product",
            lambda a, b: a.outer_product(b),
            n,
            full_name,
            call(dot("left", "outer_product"), [nm("right")]),
        ),
        dispatch_method(
            spec,
            "inner_product",
            lambda a, b: a.inner_product(b),
            n,
            full_name,
            call(dot("left", "inner_product"), [nm("right")]),
        ),
        dispatch_method(
            spec,
            "__add__",
            lambda a, b: a + b,
            n,
            full_name,
            ast.BinOp(nm("left"), ast.Add(), nm("right")),
            number_case=True,
        ),
        dispatch_method(
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
                scaled_stmt(
                    spec.name, fields, lambda f: ast.UnaryOp(ast.USub(), dot("self", f))
                )
            ],
            returns=SELF,
        ),
        fn("reverse", [return_construct(spec.name, rev_pairs)], returns=SELF),
        fn(
            "scalar_part",
            [ret(dot("self", field_name(())) if has_scalar else cast_coef(lit(0)))],
            returns=nm("Coef"),
        ),
        grades_method(
            [
                (g, [field_name(b) for b in blades if len(b) == g])
                for g in sorted({len(b) for b in blades})
            ]
        ),
        is_close_method(spec.name, fields),
        iter_method(blades),
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
                    class_doc_stmt(PLANE_DOC),
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
        # Versor conjugation  R x R^-1  -- the rotor sandwich, GRADE-PRESERVING:
        # the derived closed form's support is exactly x's grades (the would-be
        # higher grades cancel symbolically), so each operand returns its own
        # type (Vector->Vector, Bivector->Bivector, ...) with no projection.
        body.append(
            dispatch_method(
                spec,
                "sandwich",
                lambda r, x: r * x * r.inverse(),
                n,
                full_name,
                call(dot("left", "sandwich"), [nm("right")]),
                param_name="x",
                return_type=nm("_OperandT"),
                cast=cast_operand,
                param_annotation=nm("_OperandT"),
            )
        )
    return [
        cls(spec.name, body, decorators=[dataclass_decorator(eq=False)]),
        *basis_constant_assignments(spec.name, blades),
    ]


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
                blade_label(b),
                nm(name),
                call(
                    dot(name, "from_blade_dict"),
                    [ast.Dict(keys=[lit(b)], values=[lit(1)])],
                ),
            )
        )
    exported = [name, "Scalar", *(s.name for s in graded_specs(n)), "zero", "one"]
    exported += [blade_label(b) for b in nonempty]
    nodes.append(
        assign("__all__", ast.List(elts=[lit(s) for s in exported], ctx=_LOAD))
    )
    return nodes


# ==========================================================================
# File headers, constants, and the generation driver
# ==========================================================================


def header(name: str, n: int) -> str:
    # _OperandT (the sandwich operand TypeVar) is only used by the Rotor class,
    # which exists for n >= 2; importing it for G1 would be unused (F401).
    operand_import = ", _OperandT" if n >= 2 else ""
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
import typing
from collections.abc import Generator

import numpy as np
import sympy

from gacalc.base import AbstractMultiVector, BladeCoef, Coef{operand_import}
from gacalc.gn import Gn
from gacalc.scalar import Scalar


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
import typing

import numpy as np
import sympy

from gacalc.base import AbstractMultiVector, BladeCoef, Coef
from gacalc.gn import Gn
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
    # Each module's body is a list of `ast` statement nodes (the per-construct
    # generators build them directly), rendered to source with `ast.unparse`
    # (module_source).  The file header -- copyright comment + imports -- stays raw
    # text (comments can't live in an AST) and is prepended.

    # the shared Scalar module first (the graded types import it)
    scalar_nodes = generate_scalar() + [
        assign("__all__", ast.List(elts=[lit("Scalar")], ctx=_LOAD))
    ]
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
