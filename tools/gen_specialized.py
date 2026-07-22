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

Naming conventions (internal to this generator -- these abbreviations never
appear in the generated output or public API).

``_ann`` suffix -- an ``ast`` node used as a type *annotation* (the module is
built as AST, so a type like ``typing.Self`` is a node, not a string):

  - ``self_ann``   -> ``typing.Self``
  - ``mvb_ann``    -> ``MultiVectorBase``
  - ``coef_ann``   -> ``Coef``
  - ``param_ann``  -> a method parameter's annotation
  - ``radd_ann``   -> the ``__radd__`` return annotation

``_spec`` suffix -- a ``TypeSpec`` (see the "type system" section): the resolved
multivector type of an operand or a result:

  - ``self_spec`` / ``lhs_spec`` / ``rhs_spec`` / ``operand_spec``  -> operands
  - ``result_spec`` / ``num_spec`` / ``add_scalar_spec``           -> results

``mvb`` -- ``MultiVectorBase``, the abstract base class.

``rvp`` -- ``r_vector_part`` (the grade-r part, ⟨A⟩ᵣ):

  - ``rvp_cases``            -> the full class's ``match r:``
  - ``rvp_body``            -> the graded classes' ``if r == …:`` chain
  - ``rvp_overload_stub(s)`` -> its ``@overload`` signatures
  - ``rvp_spec``            -> a grade's resolved part type
"""

from __future__ import annotations

import ast
import inspect
import os
import subprocess
import sys
from collections.abc import Callable, Iterable, Sequence
from itertools import chain, combinations
from typing import NamedTuple

import sympy

# allow running from the repo root without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# the node-builder DSL lives in a sibling module (tools/ is on sys.path as the
# script's own directory); see tools/astbuild.py
from astbuild import (  # noqa: E402
    _LOAD,
    _STORE,
    SymbolToAttr,
    annotated_assign,
    argument,
    assign,
    attribute,
    bool_and,
    bool_or,
    call,
    cast_coef,
    cast_operand,
    cast_self,
    class_def,
    constant,
    construct,
    construct_type_of,
    construct_type_self,
    dataclass_decorator,
    function_def,
    inject_region_markers,
    isinstance_,
    module_source,
    name_ref,
    ne_zero,
    not_,
    opt_int,
    parse_expr,
    return_construct,
    return_stmt,
    subscript,
)

from gacalc.base import Blade, BladeCoef, MultiVectorBase  # noqa: E402
from gacalc.gn import Gn  # noqa: E402

# ==========================================================================
# sympy -> ast bridge
# ==========================================================================


def expr_to_ast(expr: sympy.Expr, rename: dict[str, tuple[str, str]]) -> ast.expr:
    """sympy expression -> AST expression with operand symbols as attribute access."""
    tree = parse_expr(sympy.sstr(expr))
    return ast.fix_missing_locations(SymbolToAttr(rename).visit(tree))


# ==========================================================================
# Geometric-algebra domain utilities
# ==========================================================================


def out_path(filename: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "src", "gacalc", filename)


def blades_for_dim(n: int) -> list[Blade]:
    """All 2**n basis blades of 𝒢ₙ in canonical (grade, then index) order."""
    idx = list(range(1, n + 1))
    powerset = chain.from_iterable(combinations(idx, r) for r in range(n + 1))
    return sorted(powerset, key=lambda b: (len(b), b))


def blade_label(blade: Blade) -> str:
    """The human/blade label: () -> 'scalar', (1,) -> 'e_1', (1, 2) -> 'e_12'.

    Used for docstrings and the internal cse symbol names (``a_e_1``/``b_e_1``).
    The dataclass *field* that stores a blade's coefficient is ``field_name`` (a
    ``coeff_``-prefixed form), kept distinct so the basis-blade names ``e_1`` ...
    stay free to denote the basis-vector constants on each class.
    """
    if blade == ():
        return "scalar"
    return "e_" + "".join(str(i) for i in blade)


def field_name(blade: Blade) -> str:
    """The dataclass field storing a blade's coefficient:
    () -> 'coeff_scalar', (1,) -> 'coeff_e_1', (1, 2) -> 'coeff_e_12'.
    """
    return "coeff_" + blade_label(blade)


def blade_of_label(label: str) -> Blade:
    """Inverse of ``blade_label``: 'scalar'->(), 'e_1'->(1,), 'e_12'->(1, 2).

    Assumes single-digit basis indices (n < 10), which the naming already
    requires (``e_12`` is otherwise ambiguous).
    """
    if label == "scalar":
        return ()
    return tuple(int(c) for c in label[2:])


def term_grade_key(
    term: sympy.Expr,
) -> tuple[int, Blade, int, Blade]:
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
        if not isinstance(sym, sympy.Symbol):
            continue
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


def _subscript(number: int) -> str:
    return "".join("₀₁₂₃₄₅₆₇₈₉"[int(d)] for d in str(number))


def _superscript(number: int) -> str:
    return "".join("⁰¹²³⁴⁵⁶⁷⁸⁹"[int(d)] for d in str(number))


def generic_docstring(n: int) -> str:
    """Standard class docstring for any dimension (fallback for unknown n)."""
    blades: list[Blade] = blades_for_dim(n)
    grades: str = "\n".join(
        f"        {', '.join(blade_label(b) for b in blades if len(b) == grade)}"
        f"  (grade {grade})"
        for grade in range(n + 1)
    )
    return (
        f"An element (multivector) of 𝒢{_subscript(n)}, the geometric algebra of\n"
        f"    {n}-dimensional Euclidean space ℝ{_superscript(n)} "
        f"(Hestenes' notation).\n"
        "\n"
        f"    𝒢{_subscript(n)} has 2{_superscript(n)} = {2**n} basis blades:\n"
        f"{grades}\n"
        "\n"
        f"    A specialized, performant representation of 𝒢{_subscript(n)}; "
        f"see Gn for the\n"
        f"    general 𝒢ₙ case.  Terminology: 𝒢{_subscript(n)} denotes "
        f"the *algebra*; an\n"
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
    grade_words: dict[int, str] = {
        0: "scalar",
        1: "vector",
        2: "bivector",
        3: "trivector",
    }
    labels: str = ", ".join(blade_label(b) for b in spec.blades)
    kind: str = (
        "the even subalgebra (rotor / spinor)"
        if spec.name.startswith("Rotor")
        else "the grade-%d (%s) part"
        % (len(spec.blades[0]), grade_words.get(len(spec.blades[0]), "k-vector"))
        if len({len(b) for b in spec.blades}) == 1
        else "a graded part"
    )
    return (
        f"An element of {kind}\n"
        f"    of 𝒢{_subscript(spec.dim)}.  Spanning the basis blades: {labels}.\n\n"
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


def method_doc_stmts(method_name: str, indent: str = "        ") -> list[ast.stmt]:
    """The base method's docstring as a leading ``Expr(Constant)``, or ``[]``.

    The Constant value reproduces what the string generator emitted (a leading
    newline + ``indent``-prefixed lines), so the parsed AST matches for parity.
    """
    member: object | None = getattr(MultiVectorBase, method_name, None)
    doc: str | None = inspect.getdoc(member) if member is not None else None
    if not doc:
        return []
    body: str = "\n".join(f"{indent}{line}".rstrip() for line in doc.splitlines())
    return [ast.Expr(value=constant(f"\n{body}\n{indent}"))]


def class_doc_stmt(text: str) -> ast.Expr:
    """A class docstring statement -- ``text`` used verbatim."""
    return ast.Expr(value=constant(text))


# ==========================================================================
# Type registry + grade-resolution + symbolic op results
# ==========================================================================


class TypeSpec(NamedTuple):
    """A generated value type's spec: its name, its basis blades (each a tuple of
    basis-vector indices), the algebra dimension, and its kind."""

    name: str
    blades: tuple[Blade, ...]
    dim: int
    kind: str


SCALAR = TypeSpec("Scalar", ((),), 0, "scalar")


def graded_specs(n: int) -> list[TypeSpec]:
    """The graded (grade-pure + even/Rotor) types of 𝒢ₙ, per the Phase 1 registry."""
    blades: list[Blade] = blades_for_dim(n)

    def blades_of_grade(grade: int) -> tuple[Blade, ...]:
        return tuple(b for b in blades if len(b) == grade)

    specs: list[TypeSpec] = [TypeSpec(f"Vector{n}", blades_of_grade(1), n, "graded")]
    if n >= 2:
        specs.append(TypeSpec(f"Bivector{n}", blades_of_grade(2), n, "graded"))
    if n >= 3:
        specs.append(TypeSpec(f"Trivector{n}", blades_of_grade(3), n, "graded"))
    if n >= 2:  # even subalgebra (Rotor); for n==1 the even part is just the scalar
        even: tuple[Blade, ...] = tuple(b for b in blades if len(b) % 2 == 0)
        specs.append(TypeSpec(f"Rotor{n}", even, n, "graded"))
    return specs


def full_spec(n: int, full_name: str) -> TypeSpec:
    return TypeSpec(full_name, tuple(blades_for_dim(n)), n, "full")


def registry_for_dim(n: int, full_name: str) -> list[TypeSpec]:
    """Scalar + graded types + the full G_n -- every type a result can resolve to."""
    return [SCALAR, *graded_specs(n), full_spec(n, full_name)]


def resolve(support: Sequence[Blade], n: int, full_name: str) -> TypeSpec:
    """Smallest registered type covering ``support`` (the full G_n always does)."""
    want: set[Blade] = set(support)
    candidates: list[TypeSpec] = [
        t for t in registry_for_dim(n, full_name) if want <= set(t.blades)
    ]
    return min(
        candidates,
        key=lambda t: (len(t.blades), 0 if t.kind == "scalar" else 1, t.name),
    )


def product_result(
    lhs_spec: TypeSpec,
    rhs_spec: TypeSpec,
    gn_product: Callable[[Gn, Gn], Gn],
    n: int,
    full_name: str,
) -> tuple[TypeSpec, list[sympy.Expr]]:
    """(result_spec, output exprs over result's blades) for lhs_spec <op> rhs_spec."""
    lhs_symbols: dict[Blade, sympy.Symbol] = {
        b: sympy.Symbol("a_" + blade_label(b)) for b in lhs_spec.blades
    }
    rhs_symbols: dict[Blade, sympy.Symbol] = {
        b: sympy.Symbol("b_" + blade_label(b)) for b in rhs_spec.blades
    }
    result_mv: Gn = gn_product(
        Gn.from_blade_dict(lhs_symbols), Gn.from_blade_dict(rhs_symbols)
    )
    result_coeffs: BladeCoef = result_mv.to_blade_dict()
    support: list[Blade] = [
        b for b in blades_for_dim(n) if sympy.sympify(result_coeffs.get(b, 0)) != 0
    ]
    result_spec: TypeSpec = resolve(support, n, full_name)
    out_exprs: list[sympy.Expr] = [
        sympy.sympify(result_coeffs.get(b, 0)) for b in result_spec.blades
    ]
    return result_spec, out_exprs


def unary_result(
    operand_spec: TypeSpec,
    gn_unary: Callable[[Gn], MultiVectorBase],
    n: int,
    full_name: str,
) -> tuple[TypeSpec, list[sympy.Expr]]:
    """(result_spec, output exprs) for a unary op (dual / grade projection).

    ``gn_unary``'s return is ``MultiVectorBase`` (not ``Gn``) so it also accepts
    ``even_part``/``odd_part``, which base now types ``-> MultiVectorBase``;
    ``Gn``-returning ops (``dual``, grade projection) still fit by covariance."""
    operand_symbols: dict[Blade, sympy.Symbol] = {
        b: sympy.Symbol("a_" + blade_label(b)) for b in operand_spec.blades
    }
    result_mv: MultiVectorBase = gn_unary(Gn.from_blade_dict(operand_symbols))
    result_coeffs: BladeCoef = result_mv.to_blade_dict()
    support: list[Blade] = [
        b for b in blades_for_dim(n) if sympy.sympify(result_coeffs.get(b, 0)) != 0
    ]
    result_spec: TypeSpec = resolve(support, n, full_name)
    out_exprs: list[sympy.Expr] = [
        sympy.sympify(result_coeffs.get(b, 0)) for b in result_spec.blades
    ]
    return result_spec, out_exprs


def _is_neg_term(term: sympy.Expr, rename: dict[str, tuple[str, str]]) -> bool:
    return ast.unparse(expr_to_ast(term, rename)).lstrip().startswith("-")


def summed_value(expr: sympy.Expr, rename: dict[str, tuple[str, str]]) -> ast.expr:
    """A constructor field value: grade-ordered sum of terms (≈ format_assignment).

    Constants are cast to ``Coef``; sums fold left-assoc as ``BinOp`` in
    ``term_grade_key`` order, subtracting negative terms -- so the node tree matches
    the string baseline's operand order.
    """
    expr = sympy.sympify(expr)
    if not expr.free_symbols:
        return cast_coef(expr_to_ast(expr, rename))
    terms: list[sympy.Expr] = (
        sorted(expr.as_ordered_terms(), key=term_grade_key) if expr.is_Add else [expr]
    )
    node: ast.expr = expr_to_ast(terms[0], rename)
    term: sympy.Expr
    for term in terms[1:]:
        if _is_neg_term(term, rename):
            node = ast.BinOp(left=node, op=ast.Sub(), right=expr_to_ast(-term, rename))
        else:
            node = ast.BinOp(left=node, op=ast.Add(), right=expr_to_ast(term, rename))
    return node


def result_value(expr: sympy.Expr, rename: dict[str, tuple[str, str]]) -> ast.expr:
    """Constructor field value for the graded dispatch (mirrors result_block)."""
    e: sympy.Expr = sympy.sympify(expr)
    if e.is_Mul and (-e).is_Symbol:
        return cast_coef(expr_to_ast(e, rename))
    return summed_value(e, rename)


def unary_value(expr: sympy.Expr, rename: dict[str, tuple[str, str]]) -> ast.expr:
    """Constructor field value for unary results (mirrors unary_return)."""
    e: sympy.Expr = sympy.sympify(expr)
    return expr_to_ast(e, rename) if e.is_Symbol else cast_coef(expr_to_ast(e, rename))


# ==========================================================================
# Shared class / method builders (used by every generated class)
# ==========================================================================


#: coordinate-accessor names, by basis index: x = e_1, y = e_2, z = e_3.
AXIS_NAMES = ("x", "y", "z")


def coordinate_property_defs(spec: TypeSpec) -> list[ast.stmt]:
    """``x``/``y``/``z`` read-write properties on grade-1 (vector) types.

    A vector's coordinates ARE its basis coefficients; these are ergonomic
    views over ``coeff_e_1``/``coeff_e_2``/``coeff_e_3`` for consumers that
    speak coordinates (the Code-the-Classics games mutate ``v.x`` per frame).
    Only grade-1 types get them -- ``x`` on a rotor or a full multivector
    would suggest a coordinate tuple it doesn't have."""
    if any(len(b) != 1 for b in spec.blades):
        return []
    defs: list[ast.stmt] = []
    blade: Blade
    for blade in spec.blades:
        axis: str = AXIS_NAMES[blade[0] - 1]
        field: str = field_name(blade)
        defs.append(
            function_def(
                axis,
                [
                    ast.Expr(
                        ast.Constant(
                            f"The {axis} coordinate -- the ``{field}``"
                            " basis coefficient (read/write)."
                        )
                    ),
                    return_stmt(attribute("self", field)),
                ],
                decorators=[name_ref("property")],
                returns=name_ref("Coef"),
            )
        )
        defs.append(
            function_def(
                axis,
                [
                    ast.Assign(
                        targets=[
                            ast.Attribute(
                                value=name_ref("self"),
                                attr=field,
                                ctx=ast.Store(),
                            )
                        ],
                        value=name_ref("value"),
                    )
                ],
                params=[argument("self"), argument("value", name_ref("Coef"))],
                decorators=[attribute(axis, "setter")],
                returns=constant(None),
            )
        )
    return defs


def rename_map(
    blades_self: Sequence[Blade],
    blades_rhs: Sequence[Blade],
    rhs_name: str = "rhs",
) -> dict[str, tuple[str, str]]:
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
        annotated_assign(
            "left",
            name_ref("Gn"),
            call(
                attribute("Gn", "from_blade_dict"),
                [call(attribute("self", "to_blade_dict"))],
            ),
        ),
        annotated_assign(
            "right",
            name_ref("Gn"),
            call(
                attribute("Gn", "from_blade_dict"),
                [call(attribute("rhs", "to_blade_dict"))],
            ),
        ),
    ]


def eq_method() -> ast.FunctionDef:
    """The shared simplify-aware, cross-representation ``__eq__`` as nodes."""
    diff: ast.BinOp = ast.BinOp(
        left=call(
            attribute("sympy", "sympify"),
            [call(attribute("left", "get"), [name_ref("blade"), constant(0)])],
        ),
        op=ast.Sub(),
        right=call(
            attribute("sympy", "sympify"),
            [call(attribute("right", "get"), [name_ref("blade"), constant(0)])],
        ),
    )
    gen: ast.GeneratorExp = ast.GeneratorExp(
        elt=ast.Compare(
            left=call(attribute("sympy", "simplify"), [diff]),
            ops=[ast.Eq()],
            comparators=[constant(0)],
        ),
        generators=[
            ast.comprehension(
                target=ast.Name("blade", _STORE),
                iter=ast.BinOp(
                    left=call("set", [call(attribute("left", "keys"))]),
                    op=ast.BitOr(),
                    right=call("set", [call(attribute("right", "keys"))]),
                ),
                ifs=[],
                is_async=0,
            )
        ],
    )
    body: list[ast.stmt] = [
        ast.If(
            test=not_(isinstance_(name_ref("other"), name_ref("MultiVectorBase"))),
            body=[return_stmt(name_ref("NotImplemented"))],
            orelse=[],
        ),
        annotated_assign(
            "left", name_ref("BladeCoef"), call(attribute("self", "to_blade_dict"))
        ),
        annotated_assign(
            "right", name_ref("BladeCoef"), call(attribute("other", "to_blade_dict"))
        ),
        return_stmt(call("all", [gen])),
    ]
    return function_def(
        "__eq__",
        body,
        params=[argument("self"), argument("other")],
        returns=name_ref("bool"),
    )


def dimension_decl(n: int) -> ast.stmt:
    """``DIMENSION: typing.ClassVar[int] = <n>``."""
    return annotated_assign(
        "DIMENSION",
        subscript(attribute("typing", "ClassVar"), name_ref("int")),
        constant(n),
    )


def field_decls(blades: Sequence[Blade]) -> list[ast.stmt]:
    """``<field>: Coef = cast(Coef, 0)`` per blade."""
    return [
        annotated_assign(field_name(b), name_ref("Coef"), cast_coef(constant(0)))
        for b in blades
    ]


def basis_classvar_decls(name: str, blades: Sequence[Blade]) -> list[ast.stmt]:
    """``e_1: typing.ClassVar[Name]`` ... (annotation only) per nonempty blade.

    Declares the basis-vector class constants so a type checker sees them; the
    *values* are assigned after the class body (a class can't reference itself
    while it is being defined -- see ``basis_constant_assignments``).  As a
    ClassVar these are excluded from the dataclass fields / ``__slots__``.
    """
    return [
        annotated_assign(
            blade_label(b), subscript(attribute("typing", "ClassVar"), name_ref(name))
        )
        for b in blades
        if b != ()
    ]


def basis_constant_assignments(name: str, blades: Sequence[Blade]) -> list[ast.stmt]:
    """``Name.e_1 = Name.from_blade_dict({(1,): 1})`` ... per nonempty blade.

    The basis-vector constants of the class's own type, assigned *after* the
    class so it can reference itself.  Because ``e_1`` is not a (``coeff_``) field,
    both ``Name.e_1`` and ``instance.e_1`` resolve to this one constant.
    """
    return [
        ast.Assign(
            targets=[
                ast.Attribute(value=name_ref(name), attr=blade_label(b), ctx=_STORE)
            ],
            value=call(
                attribute(name, "from_blade_dict"),
                [ast.Dict(keys=[constant(b)], values=[constant(1)])],
            ),
        )
        for b in blades
        if b != ()
    ]


def from_blade_dict_method(blades: Sequence[Blade]) -> ast.FunctionDef:
    """The ``from_blade_dict`` classmethod over the given blades."""
    keywords: list[ast.keyword] = [
        ast.keyword(
            arg=field_name(b),
            value=cast_coef(call(attribute("d", "get"), [constant(b), constant(0)])),
        )
        for b in blades
    ]
    body: list[ast.stmt] = [
        annotated_assign(
            "d", name_ref("BladeCoef"), call("dict", [name_ref("blade_coef")])
        ),
        return_stmt(ast.Call(func=name_ref("cls"), args=[], keywords=keywords)),
    ]
    return function_def(
        "from_blade_dict",
        body,
        params=[argument("cls"), argument("blade_coef")],
        decorators=[name_ref("classmethod")],
        returns=attribute("typing", "Self"),
    )


def to_blade_dict_method(blades: Sequence[Blade]) -> ast.FunctionDef:
    """The ``to_blade_dict`` dict-comprehension method over the given blades."""
    pairs_iter: ast.Tuple = ast.Tuple(
        elts=[
            ast.Tuple(elts=[constant(b), attribute("self", field_name(b))], ctx=_LOAD)
            for b in blades
        ],
        ctx=_LOAD,
    )
    comp: ast.comprehension = ast.comprehension(
        target=ast.Tuple(
            elts=[ast.Name("blade", _STORE), ast.Name("coef", _STORE)], ctx=_STORE
        ),
        iter=pairs_iter,
        ifs=[ne_zero(name_ref("coef"))],
        is_async=0,
    )
    dictcomp: ast.DictComp = ast.DictComp(
        key=name_ref("blade"), value=name_ref("coef"), generators=[comp]
    )
    return function_def(
        "to_blade_dict", [return_stmt(dictcomp)], returns=name_ref("BladeCoef")
    )


def class_header_stmts(doc: str, n: int, blades: Sequence[Blade]) -> list[ast.stmt]:
    """The common class prefix: docstring, DIMENSION, fields, interchange, __eq__."""
    return [
        class_doc_stmt(doc),
        dimension_decl(n),
        *field_decls(blades),
        from_blade_dict_method(blades),
        to_blade_dict_method(blades),
        eq_method(),
    ]


def is_close_method(type_name: str, fields: Sequence[str]) -> ast.FunctionDef:
    """``is_close``: defer to the ABC for a foreign type, else np.isclose per field."""
    return function_def(
        "is_close",
        [
            ast.If(
                not_(isinstance_(name_ref("other"), name_ref(type_name))),
                [return_stmt(super_call("is_close", [name_ref("other")]))],
                [],
            ),
            return_stmt(call("bool", [bool_and([isclose_call(f) for f in fields])])),
        ],
        params=[argument("self"), argument("other")],
        returns=name_ref("bool"),
    )


def iter_method(blades: Sequence[Blade]) -> ast.FunctionDef:
    """``__iter__``: yield the component VALUES, one per field, in blade order.

    A value (vector, rotor, full multivector, ...) reads as the numbers it holds,
    so ``list(v)`` / ``tuple(v)`` / ``np.array([list(v), ...])`` give the
    coefficients -- not one single-blade multivector per term.  All fields are
    yielded (dense, fixed length), so e.g. ``list(Vector2(3, 0)) == [3, 0]``.
    """
    return function_def(
        "__iter__",
        [
            *method_doc_stmts("__iter__"),
            *[ast.Expr(ast.Yield(attribute("self", field_name(b)))) for b in blades],
        ],
    )


def grades_method(grade_groups: Sequence[tuple[int, list[str]]]) -> ast.FunctionDef:
    """``grades``: append each grade whose fields are not all zero.

    ``grade_groups`` is an ordered list of ``(grade, [field names])``.
    """
    body: list[ast.stmt] = [
        annotated_assign(
            "present", subscript(name_ref("list"), name_ref("int")), ast.List([], _LOAD)
        )
    ]
    g: int
    flds: list[str]
    for g, flds in grade_groups:
        body.append(
            ast.If(
                bool_or([ne_zero(attribute("self", f)) for f in flds]),
                [ast.Expr(call(attribute("present", "append"), [constant(g)]))],
                [],
            )
        )
    body.append(return_stmt(name_ref("present")))
    return function_def(
        "grades", body, returns=subscript(name_ref("list"), name_ref("int"))
    )


def result_stmts(
    type_name: str, pairs: Iterable[tuple[str, ast.expr]]
) -> list[ast.stmt]:
    """``return type(self)(...)`` as nodes.

    Every caller passes the OWNING class as ``type_name`` (same-type results:
    the linear ops, reverse, grade parts), so construction goes through
    ``type(self)`` and subclasses get their own type back; no cast needed
    (``type(self)`` is ``type[Self]``).  ``type_name`` is kept for the
    call-site's readability/assertions."""
    return [return_stmt(construct_type_self(pairs))]


def isclose_call(field: str, other: str = "other") -> ast.expr:
    """``np.isclose(float(self.<f>), float(other.<f>), rtol=1e-5, atol=1e-5)``."""
    return call(
        attribute("np", "isclose"),
        [
            call("float", [attribute("self", field)]),
            call("float", [attribute(other, field)]),
        ],
        rtol=constant(1e-5),
        atol=constant(1e-5),
    )


def super_call(method: str, args: list[ast.expr]) -> ast.expr:
    """``super().<method>(<args>)``."""
    return call(attribute(call("super", []), method), args)


def scaled_stmt(
    type_name: str, fields: Sequence[str], value_fn: Callable[[str], ast.expr]
) -> ast.stmt:
    """``return <TypeName>(field=cast(Real, value_fn(field)), ...)``.

    Same-type scalar scaling (mul/rmul/neg) on a graded value type.  Those types
    are ``@typing.final`` (not subclassable), so the concrete class is emitted
    directly.  (This helper is only used by the graded generator; the full G_n
    class scales via ``result_stmts``, which keeps ``type(self)``.)"""
    return return_stmt(
        construct(type_name, [(f, cast_coef(value_fn(f))) for f in fields])
    )


def result_block_stmts(
    result_spec: TypeSpec,
    out_exprs: Sequence[sympy.Expr],
    rename: dict[str, tuple[str, str]],
    cast: Callable[[ast.expr], ast.Call] = cast_self,
    owner: str | None = None,
    via_var: str | None = None,
) -> list[ast.stmt]:
    """cse temps + ``return cast(<T>, RType(...))`` (= result_block, as nodes).

    ``cast`` defaults to ``cast_self``; the rotor sandwich passes ``cast_operand``
    so the return is typed as the operand (``_OperandT``), not ``Self``.
    When ``owner`` equals the result type (a same-type product, e.g.
    Rotor2 * Rotor2 -> Rotor2), construct via ``type(self)`` so subclasses
    are preserved; widening/grade-changing results keep the concrete class
    (a Vector2 subclass has no say over a Rotor2 result).
    ``via_var`` names an operand variable to construct through instead --
    ``cast(<T>, type(<via_var>)(...))``: the sandwich is grade-preserving
    (every arm's result type IS the operand's type, which base.sandwich
    documents as "returns a value of x's own type"), so its arms build via
    ``type(x)`` and an operand subclass keeps its type.
    """
    replacements, reduced = sympy.cse(out_exprs)
    stmts: list[ast.stmt] = [
        annotated_assign(str(t), name_ref("Coef"), expr_to_ast(e, rename))
        for t, e in replacements
    ]
    pairs: list[tuple[str, ast.expr]] = [
        (field_name(b), result_value(e, rename))
        for b, e in zip(result_spec.blades, reduced)
    ]
    if via_var is not None:
        stmts.append(return_stmt(cast(construct_type_of(via_var, pairs))))
    elif owner is not None and owner == result_spec.name and cast is cast_self:
        # Same-type result. A final (graded/scalar) type can't be subclassed, so
        # emit the concrete class directly (``type(self)`` is statically that class
        # anyway); the subclassable full G_n keeps ``type(self)`` so a subclass gets
        # its own type back.
        if result_spec.kind != "full":
            stmts.append(return_stmt(construct(result_spec.name, pairs)))
        else:
            stmts.append(return_stmt(construct_type_self(pairs)))
    else:
        # grade-changing arm (graded types only -- the full G_n's products are all
        # same-type).  These methods return MultiVectorBase, so emit the concrete
        # result type with NO cast; the old cast(Self, Rotor2(...)) was unsound.
        stmts.append(return_stmt(construct(result_spec.name, pairs)))
    return stmts


def unary_stmt(
    result_spec: TypeSpec,
    out_exprs: Sequence[sympy.Expr],
    rename: dict[str, tuple[str, str]],
    owner: str | None = None,
    cast: Callable[[ast.expr], ast.expr] = cast_self,
) -> ast.stmt:
    """``return cast(Self, RType(...))`` (= unary_return, as nodes).

    Same-type results (``owner == result``) construct via ``type(self)``,
    preserving subclasses.  ``cast`` wraps a *different*-type result; it
    defaults to ``cast_self`` (the ``-> Self`` methods).  Pass an identity to
    emit the concrete type directly when the method returns ``MultiVectorBase``
    (r_vector_part's overloaded impl), so no unsound ``Self`` cast is generated."""
    pairs: list[tuple[str, ast.expr]] = [
        (field_name(b), unary_value(e, rename))
        for b, e in zip(result_spec.blades, out_exprs)
    ]
    if owner is not None and owner == result_spec.name:
        # final -> concrete class; full G_n keeps type(self) (as in result_block_stmts)
        if result_spec.kind != "full":
            return return_stmt(construct(result_spec.name, pairs))
        return return_stmt(construct_type_self(pairs))
    return return_stmt(cast(construct(result_spec.name, pairs)))


def _match_class(class_expr: ast.expr) -> ast.MatchClass:
    return ast.MatchClass(cls=class_expr, patterns=[], kwd_attrs=[], kwd_patterns=[])


def dispatch_method(
    self_spec: TypeSpec,
    method: str,
    gn_product: Callable[[Gn, Gn], Gn],
    n: int,
    full_name: str,
    fallback_node: ast.expr,
    number_case: bool = False,
    param_name: str = "rhs",
    return_type: ast.expr | None = None,
    cast: Callable[[ast.expr], ast.Call] = cast_self,
    param_annotation: ast.expr | None = None,
) -> ast.FunctionDef:
    """A method that ``match``es on the operand type (the grade product/sum table).

    Defaults emit ``def <method>(self, rhs) -> typing.Self`` casting each case to
    ``Self`` (the products).  The rotor sandwich overrides ``param_name='x'``,
    ``return_type=_OperandT``, ``cast=cast_operand`` so it is a Liskov-compatible
    override of ``MultiVectorBase.sandwich(self, x: _OperandT) -> _OperandT``
    and is typed as the operand, not ``Self``.
    """
    cases: list[ast.match_case] = []
    if number_case:
        # #3: a bare number is the grade-0 (scalar) operand.  Emit the SAME result
        # as the ``Scalar`` arm below, but reading ``rhs`` directly rather than
        # ``rhs.coeff_scalar`` (an empty rename ``attr`` renders as the bare name) --
        # so there is no intermediate ``Scalar`` object and no re-dispatch.
        num_spec: TypeSpec
        num_exprs: list[sympy.Expr]
        num_spec, num_exprs = product_result(
            self_spec, SCALAR, gn_product, n, full_name
        )
        num_rename: dict[str, tuple[str, str]] = rename_map(
            self_spec.blades, SCALAR.blades, param_name
        )
        num_rename["b_" + blade_label(())] = (param_name, "")
        cases.append(
            ast.match_case(
                pattern=ast.MatchOr(
                    patterns=[
                        _match_class(name_ref("int")),
                        _match_class(name_ref("float")),
                        _match_class(attribute("sympy", "Expr")),
                    ]
                ),
                body=result_block_stmts(
                    num_spec, num_exprs, num_rename, cast, owner=self_spec.name
                ),
            )
        )
    rhs_spec: TypeSpec
    for rhs_spec in [SCALAR, *graded_specs(n)]:
        result_spec: TypeSpec
        out_exprs: list[sympy.Expr]
        result_spec, out_exprs = product_result(
            self_spec, rhs_spec, gn_product, n, full_name
        )
        cases.append(
            ast.match_case(
                pattern=_match_class(name_ref(rhs_spec.name)),
                body=result_block_stmts(
                    result_spec,
                    out_exprs,
                    rename_map(self_spec.blades, rhs_spec.blades, param_name),
                    cast,
                    owner=self_spec.name,
                    # the sandwich (cast_operand) is grade-preserving:
                    # construct via type(<operand>) so subclasses survive.
                    via_var=param_name if cast is cast_operand else None,
                ),
            )
        )
    cases.append(
        ast.match_case(
            pattern=ast.MatchAs(pattern=None, name=None),
            body=[
                annotated_assign(
                    "left",
                    name_ref(full_name),
                    call("_coerce", [name_ref("self"), name_ref(full_name)]),
                ),
                annotated_assign(
                    "right",
                    name_ref(full_name),
                    call("_coerce", [name_ref(param_name), name_ref(full_name)]),
                ),
                # The Gn-coerce fallback returns a G_n.  The overloaded graded
                # products/sums (return_type set, cast_self) return MultiVectorBase,
                # so no cast is needed; the full class (return_type None -> Self) and
                # the sandwich (cast_operand) still cast.
                return_stmt(
                    fallback_node
                    if return_type is not None and cast is cast_self
                    else cast(fallback_node)
                ),
            ],
        )
    )
    body_stmts: list[ast.stmt] = []
    # #1: exact-type early-out.  The dominant operand (measured across the CtC + mvp
    # workloads) is the SAME concrete type as ``self``; a single ``type(x) is T``
    # identity check reaches the closed form without walking the ``match`` ladder.
    # A *subtype* (for which ``type(x) is T`` is False) still falls through to the
    # ``case T()`` arm below, so subclass preservation is unchanged.  Only for the
    # Self-returning ops -- NOT the operand-typed sandwich (cast_operand), where the
    # same-type operand is rare so the extra check would not pay for itself.
    if cast is cast_self:
        st_spec: TypeSpec
        st_exprs: list[sympy.Expr]
        st_spec, st_exprs = product_result(
            self_spec, self_spec, gn_product, n, full_name
        )
        body_stmts.append(
            ast.If(
                ast.Compare(
                    call("type", [name_ref(param_name)]),
                    [ast.Is()],
                    [name_ref(self_spec.name)],
                ),
                result_block_stmts(
                    st_spec,
                    st_exprs,
                    rename_map(self_spec.blades, self_spec.blades, param_name),
                    cast,
                    owner=self_spec.name,
                ),
                [],
            )
        )
    body_stmts.append(ast.Match(subject=name_ref(param_name), cases=cases))
    return function_def(
        method,
        body_stmts,
        params=[argument("self"), argument(param_name, param_annotation)],
        returns=return_type if return_type is not None else attribute("typing", "Self"),
    )


def _number_union() -> ast.expr:
    """The annotation ``int | float | sympy.Expr`` (a scalar Coef operand)."""
    return ast.BinOp(
        ast.BinOp(name_ref("int"), ast.BitOr(), name_ref("float")),
        ast.BitOr(),
        attribute("sympy", "Expr"),
    )


def product_overload_stubs(
    method: str,
    self_spec: TypeSpec,
    gn_product: Callable[[Gn, Gn], Gn],
    n: int,
    full_name: str,
    param_name: str = "rhs",
    number_case: bool = False,
) -> list[ast.stmt]:
    """``@typing.overload`` signatures for a bilinear-product method -- one per rhs
    type, each returning the **resolved concrete type** (e.g. ``Vector2 * Vector2``
    -> ``Rotor2``).  So the operator/method types precisely at a known-type call
    site instead of the imprecise, unsound ``-> Self``.  Emitted just before the
    implementation (which does the real dispatch and stays ``-> Self``).

    The final ``MultiVectorBase`` catch-all covers ``Gn`` / the full class / any
    other operand, which the impl coerces to ``G_n``; ``number_case`` adds a scalar
    (``int | float | sympy.Expr``) overload that scales, returning ``Self``'s type.
    """

    def stub(param_ann: ast.expr, ret: ast.expr) -> ast.stmt:
        return function_def(
            method,
            [ast.Expr(constant(...))],
            params=[argument("self"), argument(param_name, param_ann)],
            decorators=[attribute("typing", "overload")],
            returns=ret,
        )

    stubs: list[ast.stmt] = []
    if number_case:
        # A bare number is a grade-0 (Scalar) operand: for ``*`` this scales (result
        # = Self), for ``+``/``-`` it adds a scalar (e.g. Bivector2 + scalar ->
        # Rotor2).  Both fall out of ``product_result(self, Scalar)``.
        num_spec: TypeSpec
        num_spec, _ = product_result(self_spec, SCALAR, gn_product, n, full_name)
        stubs.append(stub(_number_union(), name_ref(num_spec.name)))
    rhs_spec: TypeSpec
    for rhs_spec in [SCALAR, *graded_specs(n)]:
        result_spec: TypeSpec
        result_spec, _ = product_result(self_spec, rhs_spec, gn_product, n, full_name)
        stubs.append(stub(name_ref(rhs_spec.name), name_ref(result_spec.name)))
    stubs.append(stub(name_ref("MultiVectorBase"), name_ref(full_name)))
    return stubs


# ==========================================================================
# The four generators (one per emitted construct)
# ==========================================================================


def generate_scalar() -> list[ast.stmt]:
    """The shared grade-0 ``Scalar`` type, hand-built as `ast` nodes (level C)."""
    self_scalar_field: ast.expr = attribute("self", field_name(()))

    def scalar_const(
        value: ast.expr,
    ) -> ast.expr:  # Scalar(coeff_scalar=value) -- Scalar is @final, so concrete
        return construct("Scalar", [(field_name(()), value)])

    def scalar_const_coef(
        value: ast.expr,
    ) -> ast.expr:  # cast(typing.Self, Scalar(coeff_scalar=cast(Coef, value)))
        return scalar_const(cast_coef(value))

    def mul_expr(a: ast.expr, b: ast.expr) -> ast.BinOp:
        return ast.BinOp(left=a, op=ast.Mult(), right=b)

    self_ann: ast.expr = attribute("typing", "Self")
    coef_ann: ast.expr = name_ref("Coef")
    number_types: list[ast.expr] = [
        name_ref("int"),
        name_ref("float"),
        attribute("sympy", "Expr"),
    ]

    body: list[ast.stmt] = [
        class_doc_stmt(SCALAR_DOC),
        annotated_assign(field_name(()), coef_ann, cast_coef(constant(0))),
        function_def(
            "from_blade_dict",
            [
                assign("d", call("dict", [name_ref("blade_coef")])),
                return_stmt(
                    ast.Call(
                        func=name_ref("cls"),
                        args=[],
                        keywords=[
                            ast.keyword(
                                arg=field_name(()),
                                value=cast_coef(
                                    call(
                                        attribute("d", "get"),
                                        [constant(()), constant(0)],
                                    )
                                ),
                            )
                        ],
                    )
                ),
            ],
            params=[argument("cls"), argument("blade_coef")],
            decorators=[name_ref("classmethod")],
            returns=self_ann,
        ),
        function_def(
            "to_blade_dict",
            [
                return_stmt(
                    ast.IfExp(
                        test=ne_zero(self_scalar_field),
                        body=ast.Dict(keys=[constant(())], values=[self_scalar_field]),
                        orelse=ast.Dict(keys=[], values=[]),
                    )
                )
            ],
            returns=name_ref("BladeCoef"),
        ),
        eq_method(),
        function_def(
            "__mul__",
            [
                ast.If(
                    isinstance_(name_ref("rhs"), number_types),
                    [
                        return_stmt(
                            scalar_const_coef(
                                mul_expr(self_scalar_field, name_ref("rhs"))
                            )
                        )
                    ],
                    [],
                ),
                return_stmt(
                    call(attribute("self", "_geometric_product"), [name_ref("rhs")])
                ),
            ],
            params=[argument("self"), argument("rhs")],
            returns=self_ann,
        ),
        function_def(
            "__rmul__",
            [
                ast.If(
                    isinstance_(name_ref("lhs"), number_types),
                    [
                        return_stmt(
                            scalar_const_coef(
                                mul_expr(name_ref("lhs"), self_scalar_field)
                            )
                        )
                    ],
                    [],
                ),
                return_stmt(
                    call(attribute("self", "_geometric_product"), [name_ref("lhs")])
                ),
            ],
            params=[argument("self"), argument("lhs")],
            returns=self_ann,
        ),
        function_def(
            "_geometric_product",
            [
                ast.If(
                    isinstance_(name_ref("rhs"), name_ref("Scalar")),
                    [
                        return_stmt(
                            scalar_const_coef(
                                mul_expr(
                                    self_scalar_field, attribute("rhs", field_name(()))
                                )
                            )
                        )
                    ],
                    [],
                ),
                ast.If(
                    isinstance_(name_ref("rhs"), name_ref("MultiVectorBase")),
                    [
                        return_stmt(
                            cast_self(mul_expr(self_scalar_field, name_ref("rhs")))
                        )
                    ],
                    [],
                ),
                return_stmt(
                    scalar_const_coef(mul_expr(self_scalar_field, name_ref("rhs")))
                ),
            ],
            params=[argument("self"), argument("rhs")],
            returns=self_ann,
        ),
        function_def(
            "outer_product",
            [
                return_stmt(
                    call(attribute("self", "_geometric_product"), [name_ref("rhs")])
                )
            ],
            params=[argument("self"), argument("rhs")],
            returns=self_ann,
        ),
        function_def(
            "inner_product",
            coerce_pair_gn()
            + [
                return_stmt(
                    cast_self(
                        call(attribute("left", "inner_product"), [name_ref("right")])
                    )
                )
            ],
            params=[argument("self"), argument("rhs")],
            returns=self_ann,
        ),
        function_def(
            "__add__",
            [
                ast.If(
                    isinstance_(name_ref("rhs"), number_types),
                    [
                        return_stmt(
                            scalar_const_coef(
                                ast.BinOp(self_scalar_field, ast.Add(), name_ref("rhs"))
                            )
                        )
                    ],
                    [],
                ),
                ast.If(
                    isinstance_(name_ref("rhs"), name_ref("Scalar")),
                    [
                        return_stmt(
                            scalar_const(
                                ast.BinOp(
                                    self_scalar_field,
                                    ast.Add(),
                                    attribute("rhs", field_name(())),
                                )
                            )
                        )
                    ],
                    [],
                ),
                ast.If(
                    isinstance_(name_ref("rhs"), name_ref("MultiVectorBase")),
                    [
                        return_stmt(
                            cast_self(
                                ast.BinOp(name_ref("rhs"), ast.Add(), name_ref("self"))
                            )
                        )
                    ],
                    [],
                ),
                return_stmt(cast_self(name_ref("NotImplemented"))),
            ],
            params=[argument("self"), argument("rhs")],
            returns=self_ann,
        ),
        function_def(
            "__radd__",
            [return_stmt(call(attribute("self", "__add__"), [name_ref("lhs")]))],
            params=[argument("self"), argument("lhs")],
            returns=self_ann,
        ),
        function_def(
            "__sub__",
            [
                return_stmt(
                    ast.BinOp(
                        name_ref("self"),
                        ast.Add(),
                        mul_expr(ast.UnaryOp(ast.USub(), constant(1)), name_ref("rhs")),
                    )
                )
            ],
            params=[argument("self"), argument("rhs")],
            returns=self_ann,
        ),
        function_def(
            "__rsub__",
            [
                return_stmt(
                    ast.BinOp(
                        ast.UnaryOp(ast.USub(), name_ref("self")),
                        ast.Add(),
                        name_ref("lhs"),
                    )
                )
            ],
            params=[argument("self"), argument("lhs")],
            returns=self_ann,
        ),
        function_def(
            "__neg__",
            [
                return_stmt(
                    scalar_const_coef(ast.UnaryOp(ast.USub(), self_scalar_field))
                )
            ],
            returns=self_ann,
        ),
        function_def(
            "reverse", [return_stmt(scalar_const(self_scalar_field))], returns=self_ann
        ),
        function_def("scalar_part", [return_stmt(self_scalar_field)], returns=coef_ann),
        function_def(
            "grades",
            [
                return_stmt(
                    ast.IfExp(
                        test=ne_zero(self_scalar_field),
                        body=ast.List(elts=[constant(0)], ctx=_LOAD),
                        orelse=ast.List(elts=[], ctx=_LOAD),
                    )
                )
            ],
            returns=subscript(name_ref("list"), name_ref("int")),
        ),
        function_def(
            "is_close",
            [
                ast.If(
                    not_(isinstance_(name_ref("other"), name_ref("Scalar"))),
                    [
                        return_stmt(
                            call(
                                attribute(call("super", []), "is_close"),
                                [name_ref("other")],
                            )
                        )
                    ],
                    [],
                ),
                return_stmt(
                    call(
                        "bool",
                        [
                            call(
                                attribute("np", "isclose"),
                                [
                                    call("float", [self_scalar_field]),
                                    call("float", [attribute("other", field_name(()))]),
                                ],
                                rtol=constant(1e-5),
                                atol=constant(1e-5),
                            )
                        ],
                    )
                ),
            ],
            params=[argument("self"), argument("other")],
            returns=name_ref("bool"),
        ),
        function_def(
            "__iter__",
            [
                ast.If(
                    ne_zero(self_scalar_field),
                    [
                        ast.Expr(
                            ast.Yield(
                                construct(
                                    "Scalar", [(field_name(()), self_scalar_field)]
                                )
                            )
                        )
                    ],
                    [],
                )
            ],
        ),
        function_def(
            "even_part",
            [return_stmt(scalar_const(self_scalar_field))],
            returns=self_ann,
        ),
        function_def(
            "odd_part", [return_stmt(scalar_const_coef(constant(0)))], returns=self_ann
        ),
        function_def(
            "r_vector_part",
            [
                ast.If(
                    ast.Compare(name_ref("r"), [ast.Eq()], [constant(0)]),
                    [return_stmt(scalar_const(self_scalar_field))],
                    [],
                ),
                return_stmt(scalar_const_coef(constant(0))),
            ],
            params=[argument("self"), argument("r", name_ref("int"))],
            returns=self_ann,
        ),
        function_def(
            "dual",
            [
                ast.If(
                    ast.Compare(name_ref("n"), [ast.Is()], [constant(None)]),
                    [
                        ast.Raise(
                            exc=call(
                                "ValueError",
                                [constant("Scalar.dual needs an explicit dimension n")],
                            ),
                            cause=None,
                        )
                    ],
                    [],
                ),
                return_stmt(
                    cast_self(
                        call(
                            attribute(
                                call(
                                    attribute("Gn", "from_blade_dict"),
                                    [call(attribute("self", "to_blade_dict"))],
                                ),
                                "dual",
                            ),
                            [name_ref("n")],
                        )
                    )
                ),
            ],
            params=[argument("self"), argument("n", opt_int())],
            defaults=[constant(None)],
            returns=self_ann,
        ),
    ]
    return [
        class_def(
            "Scalar",
            body,
            decorators=[
                attribute("typing", "final"),
                dataclass_decorator(eq=False, slots=True),
            ],
        )
    ]


def generate_class(n: int, name: str) -> list[ast.stmt]:
    """The full all-blades G_n class, hand-built as `ast` nodes (level C)."""
    blades: list[Blade] = blades_for_dim(n)
    fields: list[str] = [field_name(b) for b in blades]
    rename: dict[str, tuple[str, str]] = rename_map(blades, blades)
    a_mv: Gn = Gn.from_blade_dict(
        {b: sympy.Symbol("a_" + blade_label(b)) for b in blades}
    )
    b_mv: Gn = Gn.from_blade_dict(
        {b: sympy.Symbol("b_" + blade_label(b)) for b in blades}
    )
    by_grade: dict[int, list[Blade]] = {
        g: [b for b in blades if len(b) == g] for g in range(n + 1)
    }
    self_ann: ast.expr = attribute("typing", "Self")

    def bilinear(method: str, cross_node: ast.expr, result_mv: Gn) -> ast.FunctionDef:
        result_coeffs: BladeCoef = result_mv.to_blade_dict()
        replacements, reduced = sympy.cse(
            [sympy.sympify(result_coeffs.get(b, 0)) for b in blades]
        )
        body: list[ast.stmt] = method_doc_stmts(method) + [
            ast.If(
                not_(isinstance_(name_ref("rhs"), name_ref(name))),
                coerce_pair_gn() + [return_stmt(cast_self(cross_node))],
                [],
            )
        ]
        body += [assign(str(t), expr_to_ast(e, rename)) for t, e in replacements]
        pairs: list[tuple[str, ast.expr]] = [
            (field_name(b), summed_value(e, rename)) for b, e in zip(blades, reduced)
        ]
        body += result_stmts(name, pairs)
        return function_def(
            method, body, params=[argument("self"), argument("rhs")], returns=self_ann
        )

    def linear(
        method: str, op_cls: type[ast.operator], gn_op_cls: type[ast.operator]
    ) -> ast.FunctionDef:
        return function_def(
            method,
            [
                ast.If(
                    not_(isinstance_(name_ref("rhs"), name_ref(name))),
                    coerce_pair_gn()
                    + [
                        return_stmt(
                            cast_self(
                                ast.BinOp(
                                    name_ref("left"), gn_op_cls(), name_ref("right")
                                )
                            )
                        )
                    ],
                    [],
                ),
                *result_stmts(
                    name,
                    [
                        (
                            f,
                            ast.BinOp(
                                attribute("self", f), op_cls(), attribute("rhs", f)
                            ),
                        )
                        for f in fields
                    ],
                ),
            ],
            params=[argument("self"), argument("rhs")],
            returns=self_ann,
        )

    rvp_cases: list[ast.match_case] = [
        ast.match_case(
            pattern=ast.MatchValue(constant(g)),
            body=result_stmts(
                name,
                [
                    (field_name(b), attribute("self", field_name(b)))
                    for b in by_grade[g]
                ],
            ),
        )
        for g in range(n + 1)
    ]
    rvp_cases.append(
        ast.match_case(
            pattern=ast.MatchAs(pattern=None, name=None), body=result_stmts(name, [])
        )
    )

    rev_pairs: list[tuple[str, ast.expr]] = []
    b: Blade
    for b in blades:
        f: str = field_name(b)
        sign: int = (-1) ** ((len(b) * (len(b) - 1)) // 2)
        rev_pairs.append(
            (
                f,
                attribute("self", f)
                if sign == 1
                else cast_coef(ast.UnaryOp(ast.USub(), attribute("self", f))),
            )
        )

    def grade_copy(parity: int) -> list[tuple[str, ast.expr]]:
        return [
            (field_name(b), attribute("self", field_name(b)))
            for b in blades
            if len(b) % 2 == parity
        ]

    def default_dim_test() -> ast.expr:
        # ``n is None or n == <DIMENSION>`` -- the guard under which the
        # gen-time-known value applies.  ``n`` is retained only because the
        # base methods are n-required (Liskov); a non-default ``n`` (never used
        # for a fixed-dimension class in practice) falls back to super().
        return bool_or(
            [
                ast.Compare(name_ref("n"), [ast.Is()], [constant(None)]),
                ast.Compare(name_ref("n"), [ast.Eq()], [constant(n)]),
            ]
        )

    def const_mv(one_blade: Blade | None, value: int = 1) -> ast.Call:
        # ``cls(field=..., ...)`` with ``one_blade``'s field = ``value`` and the
        # rest 0 -- built via ``cls`` so a subclass gets its own type back.
        return construct(
            "cls",
            [
                (field_name(b), constant(value if b == one_blade else 0))
                for b in blades
            ],
        )

    def dimension_known_methods() -> list[ast.stmt]:
        # The dimension is fixed at generation time, so dual / unit_pseudoscalar
        # / its square / bases / symbolic_multivector emit the closed form or
        # constant directly instead of running base's general n-parametrized
        # algorithm (products of basis vectors, powersets).
        dual_coeffs: BladeCoef = a_mv.dual(n).to_blade_dict()
        top_blade: Blade = blades[-1]
        pseudoscalar: Gn = Gn.from_blade_dict({top_blade: 1})
        i_squared: int = int(
            sympy.sympify((pseudoscalar * pseudoscalar).to_blade_dict().get((), 0))
        )
        return [
            function_def(
                "dual",
                method_doc_stmts("dual")
                + [
                    ast.If(
                        default_dim_test(),
                        result_stmts(
                            name,
                            [
                                (
                                    field_name(b),
                                    summed_value(
                                        sympy.sympify(dual_coeffs.get(b, 0)), rename
                                    ),
                                )
                                for b in blades
                            ],
                        ),
                        [],
                    ),
                    return_stmt(super_call("dual", [name_ref("n")])),
                ],
                params=[argument("self"), argument("n", opt_int())],
                defaults=[constant(None)],
                returns=self_ann,
            ),
            function_def(
                "unit_pseudoscalar",
                method_doc_stmts("unit_pseudoscalar")
                + [
                    ast.If(
                        default_dim_test(),
                        [return_stmt(const_mv(top_blade))],
                        [],
                    ),
                    return_stmt(super_call("unit_pseudoscalar", [name_ref("n")])),
                ],
                params=[argument("cls"), argument("n", opt_int())],
                defaults=[constant(None)],
                decorators=[name_ref("classmethod")],
                returns=self_ann,
            ),
            function_def(
                "unit_pseudoscalar_squared",
                [
                    ast.If(
                        default_dim_test(),
                        [return_stmt(const_mv((), value=i_squared))],
                        [],
                    ),
                    return_stmt(
                        super_call("unit_pseudoscalar_squared", [name_ref("n")])
                    ),
                ],
                params=[argument("cls"), argument("n", opt_int())],
                defaults=[constant(None)],
                decorators=[name_ref("classmethod")],
                returns=self_ann,
            ),
            function_def(
                "bases",
                [
                    ast.If(
                        default_dim_test(),
                        [
                            ast.Expr(
                                ast.YieldFrom(
                                    ast.List(
                                        elts=[const_mv(b) for b in blades],
                                        ctx=ast.Load(),
                                    )
                                )
                            )
                        ],
                        [
                            ast.Expr(
                                ast.YieldFrom(super_call("bases", [name_ref("n")]))
                            )
                        ],
                    ),
                ],
                params=[argument("cls"), argument("n", opt_int())],
                defaults=[constant(None)],
                decorators=[name_ref("classmethod")],
                returns=subscript(name_ref("Generator"), self_ann),
            ),
            function_def(
                "symbolic_multivector",
                [
                    ast.If(
                        default_dim_test(),
                        [
                            return_stmt(
                                construct(
                                    "cls",
                                    [
                                        (
                                            field_name(b),
                                            call(
                                                attribute("sympy", "Symbol"),
                                                [
                                                    ast.BinOp(
                                                        name_ref("prefix"),
                                                        ast.Add(),
                                                        constant(str(i)),
                                                    )
                                                ],
                                            ),
                                        )
                                        for i, b in enumerate(blades)
                                    ],
                                )
                            )
                        ],
                        [],
                    ),
                    return_stmt(
                        super_call(
                            "symbolic_multivector",
                            [name_ref("n"), name_ref("prefix")],
                        )
                    ),
                ],
                params=[
                    argument("cls"),
                    argument("n", opt_int()),
                    argument("prefix", name_ref("str")),
                ],
                defaults=[constant(None), constant("a")],
                decorators=[name_ref("classmethod")],
                returns=self_ann,
            ),
        ]

    body: list[ast.stmt] = [
        *class_header_stmts(docstring_for(n), n, blades),
        *basis_classvar_decls(name, blades),
        bilinear(
            "_geometric_product",
            ast.BinOp(name_ref("left"), ast.Mult(), name_ref("right")),
            a_mv * b_mv,
        ),
        bilinear(
            "inner_product",
            call(attribute("left", "inner_product"), [name_ref("right")]),
            a_mv.inner_product(b_mv),
        ),
        bilinear(
            "outer_product",
            call(attribute("left", "outer_product"), [name_ref("right")]),
            a_mv.outer_product(b_mv),
        ),
        linear("__add__", ast.Add, ast.Add),
        linear("__sub__", ast.Sub, ast.Sub),
        function_def(
            "__neg__",
            result_stmts(
                name,
                [
                    (f, cast_coef(ast.UnaryOp(ast.USub(), attribute("self", f))))
                    for f in fields
                ],
            ),
            returns=self_ann,
        ),
        function_def(
            "scalar_part",
            method_doc_stmts("scalar_part")
            + [return_stmt(attribute("self", field_name(())))],
            returns=name_ref("Coef"),
        ),
        grades_method(
            [(g, [field_name(b) for b in by_grade[g]]) for g in range(n + 1)]
        ),
        function_def(
            "r_vector_part",
            method_doc_stmts("r_vector_part")
            + [ast.Match(subject=name_ref("r"), cases=rvp_cases)],
            params=[argument("self"), argument("r", name_ref("int"))],
            returns=self_ann,
        ),
        function_def(
            "reverse",
            method_doc_stmts("reverse") + result_stmts(name, rev_pairs),
            returns=self_ann,
        ),
        function_def(
            "even_part",
            method_doc_stmts("even_part") + result_stmts(name, grade_copy(0)),
            returns=self_ann,
        ),
        function_def(
            "odd_part",
            method_doc_stmts("odd_part") + result_stmts(name, grade_copy(1)),
            returns=self_ann,
        ),
        is_close_method(name, fields),
        iter_method(blades),
        *dimension_known_methods(),
    ]
    return [
        class_def(name, body, decorators=[dataclass_decorator(eq=False, slots=True)]),
        *basis_constant_assignments(name, blades),
    ]


def generate_graded_type(spec: TypeSpec, n: int, full_name: str) -> list[ast.stmt]:
    """A graded subtype (Vector/Bivector/Trivector/Rotor), as nodes (level C)."""
    blades: list[Blade] = list(spec.blades)
    fields: list[str] = [field_name(b) for b in blades]
    has_scalar: bool = () in blades
    unary_rename: dict[str, tuple[str, str]] = rename_map(spec.blades, ())
    numlike: list[ast.expr] = [
        name_ref("int"),
        name_ref("float"),
        attribute("sympy", "Expr"),
    ]
    self_ann: ast.expr = attribute("typing", "Self")
    # The *implementation* return type of an overloaded product/sum method.  Its
    # overloads return the resolved concrete types (Rotor2, Bivector2, ...), which
    # are NOT subtypes of one another nor of the full class G_n (all are siblings
    # under MultiVectorBase) -- so the impl's own return must be their one common
    # supertype, ``MultiVectorBase``, to stay consistent with its overloads (and
    # honest: the old ``-> Self`` claimed Vector2 while returning a Rotor2).
    mvb_ann: ast.expr = name_ref("MultiVectorBase")
    # ``self +/- scalar`` result type (e.g. Bivector2 + scalar -> Rotor2).  Used to
    # type __radd__/__rsub__, whose left operand is always a bare number, so their
    # return narrows by grade just like __add__'s scalar arm.  ``a - self`` and
    # ``self + a`` span the same grades ({0} plus self's), so one spec serves both.
    add_scalar_spec: TypeSpec
    add_scalar_spec, _ = product_result(
        spec, SCALAR, lambda a, b: a + b, n, full_name
    )
    radd_ann: ast.expr = name_ref(add_scalar_spec.name)

    # #4: closed-form magnitude_squared = |A|^2 = <~A A> (a scalar), derived
    # symbolically exactly as the base method computes it -- self.reverse() then
    # scalar_product -- but collapsed to direct field arithmetic (e.g. e_1**2 +
    # e_2**2 for a vector).  The inherited base magnitude()/normalize()/__abs__()
    # call this via self, so they too stop round-tripping through
    # to_blade_dict()/from_blade_dict().  base.py is untouched (still the reference).
    msq_symbols: dict[Blade, sympy.Symbol] = {
        b: sympy.Symbol("a_" + blade_label(b)) for b in spec.blades
    }
    msq_sym: Gn = Gn.from_blade_dict(msq_symbols)
    msq_expr: sympy.Expr = sympy.sympify(msq_sym.reverse().scalar_product(msq_sym))

    def unary_body(
        gn_unary: Callable[[Gn], MultiVectorBase],
        cast: Callable[[ast.expr], ast.expr] = cast_self,
    ) -> ast.stmt:
        result_spec, out_exprs = unary_result(spec, gn_unary, n, full_name)
        return unary_stmt(
            result_spec, out_exprs, unary_rename, owner=spec.name, cast=cast
        )

    def parity_part(
        method: str, gn_unary: Callable[[Gn], MultiVectorBase]
    ) -> ast.FunctionDef:
        # even_part/odd_part have no argument to overload on, so the override
        # simply *declares* its resolved return type (e.g. Vector2.even_part ->
        # Scalar) -- a valid narrowing of base's MultiVectorBase.  The impl
        # constructs that type directly (identity cast -> no unsound Self cast).
        result_spec, _ = unary_result(spec, gn_unary, n, full_name)
        return function_def(
            method,
            [unary_body(gn_unary, cast=lambda node: node)],
            returns=name_ref(result_spec.name),
        )

    rev_pairs: list[tuple[str, ast.expr]] = []
    b: Blade
    for b in blades:
        f: str = field_name(b)
        sign: int = (-1) ** ((len(b) * (len(b) - 1)) // 2)
        rev_pairs.append(
            (
                f,
                attribute("self", f)
                if sign == 1
                else cast_coef(ast.UnaryOp(ast.USub(), attribute("self", f))),
            )
        )

    # r_vector_part: an @overload per grade maps ``r: Literal[<grade>]`` to the
    # resolved grade-r-part type (present grade -> that grade's type, e.g.
    # Rotor2 grade 2 -> Bivector2; absent grade -> Scalar, the returned zero), so
    # a literal-``r`` call types precisely.  The impl returns MultiVectorBase and
    # constructs each branch's concrete type directly -- no unsound ``Self`` cast.
    def rvp_overload_stub(param_ann: ast.expr, ret: ast.expr) -> ast.stmt:
        return function_def(
            "r_vector_part",
            [ast.Expr(constant(...))],
            params=[argument("self"), argument("r", param_ann)],
            decorators=[attribute("typing", "overload")],
            returns=ret,
        )

    rvp_overload_stubs: list[ast.stmt] = []
    for r in range(n + 1):
        rvp_spec: TypeSpec
        rvp_spec, _ = unary_result(
            spec, lambda a, r=r: a.r_vector_part(r), n, full_name
        )
        rvp_overload_stubs.append(
            rvp_overload_stub(
                subscript(attribute("typing", "Literal"), constant(r)),
                name_ref(rvp_spec.name),
            )
        )
    # a non-literal ``r: int`` can select any grade part -> MultiVectorBase
    rvp_overload_stubs.append(rvp_overload_stub(name_ref("int"), mvb_ann))

    rvp_body: list[ast.stmt] = [
        ast.If(
            ast.Compare(name_ref("r"), [ast.Eq()], [constant(r)]),
            [unary_body(lambda a, r=r: a.r_vector_part(r), cast=lambda node: node)],
            [],
        )
        for r in range(n + 1)
    ]
    rvp_body.append(
        return_stmt(construct("Scalar", [(field_name(()), cast_coef(constant(0)))]))
    )

    body: list[ast.stmt] = [
        *class_header_stmts(graded_docstring(spec), n, blades),
        *basis_classvar_decls(spec.name, blades),
        # scalar-aware __mul__ / __rmul__ (the ABC versions would drop the scalar
        # for a type with no scalar field, so they are overridden here).  The
        # @overload stubs give the operator its precise result type per rhs (e.g.
        # Vector2 * Vector2 -> Rotor2) -- sound, since the impl returns exactly that
        # runtime type; the operator's old blanket -> Self was an unsound cast.
        *product_overload_stubs(
            "__mul__", spec, lambda a, b: a * b, n, full_name, number_case=True
        ),
        function_def(
            "__mul__",
            [
                ast.If(
                    isinstance_(name_ref("rhs"), numlike),
                    [
                        scaled_stmt(
                            spec.name,
                            fields,
                            lambda f: ast.BinOp(
                                attribute("self", f), ast.Mult(), name_ref("rhs")
                            ),
                        )
                    ],
                    [],
                ),
                return_stmt(
                    call(attribute("self", "_geometric_product"), [name_ref("rhs")])
                ),
            ],
            params=[argument("self"), argument("rhs")],
            returns=mvb_ann,
        ),
        function_def(
            "__rmul__",
            [
                ast.If(
                    isinstance_(name_ref("lhs"), numlike),
                    [
                        scaled_stmt(
                            spec.name,
                            fields,
                            lambda f: ast.BinOp(
                                name_ref("lhs"), ast.Mult(), attribute("self", f)
                            ),
                        )
                    ],
                    [],
                ),
                return_stmt(
                    call(attribute("self", "_geometric_product"), [name_ref("lhs")])
                ),
            ],
            params=[argument("self"), argument("lhs")],
            returns=self_ann,
        ),
        # the three bilinear products + the two linear ops, each a match on rhs type.
        # _geometric_product is overloaded like the public products and returns
        # MultiVectorBase, so a direct caller gets the precise type and its arms
        # need no cast (the old cast(Self, Rotor2(...)) was unsound).
        *product_overload_stubs(
            "_geometric_product", spec, lambda a, b: a * b, n, full_name
        ),
        dispatch_method(
            spec,
            "_geometric_product",
            lambda a, b: a * b,
            n,
            full_name,
            ast.BinOp(name_ref("left"), ast.Mult(), name_ref("right")),
            return_type=mvb_ann,
        ),
        *product_overload_stubs(
            "outer_product", spec, lambda a, b: a.outer_product(b), n, full_name
        ),
        dispatch_method(
            spec,
            "outer_product",
            lambda a, b: a.outer_product(b),
            n,
            full_name,
            call(attribute("left", "outer_product"), [name_ref("right")]),
            return_type=mvb_ann,
        ),
        # ``a ^ b`` (the wedge operator): base ``__xor__`` returns Self, so override
        # here with the same precise overloads as outer_product, delegating to it.
        *product_overload_stubs(
            "__xor__",
            spec,
            lambda a, b: a.outer_product(b),
            n,
            full_name,
            param_name="other",
        ),
        function_def(
            "__xor__",
            [
                return_stmt(
                    call(attribute("self", "outer_product"), [name_ref("other")])
                )
            ],
            params=[argument("self"), argument("other")],
            returns=mvb_ann,
        ),
        *product_overload_stubs(
            "inner_product", spec, lambda a, b: a.inner_product(b), n, full_name
        ),
        dispatch_method(
            spec,
            "inner_product",
            lambda a, b: a.inner_product(b),
            n,
            full_name,
            call(attribute("left", "inner_product"), [name_ref("right")]),
            return_type=mvb_ann,
        ),
        # +/- also narrow by grade: scalar + bivector -> Rotor2, etc.  Overload them
        # too so a mixed-grade sum types precisely instead of -> Self.
        *product_overload_stubs(
            "__add__", spec, lambda a, b: a + b, n, full_name, number_case=True
        ),
        dispatch_method(
            spec,
            "__add__",
            lambda a, b: a + b,
            n,
            full_name,
            ast.BinOp(name_ref("left"), ast.Add(), name_ref("right")),
            number_case=True,
            return_type=mvb_ann,
        ),
        *product_overload_stubs(
            "__sub__", spec, lambda a, b: a - b, n, full_name, number_case=True
        ),
        dispatch_method(
            spec,
            "__sub__",
            lambda a, b: a - b,
            n,
            full_name,
            ast.BinOp(name_ref("left"), ast.Sub(), name_ref("right")),
            number_case=True,
            return_type=mvb_ann,
        ),
        function_def(
            "__radd__",
            # __add__ is overloaded, so its scalar arm already returns the narrowed
            # type (e.g. Bivector2 + scalar -> Rotor2); just forward.
            [return_stmt(call(attribute("self", "__add__"), [name_ref("lhs")]))],
            params=[argument("self"), argument("lhs", _number_union())],
            returns=radd_ann,
        ),
        function_def(
            "__rsub__",
            [
                return_stmt(
                    call(
                        attribute(
                            ast.UnaryOp(ast.USub(), name_ref("self")), "__add__"
                        ),
                        [name_ref("lhs")],
                    )
                )
            ],
            params=[argument("self"), argument("lhs", _number_union())],
            returns=radd_ann,
        ),
        function_def(
            "__neg__",
            [
                scaled_stmt(
                    spec.name,
                    fields,
                    lambda f: ast.UnaryOp(ast.USub(), attribute("self", f)),
                )
            ],
            returns=self_ann,
        ),
        function_def(
            "reverse",
            [return_construct(spec.name, rev_pairs, owner=spec.name, final=True)],
            returns=self_ann,
        ),
        function_def(
            "scalar_part",
            [
                return_stmt(
                    attribute("self", field_name(()))
                    if has_scalar
                    else cast_coef(constant(0))
                )
            ],
            returns=name_ref("Coef"),
        ),
        function_def(
            "magnitude_squared",
            method_doc_stmts("magnitude_squared")
            + [return_stmt(cast_coef(expr_to_ast(msq_expr, unary_rename)))],
            returns=name_ref("Coef"),
        ),
        grades_method(
            [
                (g, [field_name(b) for b in blades if len(b) == g])
                for g in sorted({len(b) for b in blades})
            ]
        ),
        is_close_method(spec.name, fields),
        *coordinate_property_defs(spec),
        iter_method(blades),
        parity_part("even_part", lambda a: a.even_part()),
        parity_part("odd_part", lambda a: a.odd_part()),
        *rvp_overload_stubs,
        function_def(
            "r_vector_part",
            rvp_body,
            params=[argument("self"), argument("r", name_ref("int"))],
            returns=mvb_ann,
        ),
        function_def(
            "dual",
            [
                ast.If(
                    bool_or(
                        [
                            ast.Compare(name_ref("n"), [ast.Is()], [constant(None)]),
                            ast.Compare(name_ref("n"), [ast.Eq()], [constant(n)]),
                        ]
                    ),
                    [unary_body(lambda a: a.dual(n))],
                    [],
                ),
                return_stmt(
                    cast_self(
                        call(
                            attribute(
                                call(
                                    "_coerce", [name_ref("self"), name_ref(full_name)]
                                ),
                                "dual",
                            ),
                            [name_ref("n")],
                        )
                    )
                ),
            ],
            params=[argument("self"), argument("n", opt_int())],
            defaults=[constant(None)],
            returns=self_ann,
        ),
    ]
    if spec.name.startswith("Rotor"):
        body.append(
            function_def(
                "plane_of_rotation",
                [
                    class_doc_stmt(PLANE_DOC),
                    return_stmt(
                        call(
                            attribute(
                                call(attribute("self", "r_vector_part"), [constant(2)]),
                                "normalize",
                            ),
                            [],
                        )
                    ),
                ],
                returns=name_ref("MultiVectorBase"),
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
                call(attribute("left", "sandwich"), [name_ref("right")]),
                param_name="x",
                return_type=name_ref("_OperandT"),
                cast=cast_operand,
                param_annotation=name_ref("_OperandT"),
            )
        )
    return [
        class_def(
            spec.name,
            body,
            decorators=[
                attribute("typing", "final"),
                dataclass_decorator(eq=False, slots=True),
            ],
        ),
        *basis_constant_assignments(spec.name, blades),
    ]


def generate_constants(n: int, name: str) -> list[ast.stmt]:
    """Module-level basis constants for one algebra, hand-built as nodes (level C)."""
    nonempty: list[Blade] = [b for b in blades_for_dim(n) if b != ()]
    nodes: list[ast.stmt] = [
        annotated_assign(
            "zero", name_ref(name), call(attribute(name, "from_scalar"), [constant(0)])
        ),
        annotated_assign(
            "one", name_ref(name), call(attribute(name, "from_scalar"), [constant(1)])
        ),
    ]
    b: Blade
    for b in nonempty:
        nodes.append(
            annotated_assign(
                blade_label(b),
                name_ref(name),
                call(
                    attribute(name, "from_blade_dict"),
                    [ast.Dict(keys=[constant(b)], values=[constant(1)])],
                ),
            )
        )
    exported: list[str] = [
        name,
        "Scalar",
        *(s.name for s in graded_specs(n)),
        "zero",
        "one",
    ]
    exported += [blade_label(b) for b in nonempty]
    nodes.append(
        assign("__all__", ast.List(elts=[constant(s) for s in exported], ctx=_LOAD))
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

# AUTO-GENERATED by tools/gen_specialized.py -- do not edit by hand.
# Regenerate with:  python tools/gen_specialized.py
#
# {name}: a specialized, performant representation of 𝒢{_subscript(n)} -- a named-field
# dataclass whose geometric product is the closed form derived from the general
# Gn symbolic product.

from __future__ import annotations

import dataclasses
import typing
from collections.abc import Generator

import numpy as np
import sympy

from gacalc.base import MultiVectorBase, BladeCoef, Coef{operand_import}
from gacalc.gn import Gn
from gacalc.scalar import Scalar


def _coerce(x: MultiVectorBase | Coef, cls: type[MultiVectorBase]) -> MultiVectorBase:
    \"\"\"Coerce a scalar or multivector to ``cls`` (the full type).\"\"\"
    if isinstance(x, MultiVectorBase):
        return cls.from_blade_dict(x.to_blade_dict())
    if isinstance(x, sympy.Expr):
        return cls.from_coef(x)
    return cls.from_scalar(x)
"""


SCALAR_HEADER = """# Copyright (c) 2025-2026 William Emerison Six
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

# AUTO-GENERATED by tools/gen_specialized.py -- do not edit by hand.
# Regenerate with:  python tools/gen_specialized.py
#
# Scalar: the shared grade-0 type used by the graded subtypes of every 𝒢ₙ.

from __future__ import annotations

import dataclasses
import typing

import numpy as np
import sympy

from gacalc.base import MultiVectorBase, BladeCoef, Coef
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
    scalar_nodes: list[ast.stmt] = generate_scalar() + [
        assign("__all__", ast.List(elts=[constant("Scalar")], ctx=_LOAD))
    ]
    scalar_body: str = module_source(inject_region_markers(scalar_nodes))
    scalar_source: str = SCALAR_HEADER + "\n\n" + scalar_body + "\n"
    with open(out_path("scalar.py"), "w") as f:
        f.write(scalar_source)
    written.append(out_path("scalar.py"))
    sys.stdout.write(f"wrote {os.path.normpath(out_path('scalar.py'))}\n")

    n: int
    name: str
    filename: str
    for n, name, filename in ALGEBRAS:
        nodes: list[ast.stmt] = generate_class(n, name)
        spec: TypeSpec
        for spec in graded_specs(n):
            nodes += generate_graded_type(spec, n, name)
        nodes += generate_constants(n, name)
        module_body: str = module_source(inject_region_markers(nodes))
        source: str = header(name, n) + "\n\n" + module_body + "\n"
        with open(out_path(filename), "w") as f:
            f.write(source)
        written.append(out_path(filename))
        sys.stdout.write(f"wrote {os.path.normpath(out_path(filename))}\n")
    ruff_format(written)


if __name__ == "__main__":
    main()
