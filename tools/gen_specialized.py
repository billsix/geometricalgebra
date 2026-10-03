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

"""Generate the specialized per-algebra modules (``g1``/``g2``/``g3``) from ``Gn``.

Read this first to understand how the generator works; the deep, file-by-file
map is ``tasks/reference/code-generator-architecture.md``.

The one idea to hold onto
=========================

``Gn`` (``gacalc/gn.py``) is the slow-but-obviously-correct reference: a
multivector as a plain ``dict`` from blade to coefficient, whose product is
textbook bubble-sort-and-cancel, eagerly ``sympy.simplify``-ing every
coefficient.  It is never optimized -- it is the oracle.

The specialized classes (``G`` and the graded subtypes
``Vector``/``Bivector``/``Versor``/...) are fast because their arithmetic is
pre-computed closed-form code.  The trick is where that code comes from:

    We do NOT parse Gn's source and we do NOT macro-expand it.  We *run* Gn --
    once, on sympy SYMBOLS instead of numbers -- and keep the formula that falls
    out.  Compiling that formula into a concrete method is the whole generator.

That is partial evaluation / symbolic execution (the same idea as a tracing
JIT): running the reference on placeholder inputs specializes it into compiled
code.  Because the formula came straight out of running the reference, the
generated fast path cannot disagree with it -- that is what "provably consistent
with Gn" means, and why a graded product's result *type* is decided at
generation time from the symbolic result, never from a runtime float.

The pipeline
============

::

    Gn  --  the reference (dict-of-blades, eager sympy.simplify, slow)
     |
     |   feed it SYMBOLS, not numbers:
     |      a = Gn({(1,): a_e_1, (2,): a_e_2})
     |      b = Gn({(1,): b_e_1, (2,): b_e_2})
     v
    run Gn's REAL product  a * b   (the unchanged reference code)
     |
     v
    a Gn whose coefficients are now FORMULAS (sympy exprs):
       {():    a_e_1*b_e_1 + a_e_2*b_e_2,      <- scalar part
        (1,2): a_e_1*b_e_2 - a_e_2*b_e_1}      <- bivector part
     |
     |   resolve() the nonzero blades -> a result type
     |             (scalar + bivector  =>  Versor)
     |   sympy.cse() to factor; rewrite  a_e_1 -> self.coeff_e_1
     v
    Python AST nodes  --ast.unparse-->  Vector._geometric_product source
     |
     v
    g2.py   (a gitignored build artifact -- never hand-edited)

The middle step, run live so you can see the formula the generator captures
(read out by key: the union-of-blades dict has no guaranteed order):

    >>> import sympy
    >>> from gacalc.gn import Gn
    >>> a = Gn.from_blade_dict(
    ...     {(1,): sympy.Symbol("a_e_1"), (2,): sympy.Symbol("a_e_2")})
    >>> b = Gn.from_blade_dict(
    ...     {(1,): sympy.Symbol("b_e_1"), (2,): sympy.Symbol("b_e_2")})
    >>> d = (a * b).to_blade_dict()
    >>> d[()]                      # scalar part
    a_e_1*b_e_1 + a_e_2*b_e_2
    >>> d[(1, 2)]                  # bivector part
    a_e_1*b_e_2 - a_e_2*b_e_1

The product of two general 2-D vectors has a scalar part and a bivector part and
nothing else, so ``resolve`` picks the smallest registered type covering those
two blades -- the even subalgebra ``Versor`` -- which is why ``Vector *
Vector`` is typed and built as a ``Versor``.

The three files
===============

- ``tools/gen_specialized.py`` (this file) -- the geometric-algebra layer: the
  type registry + ``resolve``, ``product_result`` (build symbolic operands, run
  the real Gn op, read off the formula), and one builder per emitted construct
  (``generate_scalar`` / ``generate_class`` / ``generate_graded_type`` /
  ``generate_constants``).  ``main()`` writes the three self-contained modules
  so a reader can import just the one they need (``from gacalc.g2 import G``).
- ``tools/astbuild.py`` -- a domain-agnostic node-builder DSL over ``ast``,
  knowing nothing about geometric algebra: it turns the pieces above into AST
  nodes and renders them with ``ast.unparse`` (there is no string-template layer
  -- the AST is the intermediate form).  It also holds the doc-region markers.
- ``tools/check_doc_regions.py`` -- a standalone verifier for those markers.

Golden rule: a correct generator change appears in ``git diff`` as a ``tools/``
diff and NOTHING under ``src/gacalc/`` (the ``g*.py`` are gitignored build
artifacts).  To study the output, run this script and read the real
``src/gacalc/g2.py`` on disk -- never edit it, never reason from memory about it.

Re-run this script by hand when the algebra changes:

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
from collections.abc import Callable, Iterable, Mapping, Sequence
from itertools import chain, combinations
from typing import NamedTuple, cast

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
    dataclass_decorator,
    function_def,
    inject_region_markers,
    isinstance_,
    marker,
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

from gacalc.base import (  # noqa: E402
    Blade,
    BladeCoef,
    MultiVectorBase,
    pseudoscalar_squared_sign,
)
from gacalc.gn import Gn  # noqa: E402

# ==========================================================================
# sympy -> ast bridge
# ==========================================================================


def expr_to_ast(expr: sympy.Expr, rename: Mapping[str, tuple[str, str]]) -> ast.expr:
    """sympy expression -> AST expression with operand symbols as attribute access."""
    tree: ast.expr = parse_expr(sympy.sstr(expr))
    return ast.fix_missing_locations(SymbolToAttr(rename).visit(tree))


# ==========================================================================
# Geometric-algebra domain utilities
# ==========================================================================


def out_path(filename: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "src", "gacalc", filename)


def blades_for_dim(n: int) -> list[Blade]:
    """All 2**n basis blades of 𝒢ₙ in canonical (grade, then index) order."""
    idx: list[int] = list(range(1, n + 1))
    powerset: Iterable[Blade] = chain.from_iterable(
        combinations(idx, r) for r in range(n + 1)
    )
    return sorted(powerset, key=lambda b: (len(b), b))


def blade_label(blade: Blade) -> str:
    """The human/blade label: () -> 'scalar', (1,) -> 'e_1', (1, 2) -> 'e_12'.

    Used for docstrings and the internal cse symbol names (``a_e_1``/``b_e_1``).
    The dataclass *field* that stores a blade's coefficient is ``field_name`` (a
    ``coeff_``-prefixed form), kept distinct so the basis-blade names ``e_1`` ...
    stay free to denote the basis-vector constants on each class.
    """
    return "scalar" if blade == () else "e_" + "".join(str(i) for i in blade)


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
    return () if label == "scalar" else tuple(int(c) for c in label[2:])


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
    sentinel: tuple[int, Blade] = (99, ())
    left: tuple[int, Blade] | None = None
    right: tuple[int, Blade] | None = None
    sym: sympy.Basic
    for sym in term.free_symbols:
        if not isinstance(sym, sympy.Symbol):
            continue
        kind: str
        label: str
        kind, _, label = sym.name.partition("_")
        blade: Blade = blade_of_label(label)
        match kind:
            case "a":
                left = (len(blade), blade)
            case "b":
                right = (len(blade), blade)
            case _:
                raise ValueError(f"unexpected operand symbol {sym.name!r}")
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


DOCSTRINGS: dict[int, str] = {
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
        "the even subalgebra (versor / spinor)"
        if spec.name.startswith("Versor")
        else "the grade-%d (%s) part"
        % (len(spec.blades[0]), grade_words.get(len(spec.blades[0]), "k-vector"))
        if len({len(b) for b in spec.blades}) == 1
        else "a graded part"
    )
    return (
        f"An element of {kind}\n"
        f"    of 𝒢{_subscript(spec.dim)}.  Spanning the basis blades: {labels}.\n\n"
        "    A graded subtype: products dispatch by operand type and return the\n"
        "    grade-correct type (e.g. vector*vector -> the even/Versor type).  "
        "Results\n    that span grades no graded type covers widen to "
        f"{full_name_for(spec.dim)}.\n    AUTO-GENERATED by tools/gen_specialized.py."
    )


def full_name_for(dim: int) -> str:
    return "G"


def scalar_doc(n: int) -> str:
    """Docstring for the per-algebra ``ScalarN`` grade-0 type."""
    return (
        f"The grade-0 (scalar) type of 𝒢{_subscript(n)}.\n"
        "\n"
        "    ``ScalarN * x`` scales ``x`` and returns x's type; pure-scalar\n"
        "    product results (e.g. Bivector * Bivector) land here.  One type per\n"
        "    algebra so ``dual`` is precise (grade 0 -> the pseudoscalar).\n"
        "    AUTO-GENERATED by tools/gen_specialized.py."
    )


PLANE_DOC: str = (
    "The unit bivector (2-blade) this versor rotates in.\n"
    "\n"
    "        A rotor is ``cos(t/2) - sin(t/2) * B`` for a unit bivector B --\n"
    "        the oriented plane of rotation.  This returns B, the normalized\n"
    "        bivector part.  In 2D that 2-blade is also the pseudoscalar; in 3D\n"
    "        it is a bivector plane, not the trivector.  Undefined for the\n"
    "        identity rotor (no rotation)."
)


def doc_expr(doc: str, indent: str = "        ") -> ast.Expr:
    """A docstring statement for ``doc``, re-indented to ``indent`` per line.

    The Constant value reproduces what the string generator emitted (a leading
    newline + ``indent``-prefixed lines), so the parsed AST matches for parity
    and ``ast.unparse`` renders a properly-indented triple-quoted docstring.
    """
    body: str = "\n".join(f"{indent}{line}".rstrip() for line in doc.splitlines())
    return ast.Expr(value=constant(f"\n{body}\n{indent}"))


def method_doc_stmts(method_name: str, indent: str = "        ") -> list[ast.stmt]:
    """The base method's docstring as a leading ``Expr(Constant)``, or ``[]``."""
    member: object | None = getattr(MultiVectorBase, method_name, None)
    doc: str | None = inspect.getdoc(member) if member is not None else None
    if not doc:
        return []
    return [doc_expr(doc, indent)]


def class_doc_stmt(text: str) -> ast.Expr:
    """A class docstring statement -- ``text`` used verbatim."""
    return ast.Expr(value=constant(text))


# --------------------------------------------------------------------------
# Method docstrings on the generated classes
# --------------------------------------------------------------------------
# Every generated method should carry a docstring so the class is
# self-documenting on disk (autodoc also inherits the base docstring via
# ``inspect.getdoc``, but the generated source itself would otherwise be bare).
# Policy, applied by ``inject_method_docstrings`` after each class is built:
#
#   * ``@overload`` stubs are left bare (``...``): they never render (autodoc
#     uses the implementation) and a docstring there is noise.
#   * For the dev dimensions (1--3) a method may get a *specialized*, grade-aware
#     docstring from ``CUSTOM_METHOD_DOCS`` below -- keyed by (role, method),
#     with ``role`` the class's grade identity ("scalar"/"vector"/"bivector"/
#     "trivector"/"versor"/"odd"/"full") or "*" for every role.  These are the
#     docstrings worth writing by hand because grade narrows the behaviour
#     (reversing a vector is a no-op; a bivector reverses to its negative; ...).
#   * Otherwise -- and always for dims >= 4 (release-only, niche) -- the method
#     copies the *generic* base docstring (``MultiVectorBase``/``Gn``), the same
#     text ``inspect.getdoc`` would surface anyway.  A method with no such
#     counterpart and no custom entry is left bare.
#
# The table is a plain dict (deterministic lookup), so ``make check-generated``
# still sees byte-identical output across two runs.
_CUSTOM_DOC_DIMS: frozenset[int] = frozenset({1, 2, 3})

# A custom-docstring entry: literal text, or a ``(role, n) -> str`` callable for
# grade-/dimension-aware wording (so one function serves every role and the doctest
# example fits the algebra it lands in).
DocEntry = str | Callable[[str, int], str]


def _bivector_dual_doc(role: str, n: int) -> str:
    """Grade-2 ``dual`` -- dimension-dependent (𝒢₂: bivector→scalar; 𝒢₃:
    bivector→the vector normal to its plane)."""
    if n == 2:
        return (
            "Dual  B* = B / i  in 𝒢₂: the dual of a bivector is a scalar (the\n"
            "bivector IS the pseudoscalar here, so its dual is a plain number).\n"
            "\n"
            "Returns:\n"
            "    Scalar: the dual of the bivector (a scalar in 𝒢₂).\n"
            "\n"
            "Example:\n"
            "    >>> (1 * Bivector.e_12).dual() == Scalar.from_scalar(1)\n"
            "    True"
        )
    return (
        "Dual  B* = B / i  in 𝒢₃: the dual of a bivector is the VECTOR normal to\n"
        "its plane -- the e₁e₂ plane duals to e₃.\n"
        "\n"
        "Returns:\n"
        "    Vector: the vector normal to the bivector's plane (𝒢₃).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Bivector.e_12).dual() == 1 * Vector.e_3\n"
        "    True"
    )


def _vector_dual_doc(role: str, n: int) -> str:
    """Grade-1 ``dual`` -- dimension-dependent (𝒢₁: →scalar; 𝒢₂: →the
    perpendicular vector, a 90° turn; 𝒢₃: →the plane ⟂ to the vector)."""
    if n == 1:
        return (
            "Dual of a vector in 𝒢₁ is a scalar.\n"
            "\n"
            "Returns:\n"
            "    Scalar: the dual (a scalar in 𝒢₁).\n"
            "\n"
            "Example:\n"
            "    >>> (1 * Vector.e_1).dual() == Scalar.from_scalar(1)\n"
            "    True"
        )
    if n == 2:
        return (
            "Dual of a vector in 𝒢₂ is the perpendicular vector -- dualizing is a\n"
            "quarter turn:  e₁ → −e₂.\n"
            "\n"
            "Returns:\n"
            "    Vector: the perpendicular vector (a quarter turn).\n"
            "\n"
            "Example:\n"
            "    >>> (1 * Vector.e_1).dual() == -1 * Vector.e_2\n"
            "    True"
        )
    return (
        "Dual of a vector in 𝒢₃ is the BIVECTOR of the plane perpendicular to it\n"
        "(its normal plane):  e₁ → −e₂e₃.\n"
        "\n"
        "Returns:\n"
        "    Bivector: the bivector of the plane perpendicular to the vector.\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Vector.e_1).dual() == -1 * Bivector.e_23\n"
        "    True"
    )


def _vector_outer_doc(role: str, n: int) -> str:
    """Grade-1 ∧ grade-1 -- 0 in 𝒢₁ (all vectors parallel), else the bivector
    spanning the two vectors."""
    if n == 1:
        return (
            "Outer (wedge) product.  In 𝒢₁ any two vectors are parallel, so their\n"
            "wedge is 0.\n"
            "\n"
            "Args:\n"
            "    rhs: the other vector.\n"
            "\n"
            "Returns:\n"
            "    Scalar: the zero bivector, which in 𝒢₁ is the scalar 0.\n"
            "\n"
            "Example:\n"
            "    >>> (1 * Vector.e_1) ^ (1 * Vector.e_1) == Scalar.zero()\n"
            "    True"
        )
    return (
        "Outer (wedge) product of two vectors: the BIVECTOR they span -- the\n"
        "oriented area of their parallelogram.  a ∧ a = 0 (parallel).\n"
        "\n"
        "Args:\n"
        "    rhs: the other vector.\n"
        "\n"
        "Returns:\n"
        "    Bivector: the oriented plane the two vectors span.\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Vector.e_1) ^ (1 * Vector.e_2) == 1 * Bivector.e_12\n"
        "    True"
    )


def _vector_i_doc(role: str, n: int) -> str:
    """Grade-1 ``i`` classmethod -- needs a 2-D plane, so 𝒢₁ has no example."""
    if n == 1:
        return (
            "The unit bivector î (î² = −1) of the plane of two vectors; a\n"
            "classmethod.  𝒢₁ is 1-dimensional, so it has no such plane.\n"
            "\n"
            "Args:\n"
            "    a: the first vector spanning the plane.\n"
            "    b: the second vector spanning the plane.\n"
            "\n"
            "Returns:\n"
            "    Bivector: the unit bivector of the a-b plane (no such plane in 𝒢₁).\n"
            "\n"
            "Raises:\n"
            "    ValueError: if a and b are parallel (they span no plane)."
        )
    return (
        "The unit bivector of the plane of two vectors (î² = −1); a classmethod.\n"
        "\n"
        "Args:\n"
        "    a: the first vector spanning the plane.\n"
        "    b: the second vector spanning the plane.\n"
        "\n"
        "Returns:\n"
        "    Bivector: the unit bivector î of the a-b plane (î² = −1).\n"
        "\n"
        "Raises:\n"
        "    ValueError: if a and b are parallel (they span no plane).\n"
        "\n"
        "Example:\n"
        "    >>> Vector.i(Vector.e_1, Vector.e_2) == 1 * Bivector.e_12\n"
        "    True"
    )


def _vector_proj_doc(role: str, n: int) -> str:
    """Grade-1 ``projected_onto`` -- the parallel component."""
    if n == 1:
        return (
            "The component of this vector ALONG another (the parallel part).\n"
            "\n"
            "Args:\n"
            "    onto: the vector (or blade) to project onto.\n"
            "\n"
            "Returns:\n"
            "    Vector: the component of this vector along ``onto``.\n"
            "\n"
            "Example:\n"
            "    >>> (3 * Vector.e_1).projected_onto(Vector.e_1) == 3 * Vector.e_1\n"
            "    True"
        )
    return (
        "The component of this vector ALONG another (the parallel part).\n"
        "\n"
        "Args:\n"
        "    onto: the vector (or blade) to project onto.\n"
        "\n"
        "Returns:\n"
        "    Vector: the component of this vector along ``onto``.\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Vector.e_1 + 1 * Vector.e_2).projected_onto(Vector.e_1) == Vector.e_1\n"
        "    True"
    )


def _vector_rej_doc(role: str, n: int) -> str:
    """Grade-1 ``rejected_away_from`` -- the perpendicular component."""
    if n == 1:
        return (
            "The component of this vector PERPENDICULAR to another (the\n"
            "rejection).  In 𝒢₁ every vector is parallel, so the rejection is 0.\n"
            "\n"
            "Args:\n"
            "    away_from: the vector (or blade) to reject from.\n"
            "\n"
            "Returns:\n"
            "    Vector: the component of this vector perpendicular to ``away_from``.\n"
            "\n"
            "Example:\n"
            "    >>> (3 * Vector.e_1).rejected_away_from(Vector.e_1) == Vector.zero()\n"
            "    True"
        )
    return (
        "The component of this vector PERPENDICULAR to another (the rejection).\n"
        "\n"
        "Args:\n"
        "    away_from: the vector (or blade) to reject from.\n"
        "\n"
        "Returns:\n"
        "    Vector: the component of this vector perpendicular to ``away_from``.\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Vector.e_1 + 1 * Vector.e_2).rejected_away_from(Vector.e_1) == Vector.e_2\n"
        "    True"
    )


def _scalar_dual_doc(role: str, n: int) -> str:
    """Grade-0 ``dual`` -- a scalar duals to the top-grade blade (× the
    pseudoscalar): a vector in 𝒢₁, a bivector in 𝒢₂, a trivector in 𝒢₃."""
    top: str = {
        1: "1 * Vector.e_1",
        2: "-1 * Bivector.e_12",
        3: "-1 * Trivector.e_123",
    }[n]
    kind: str = {1: "vector", 2: "bivector", 3: "trivector"}[n]
    return (
        f"Dual  s* = s / i  in 𝒢{_subscript(n)}: a scalar duals to the top-grade\n"
        f"blade (the {kind}), i.e. the scalar times the pseudoscalar.\n"
        "\n"
        "Returns:\n"
        f"    the top-grade blade (the {kind}): the scalar times the pseudoscalar.\n"
        "\n"
        "Example:\n"
        f"    >>> Scalar.from_scalar(1).dual() == {top}\n"
        "    True"
    )


# role, method -> a DocEntry.  A ``role|method`` key wins over the role-agnostic
# ``*|method``; both are consulted by ``custom_method_doc``.
CUSTOM_METHOD_DOCS: dict[str, DocEntry] = {
    # ``__eq__`` is dataclass/representation-specific, so it has no hand-written
    # base counterpart -- give it a one-liner rather than copying object's.
    "*|__eq__": (
        "Equality  A == B.  Exact for plain-number coefficients; symbolic\n"
        "coefficients compare via ``sympy.simplify`` (see ``base._coef_eq``).\n"
        "\n"
        "Args:\n"
        "    other: the value to compare against.\n"
        "\n"
        "Returns:\n"
        "    bool: ``True`` iff the two multivectors are equal (``NotImplemented``\n"
        "    for a non-multivector, so a bare number never compares equal)."
    ),
    # Reflected subtraction: ``number - A``.  Generated-only (the base has
    # ``__sub__`` but no ``__rsub__``), so there is nothing to copy.
    "*|__rsub__": (
        "Reflected difference  (number) - A  =  -A + number.\n"
        "\n"
        "Args:\n"
        "    lhs: the bare number on the left.\n"
        "\n"
        "Returns:\n"
        "    the difference ``lhs - self``."
    ),
    # ``reverse`` -- the flagship grade-specialized docstrings: reversion is the
    # identity on grades 0/1 and a sign flip on grades 2/3, so the generic base
    # text ("sign (−1)^(r(r−1)/2)") is far less useful than the per-grade fact.
    "scalar|reverse": (
        "Reverse  Ã  of a scalar is the scalar unchanged (grade 0 is fixed by\n"
        "reversion).\n"
        "\n"
        "Returns:\n"
        "    Scalar: the scalar unchanged."
    ),
    "vector|reverse": (
        "Reverse  Ã  of a vector is the vector itself: reversing a single vector\n"
        "factor is a no-op (the grade-1 reversion sign is +1).\n"
        "\n"
        "Returns:\n"
        "    Vector: the vector unchanged.\n"
        "\n"
        "Example:\n"
        "    >>> v: Vector = 3 * Vector.e_1\n"
        "    >>> v.reverse() == v\n"
        "    True"
    ),
    "bivector|reverse": (
        "Reverse  B̃  of a bivector negates it,  B̃ = −B  (the grade-2 reversion\n"
        "sign is −1).  This sign flip is what makes a versor's reverse invert it.\n"
        "\n"
        "Returns:\n"
        "    Bivector: the negated bivector  B̃ = −B.\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Bivector.e_12).reverse() == -1 * Bivector.e_12\n"
        "    True"
    ),
    "trivector|reverse": (
        "Reverse of a trivector negates it (the grade-3 reversion sign is −1).\n"
        "\n"
        "Returns:\n"
        "    Trivector: the negated trivector.\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Trivector.e_123).reverse() == -1 * Trivector.e_123\n"
        "    True"
    ),
    "versor|reverse": (
        "Reverse  R̃  of a versor keeps the scalar part and negates the bivector\n"
        "part.  For a unit rotor  R̃  is its inverse, so  R R̃ = 1  -- reversing a\n"
        "rotor undoes its rotation.\n"
        "\n"
        "Returns:\n"
        "    Versor: the reverse (scalar part kept, bivector part negated).\n"
        "\n"
        "Example:\n"
        "    >>> R: Versor = (1 * Bivector.e_12).exp()\n"
        "    >>> R * R.reverse() == Versor.from_scalar(1)\n"
        "    True"
    ),
    "odd|reverse": (
        "Reverse of an odd multivector (grades {1, 3} in 𝒢₃): the vector (grade-1)\n"
        "part is unchanged and the trivector (grade-3) part is negated.\n"
        "\n"
        "Returns:\n"
        "    Odd_3: the reverse (grade-1 part kept, grade-3 part negated)."
    ),
    # ------------------------------------------------------------------
    # Bivector (grade 2) -- the oriented plane element; squares to −1, so it
    # is the imaginary that generates rotations.  Present in 𝒢₂ and 𝒢₃.
    # ------------------------------------------------------------------
    "bivector|__add__": (
        "Sum of two bivectors, added plane-component by plane-component; the\n"
        "result is again a bivector (grade 2 is closed under addition).\n"
        "\n"
        "Args:\n"
        "    rhs: the bivector to add.\n"
        "\n"
        "Returns:\n"
        "    Bivector: the component-wise sum.\n"
        "\n"
        "Example:\n"
        "    >>> 1 * Bivector.e_12 + 1 * Bivector.e_12 == 2 * Bivector.e_12\n"
        "    True"
    ),
    "bivector|__sub__": (
        "Difference of two bivectors, component-wise (still a bivector).\n"
        "\n"
        "Args:\n"
        "    rhs: the bivector to subtract.\n"
        "\n"
        "Returns:\n"
        "    Bivector: the component-wise difference."
    ),
    "bivector|__neg__": (
        "Negation -- reverses the orientation of the plane (every component\n"
        "sign-flipped).\n"
        "\n"
        "Returns:\n"
        "    Bivector: the negated bivector.\n"
        "\n"
        "Example:\n"
        "    >>> -(2 * Bivector.e_12) == -2 * Bivector.e_12\n"
        "    True"
    ),
    "bivector|__mul__": (
        "Geometric product.  A unit bivector squares to −1, so a bivector behaves\n"
        "like the imaginary  i  -- this is what lets it generate rotations.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the geometric product (a scalar for two collinear unit bivectors;\n"
        "    a versor in general).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Bivector.e_12) * (1 * Bivector.e_12) == Scalar.from_scalar(-1)\n"
        "    True"
    ),
    "bivector|_geometric_product": (
        "The geometric-product primitive (use the ``*`` operator).  A unit\n"
        "bivector squares to −1.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the geometric product ``self * rhs``."
    ),
    "bivector|dot": (
        "Inner product of two bivectors -- a scalar.  For a unit bivector,\n"
        "B · B = −1 (the dot carries the same −1 as the square).\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the inner product (a scalar).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Bivector.e_12).dot(1 * Bivector.e_12) == Scalar.from_scalar(-1)\n"
        "    True"
    ),
    "bivector|inner_product": (
        "Inner product of two bivectors -- a scalar; B · B = −1 for a unit\n"
        "bivector.  A spelling of ``dot``.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the inner product (a scalar)."
    ),
    "bivector|left_contraction": (
        "Left contraction  B ⌋ C  (the ``<`` operator).  For two unit bivectors\n"
        "in the same plane it is the scalar −1.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the left contraction (a scalar for two bivectors).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Bivector.e_12).left_contraction(1 * Bivector.e_12) == Scalar.from_scalar(-1)\n"
        "    True"
    ),
    "bivector|right_contraction": (
        "Right contraction  B ⌊ C  (the ``>`` operator); grade |C|−|B|.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the right contraction (grade |C|−|B|)."
    ),
    "bivector|outer_product": (
        "Outer (wedge) product.  A bivector wedged with another bivector is 0 --\n"
        "grade 2 + 2 = 4 exceeds the dimension of 𝒢₂/𝒢₃.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Scalar: 0 (grade 4 exceeds the dimension of 𝒢₂/𝒢₃).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Bivector.e_12) ^ (1 * Bivector.e_12) == Scalar.zero()\n"
        "    True"
    ),
    "bivector|wedge": (
        "Outer (wedge) product; a bivector ∧ a bivector is 0 in 𝒢₂/𝒢₃.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the outer product (0 for two bivectors in 𝒢₂/𝒢₃)."
    ),
    "bivector|__xor__": (
        "Outer (wedge) product operator ``^``; see ``wedge``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the outer product ``self ^ other``."
    ),
    "bivector|dual": _bivector_dual_doc,
    "bivector|even_part": (
        "A bivector has even grade (2), so its even part is the whole thing.\n"
        "\n"
        "Returns:\n"
        "    Bivector: the bivector itself.\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Bivector.e_12).even_part() == 2 * Bivector.e_12\n"
        "    True"
    ),
    "bivector|odd_part": (
        "A bivector has no odd-grade part, so its odd part is 0.\n"
        "\n"
        "Returns:\n"
        "    Scalar: 0 (a bivector has no odd-grade part).\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Bivector.e_12).odd_part() == Scalar.zero()\n"
        "    True"
    ),
    "bivector|scalar_part": (
        "The scalar (grade-0) part of a bivector is 0.\n"
        "\n"
        "Returns:\n"
        "    Coef: 0 (a bivector has no scalar part).\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Bivector.e_12).scalar_part()\n"
        "    0"
    ),
    "bivector|r_vector_part": (
        "The grade-r part.  A bivector is pure grade 2, so r=2 gives it back and\n"
        "every other grade is 0.\n"
        "\n"
        "Args:\n"
        "    r: the grade to extract.\n"
        "\n"
        "Returns:\n"
        "    Bivector: the grade-``r`` part (the bivector itself for r=2, else 0).\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Bivector.e_12).r_vector_part(2) == 2 * Bivector.e_12\n"
        "    True"
    ),
    "bivector|grades": (
        "A nonzero bivector is homogeneous of grade 2.\n"
        "\n"
        "Returns:\n"
        "    list[int]: ``[2]`` for a nonzero bivector.\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Bivector.e_12).grades()\n"
        "    [2]"
    ),
    "bivector|magnitude_squared": (
        "Squared magnitude  |B|²  -- the sum of squared plane components.\n"
        "\n"
        "Returns:\n"
        "    Coef: the squared magnitude.\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Bivector.e_12).magnitude_squared()\n"
        "    4"
    ),
    "bivector|exp": (
        "Exponential of a bivector IS a rotor:  exp(B) = cos|B| + sin|B| B̂.\n"
        "The zero bivector exponentiates to the identity rotor 1.\n"
        "\n"
        "Returns:\n"
        "    Versor: the rotor cos|B| + sin|B| B̂.\n"
        "\n"
        "Example:\n"
        "    >>> (0 * Bivector.e_12).exp() == Versor.from_scalar(1)\n"
        "    True"
    ),
    "bivector|i": (
        "The unit bivector  î = B / |B|  of this plane (î² = −1); already unit for\n"
        "a basis blade like e₁e₂.  This is the plane you feed a versor / ``exp``.\n"
        "\n"
        "Returns:\n"
        "    Bivector: the unit bivector î of this plane (î² = −1).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Bivector.e_12).i() == 1 * Bivector.e_12\n"
        "    True"
    ),
    "bivector|__iter__": (
        "Iterating a bivector yields its plane-component values in blade order\n"
        "(one value in 𝒢₂; the e₁e₂, e₁e₃, e₂e₃ components in 𝒢₃).\n"
        "\n"
        "Yields:\n"
        "    Coef: each plane-component value, in blade order."
    ),
    "bivector|isclose": (
        "Numeric near-equality of two bivectors, component-wise (see the base\n"
        "``isclose``).\n"
        "\n"
        "Args:\n"
        "    other: the bivector to compare against.\n"
        "\n"
        "Returns:\n"
        "    bool: ``True`` iff every component is within tolerance."
    ),
    "bivector|from_blade_dict": (
        "Build a bivector from a blade→coefficient dict (only grade-2 blades\n"
        "kept).\n"
        "\n"
        "Args:\n"
        "    blade_coef: a canonical blade -> coefficient mapping.\n"
        "\n"
        "Returns:\n"
        "    Bivector: a bivector holding the grade-2 coefficients."
    ),
    "bivector|to_blade_dict": (
        "This bivector as a blade→coefficient dict (grade-2 blades only).\n"
        "\n"
        "Returns:\n"
        "    BladeCoef: the grade-2 blade -> coefficient mapping."
    ),
    "bivector|__lt__": (
        "Left contraction operator ``<``; see ``left_contraction``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the left contraction ``self < other``."
    ),
    "bivector|__gt__": (
        "Right contraction operator ``>``; see ``right_contraction``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the right contraction ``self > other``."
    ),
    "bivector|__radd__": (
        "Reflected sum  (number) + B  -- builds the versor  number + B.\n"
        "\n"
        "Args:\n"
        "    lhs: the bare number on the left.\n"
        "\n"
        "Returns:\n"
        "    Versor: the versor ``lhs + B``."
    ),
    "bivector|__rmul__": (
        "Reflected product  (number) * B  -- scales the bivector.\n"
        "\n"
        "Args:\n"
        "    lhs: the bare number on the left.\n"
        "\n"
        "Returns:\n"
        "    Bivector: the scaled bivector."
    ),
    # ------------------------------------------------------------------
    # Scalar (grade 0) -- a plain number living in the algebra.  Present in
    # every dimension.
    # ------------------------------------------------------------------
    "scalar|__add__": (
        "Sum of two scalars -- ordinary addition (still a scalar).\n"
        "\n"
        "Args:\n"
        "    rhs: the scalar to add.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the sum.\n"
        "\n"
        "Example:\n"
        "    >>> Scalar.from_scalar(2) + Scalar.from_scalar(3) == Scalar.from_scalar(5)\n"
        "    True"
    ),
    "scalar|__sub__": (
        "Difference of two scalars -- ordinary subtraction.\n"
        "\n"
        "Args:\n"
        "    rhs: the scalar to subtract.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the difference."
    ),
    "scalar|__neg__": (
        "Negation -- ordinary sign change.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the negated scalar.\n"
        "\n"
        "Example:\n"
        "    >>> -Scalar.from_scalar(3) == Scalar.from_scalar(-3)\n"
        "    True"
    ),
    "scalar|__mul__": (
        "Geometric product of two scalars -- ordinary multiplication (the scalar\n"
        "is the centre of the algebra: it commutes with everything).\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the product -- another scalar times a scalar, or the operand scaled.\n"
        "\n"
        "Example:\n"
        "    >>> Scalar.from_scalar(2) * Scalar.from_scalar(3) == Scalar.from_scalar(6)\n"
        "    True"
    ),
    "scalar|_geometric_product": (
        "The geometric-product primitive -- for scalars, plain multiplication.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the product ``self * rhs``."
    ),
    "scalar|dot": (
        "Inner (dot) product.  The Hestenes dot EXCLUDES grade 0, so the dot of\n"
        "two scalars is 0 (use ``*`` to multiply scalars).\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Scalar: 0 (the Hestenes dot excludes grade 0).\n"
        "\n"
        "Example:\n"
        "    >>> Scalar.from_scalar(2).dot(Scalar.from_scalar(3)) == Scalar.zero()\n"
        "    True"
    ),
    "scalar|inner_product": (
        "Hestenes inner product; excludes grade 0, so it is 0 on scalars (see\n"
        "``dot``).\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Scalar: 0 on scalars."
    ),
    "scalar|outer_product": (
        "Outer (wedge) product.  A scalar wedges by ordinary multiplication (it\n"
        "adds no grade), so s ∧ t = s·t.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the wedge -- a scalar adds no grade, so this scales ``rhs``.\n"
        "\n"
        "Example:\n"
        "    >>> Scalar.from_scalar(2).wedge(Scalar.from_scalar(3)) == Scalar.from_scalar(6)\n"
        "    True"
    ),
    "scalar|wedge": (
        "Outer product; a scalar adds no grade, so s ∧ t is ordinary\n"
        "multiplication.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the wedge (scalar multiplication)."
    ),
    "scalar|__xor__": (
        "Outer (wedge) product operator ``^``; on scalars it is multiplication.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the outer product ``self ^ other``."
    ),
    "scalar|left_contraction": (
        "Left contraction  s ⌋ x  -- a scalar contracts as plain scalar\n"
        "multiplication.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the operand scaled by this scalar."
    ),
    "scalar|right_contraction": (
        "Right contraction  x ⌊ s  -- plain scalar multiplication.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the operand scaled by this scalar."
    ),
    "scalar|dual": _scalar_dual_doc,
    "scalar|even_part": (
        "A scalar is even (grade 0), so its even part is itself.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the scalar itself.\n"
        "\n"
        "Example:\n"
        "    >>> Scalar.from_scalar(3).even_part() == Scalar.from_scalar(3)\n"
        "    True"
    ),
    "scalar|odd_part": (
        "A scalar has no odd part, so it is 0.\n"
        "\n"
        "Returns:\n"
        "    Scalar: 0 (a scalar has no odd part).\n"
        "\n"
        "Example:\n"
        "    >>> Scalar.from_scalar(3).odd_part() == Scalar.zero()\n"
        "    True"
    ),
    "scalar|scalar_part": (
        "The scalar part of a scalar is its own value (a plain number).\n"
        "\n"
        "Returns:\n"
        "    Coef: the scalar's own value.\n"
        "\n"
        "Example:\n"
        "    >>> Scalar.from_scalar(3).scalar_part()\n"
        "    3"
    ),
    "scalar|r_vector_part": (
        "The grade-r part.  A scalar is pure grade 0, so r=0 gives it back and any\n"
        "other grade is 0.\n"
        "\n"
        "Args:\n"
        "    r: the grade to extract.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the grade-``r`` part (the scalar itself for r=0, else 0).\n"
        "\n"
        "Example:\n"
        "    >>> Scalar.from_scalar(3).r_vector_part(0) == Scalar.from_scalar(3)\n"
        "    True"
    ),
    "scalar|grades": (
        "A nonzero scalar is homogeneous of grade 0.\n"
        "\n"
        "Returns:\n"
        "    list[int]: ``[0]`` for a nonzero scalar.\n"
        "\n"
        "Example:\n"
        "    >>> Scalar.from_scalar(3).grades()\n"
        "    [0]"
    ),
    "scalar|__iter__": (
        "Iterating a scalar yields its single grade-0 component.\n"
        "\n"
        "Yields:\n"
        "    Coef: the single grade-0 component value."
    ),
    "scalar|isclose": (
        "Numeric near-equality of two scalars (see the base ``isclose``).\n"
        "\n"
        "Args:\n"
        "    other: the scalar to compare against.\n"
        "\n"
        "Returns:\n"
        "    bool: ``True`` iff the two are within tolerance."
    ),
    "scalar|from_blade_dict": (
        "Build a scalar from a blade→coefficient dict (only the grade-0 blade\n"
        "kept).\n"
        "\n"
        "Args:\n"
        "    blade_coef: a canonical blade -> coefficient mapping.\n"
        "\n"
        "Returns:\n"
        "    Scalar: a scalar holding the grade-0 coefficient."
    ),
    "scalar|to_blade_dict": (
        "This scalar as a blade→coefficient dict (the scalar blade only).\n"
        "\n"
        "Returns:\n"
        "    BladeCoef: the ``{(): value}`` mapping."
    ),
    "scalar|__lt__": (
        "Left contraction operator ``<``; see ``left_contraction``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the left contraction ``self < other``."
    ),
    "scalar|__gt__": (
        "Right contraction operator ``>``; see ``right_contraction``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the right contraction ``self > other``."
    ),
    "scalar|__radd__": (
        "Reflected sum  (number) + s  -- ordinary addition.\n"
        "\n"
        "Args:\n"
        "    lhs: the bare number on the left.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the sum ``lhs + s``."
    ),
    "scalar|__rmul__": (
        "Reflected product  (number) * s  -- ordinary multiplication.\n"
        "\n"
        "Args:\n"
        "    lhs: the bare number on the left.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the scaled scalar."
    ),
    # ------------------------------------------------------------------
    # Vector (grade 1) -- the arrow students already know.  Present in every
    # dimension; the multi-component examples are dimension-aware.
    # ------------------------------------------------------------------
    "vector|__add__": (
        "Sum of two vectors -- added coordinate-wise, the usual tip-to-tail\n"
        "addition (still a vector).\n"
        "\n"
        "Args:\n"
        "    rhs: the vector to add.\n"
        "\n"
        "Returns:\n"
        "    Vector: the coordinate-wise sum.\n"
        "\n"
        "Example:\n"
        "    >>> 1 * Vector.e_1 + 1 * Vector.e_1 == 2 * Vector.e_1\n"
        "    True"
    ),
    "vector|__sub__": (
        "Difference of two vectors, coordinate-wise (still a vector).\n"
        "\n"
        "Args:\n"
        "    rhs: the vector to subtract.\n"
        "\n"
        "Returns:\n"
        "    Vector: the coordinate-wise difference."
    ),
    "vector|__neg__": (
        "Negation -- the arrow reversed (every coordinate sign-flipped).\n"
        "\n"
        "Returns:\n"
        "    Vector: the reversed vector.\n"
        "\n"
        "Example:\n"
        "    >>> -(2 * Vector.e_1) == -2 * Vector.e_1\n"
        "    True"
    ),
    "vector|__mul__": (
        "Geometric product of two vectors  a b = a·b + a∧b  -- a scalar (their\n"
        "dot) plus a bivector (their wedge).  A unit vector squares to 1.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the geometric product a·b + a∧b (a scalar for parallel unit\n"
        "    vectors; a versor in general).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Vector.e_1) * (1 * Vector.e_1) == Scalar.from_scalar(1)\n"
        "    True"
    ),
    "vector|_geometric_product": (
        "The geometric-product primitive (use ``*``):  a b = a·b + a∧b.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the geometric product ``self * rhs``."
    ),
    "vector|dot": (
        "Inner (dot) product of two vectors -- the scalar  a·b = |a||b|cos θ.\n"
        "A unit vector dotted with itself is 1; perpendicular vectors give 0.\n"
        "\n"
        "Args:\n"
        "    rhs: the other vector.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the dot product  a·b = |a||b|cos θ.\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Vector.e_1).dot(1 * Vector.e_1) == Scalar.from_scalar(1)\n"
        "    True"
    ),
    "vector|inner_product": (
        "The dot product of two vectors,  a·b = |a||b|cos θ (see ``dot``).\n"
        "\n"
        "Args:\n"
        "    rhs: the other vector.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the dot product."
    ),
    "vector|outer_product": _vector_outer_doc,
    "vector|wedge": _vector_outer_doc,
    "vector|__xor__": (
        "Outer (wedge) product operator ``^`` -- the bivector two vectors span.\n"
        "\n"
        "Args:\n"
        "    other: the other vector.\n"
        "\n"
        "Returns:\n"
        "    Bivector: the oriented plane the two vectors span."
    ),
    "vector|left_contraction": (
        "Left contraction  a ⌋ B  (the ``<`` operator); lowers B's grade by 1.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the left contraction (grade |B|−1)."
    ),
    "vector|right_contraction": (
        "Right contraction  a ⌊ b  (the ``>`` operator); for two vectors, the\n"
        "dot.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the right contraction (the dot for two vectors)."
    ),
    "vector|dual": _vector_dual_doc,
    "vector|even_part": (
        "A vector has odd grade (1), so it has NO even part.\n"
        "\n"
        "Returns:\n"
        "    Scalar: 0 (a vector has no even-grade part).\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Vector.e_1).even_part() == Scalar.zero()\n"
        "    True"
    ),
    "vector|odd_part": (
        "A vector is odd (grade 1), so its odd part is the whole thing.\n"
        "\n"
        "Returns:\n"
        "    Vector: the vector itself.\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Vector.e_1).odd_part() == 2 * Vector.e_1\n"
        "    True"
    ),
    "vector|scalar_part": (
        "The scalar (grade-0) part of a vector is 0.\n"
        "\n"
        "Returns:\n"
        "    Coef: 0 (a vector has no scalar part).\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Vector.e_1).scalar_part()\n"
        "    0"
    ),
    "vector|r_vector_part": (
        "The grade-r part.  A vector is pure grade 1, so r=1 gives it back and any\n"
        "other grade is 0.\n"
        "\n"
        "Args:\n"
        "    r: the grade to extract.\n"
        "\n"
        "Returns:\n"
        "    Vector: the grade-``r`` part (the vector itself for r=1, else 0).\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Vector.e_1).r_vector_part(1) == 2 * Vector.e_1\n"
        "    True"
    ),
    "vector|grades": (
        "A nonzero vector is homogeneous of grade 1.\n"
        "\n"
        "Returns:\n"
        "    list[int]: ``[1]`` for a nonzero vector.\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Vector.e_1).grades()\n"
        "    [1]"
    ),
    "vector|magnitude_squared": (
        "Squared length  |a|² = a·a  -- the sum of squared coordinates.\n"
        "\n"
        "Returns:\n"
        "    Coef: the squared length.\n"
        "\n"
        "Example:\n"
        "    >>> (3 * Vector.e_1).magnitude_squared()\n"
        "    9"
    ),
    "vector|i": _vector_i_doc,
    "vector|bivector_from_vectors": (
        "The (unnormalized) bivector  a ∧ b  spanning two vectors -- their\n"
        "oriented area; a classmethod.  Normalize with ``i`` for a unit plane.\n"
        "\n"
        "Args:\n"
        "    a: the first vector.\n"
        "    b: the second vector.\n"
        "\n"
        "Returns:\n"
        "    Bivector: the oriented plane  a ∧ b  (zero if parallel)."
    ),
    "vector|versor_from_vectors": (
        "The versor that rotates ``a`` to ``b`` in the a-b plane (a classmethod);\n"
        "apply it with ``sandwich``.  Express rotations via factories, not by\n"
        "hand.\n"
        "\n"
        "Args:\n"
        "    from_vector: the vector to rotate from.\n"
        "    to_vector: the vector to rotate toward.\n"
        "\n"
        "Returns:\n"
        "    Versor: the versor taking ``from_vector`` toward ``to_vector``."
    ),
    "vector|cross": (
        "Cross product (𝒢₃ only)  a × b = (a ∧ b) I₃⁻¹ -- the vector dual of the\n"
        "wedge, right-handed:  e₁ × e₂ = e₃.\n"
        "\n"
        "Args:\n"
        "    other: the other vector.\n"
        "\n"
        "Returns:\n"
        "    Vector: the cross product a × b.\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Vector.e_1).cross(1 * Vector.e_2) == 1 * Vector.e_3\n"
        "    True"
    ),
    "vector|rotate_90_degrees": (
        "Quarter turn (𝒢₂ only), +90° from e₁ toward e₂:  (x, y) → (−y, x).  This\n"
        "is exactly multiplication by the unit pseudoscalar e₁e₂.\n"
        "\n"
        "Returns:\n"
        "    Vector: this vector turned +90° (e₁ toward e₂).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Vector.e_1).rotate_90_degrees() == 1 * Vector.e_2\n"
        "    True"
    ),
    "vector|projected_onto": _vector_proj_doc,
    "vector|rejected_away_from": _vector_rej_doc,
    "vector|reflected_across": (
        "This vector reflected across the line of another vector (the ``reflect``\n"
        "classmethod's ergonomic form).\n"
        "\n"
        "Args:\n"
        "    across: the vector (or blade) to reflect across.\n"
        "\n"
        "Returns:\n"
        "    Vector: this vector reflected across ``across``."
    ),
    "vector|project": (
        "Classmethod form of the projection; see ``projected_onto``.\n"
        "\n"
        "Args:\n"
        "    onto: the vector (or blade) to project onto.\n"
        "\n"
        "Returns:\n"
        "    ComposableFunction: the projection map onto ``onto``."
    ),
    "vector|reject": (
        "Classmethod form of the rejection; see ``rejected_away_from``.\n"
        "\n"
        "Args:\n"
        "    away_from: the vector (or blade) to reject from.\n"
        "\n"
        "Returns:\n"
        "    ComposableFunction: the rejection map from ``away_from``."
    ),
    "vector|reflect": (
        "Classmethod form of the reflection; see ``reflected_across``.\n"
        "\n"
        "Args:\n"
        "    across: the vector (or blade) to reflect across.\n"
        "\n"
        "Returns:\n"
        "    InvertibleFunction: the reflection map across ``across``."
    ),
    "vector|__iter__": (
        "Iterating a vector yields its coordinate values in order -- ``list(v)``\n"
        "is the coordinate tuple that feeds numpy / plotting.\n"
        "\n"
        "Yields:\n"
        "    Coef: each coordinate value, in order."
    ),
    "vector|isclose": (
        "Numeric near-equality of two vectors, coordinate-wise (see the base\n"
        "``isclose``).\n"
        "\n"
        "Args:\n"
        "    other: the vector to compare against.\n"
        "\n"
        "Returns:\n"
        "    bool: ``True`` iff every coordinate is within tolerance."
    ),
    "vector|from_blade_dict": (
        "Build a vector from a blade→coefficient dict (only grade-1 blades\n"
        "kept).\n"
        "\n"
        "Args:\n"
        "    blade_coef: a canonical blade -> coefficient mapping.\n"
        "\n"
        "Returns:\n"
        "    Vector: a vector holding the grade-1 coefficients."
    ),
    "vector|to_blade_dict": (
        "This vector as a blade→coefficient dict (grade-1 blades only).\n"
        "\n"
        "Returns:\n"
        "    BladeCoef: the grade-1 blade -> coefficient mapping."
    ),
    "vector|__lt__": (
        "Left contraction operator ``<``; see ``left_contraction``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the left contraction ``self < other``."
    ),
    "vector|__gt__": (
        "Right contraction operator ``>``; see ``right_contraction``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the right contraction ``self > other``."
    ),
    "vector|__radd__": (
        "Reflected sum  (number) + a  -- adds a scalar part, giving a mixed\n"
        "multivector.\n"
        "\n"
        "Args:\n"
        "    lhs: the bare number on the left.\n"
        "\n"
        "Returns:\n"
        "    the mixed multivector ``lhs + a`` (scalar + vector)."
    ),
    "vector|__rmul__": (
        "Reflected product  (number) * a  -- scales the vector.\n"
        "\n"
        "Args:\n"
        "    lhs: the bare number on the left.\n"
        "\n"
        "Returns:\n"
        "    Vector: the scaled vector."
    ),
    # ------------------------------------------------------------------
    # Trivector (grade 3) -- the oriented VOLUME element and the pseudoscalar
    # of 𝒢₃.  Only exists in 𝒢₃.
    # ------------------------------------------------------------------
    "trivector|__add__": (
        "Sum of two trivectors -- added component-wise (still a trivector; 𝒢₃ has\n"
        "a single grade-3 blade e₁e₂e₃).\n"
        "\n"
        "Args:\n"
        "    rhs: the trivector to add.\n"
        "\n"
        "Returns:\n"
        "    Trivector: the component-wise sum.\n"
        "\n"
        "Example:\n"
        "    >>> 1 * Trivector.e_123 + 1 * Trivector.e_123 == 2 * Trivector.e_123\n"
        "    True"
    ),
    "trivector|__sub__": (
        "Difference of two trivectors, component-wise.\n"
        "\n"
        "Args:\n"
        "    rhs: the trivector to subtract.\n"
        "\n"
        "Returns:\n"
        "    Trivector: the component-wise difference."
    ),
    "trivector|__neg__": (
        "Negation -- reverses the orientation of the volume.\n"
        "\n"
        "Returns:\n"
        "    Trivector: the negated trivector.\n"
        "\n"
        "Example:\n"
        "    >>> -(2 * Trivector.e_123) == -2 * Trivector.e_123\n"
        "    True"
    ),
    "trivector|__mul__": (
        "Geometric product.  The 𝒢₃ pseudoscalar squares to −1 and commutes with\n"
        "everything (it is the imaginary of 3-D space).\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the geometric product (a scalar for two trivectors; the operand\n"
        "    dualized in general).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Trivector.e_123) * (1 * Trivector.e_123) == Scalar.from_scalar(-1)\n"
        "    True"
    ),
    "trivector|_geometric_product": (
        "The geometric-product primitive (use ``*``); the pseudoscalar squares to\n"
        "−1.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the geometric product ``self * rhs``."
    ),
    "trivector|dot": (
        "Inner product with another trivector -- a scalar; for the unit\n"
        "pseudoscalar it is −1.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the inner product (a scalar).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Trivector.e_123).dot(1 * Trivector.e_123) == Scalar.from_scalar(-1)\n"
        "    True"
    ),
    "trivector|inner_product": (
        "Inner product of trivectors -- a scalar (−1 for the unit pseudoscalar);\n"
        "see ``dot``.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the inner product (a scalar)."
    ),
    "trivector|left_contraction": (
        "Left contraction (the ``<`` operator); lowers grade.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the left contraction (lowers grade)."
    ),
    "trivector|right_contraction": (
        "Right contraction (the ``>`` operator); lowers grade.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the right contraction (lowers grade)."
    ),
    "trivector|outer_product": (
        "Outer product.  A trivector wedged with anything of grade ≥ 1 is 0 --\n"
        "grade 3 is already the top of 𝒢₃.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Scalar: 0 (grade 3 is the top of 𝒢₃).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Trivector.e_123) ^ (1 * Trivector.e_123) == Scalar.zero()\n"
        "    True"
    ),
    "trivector|wedge": (
        "Outer product; a trivector ∧ (grade ≥ 1) is 0 (grade 3 is the top of\n"
        "𝒢₃).\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the outer product (0 with any grade ≥ 1)."
    ),
    "trivector|__xor__": (
        "Outer (wedge) product operator ``^``; see ``wedge``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the outer product ``self ^ other``."
    ),
    "trivector|dual": (
        "Dual in 𝒢₃: the trivector (pseudoscalar) duals to a scalar.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the dual (a scalar).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Trivector.e_123).dual() == Scalar.from_scalar(1)\n"
        "    True"
    ),
    "trivector|even_part": (
        "A trivector has odd grade (3), so it has no even part.\n"
        "\n"
        "Returns:\n"
        "    Scalar: 0 (a trivector has no even-grade part).\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Trivector.e_123).even_part() == Scalar.zero()\n"
        "    True"
    ),
    "trivector|odd_part": (
        "A trivector is odd (grade 3), so its odd part is the whole thing.\n"
        "\n"
        "Returns:\n"
        "    Trivector: the trivector itself.\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Trivector.e_123).odd_part() == 2 * Trivector.e_123\n"
        "    True"
    ),
    "trivector|scalar_part": (
        "The scalar (grade-0) part of a trivector is 0.\n"
        "\n"
        "Returns:\n"
        "    Coef: 0 (a trivector has no scalar part).\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Trivector.e_123).scalar_part()\n"
        "    0"
    ),
    "trivector|r_vector_part": (
        "The grade-r part.  A trivector is pure grade 3, so r=3 gives it back and\n"
        "any other grade is 0.\n"
        "\n"
        "Args:\n"
        "    r: the grade to extract.\n"
        "\n"
        "Returns:\n"
        "    Trivector: the grade-``r`` part (the trivector for r=3, else 0).\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Trivector.e_123).r_vector_part(3) == 2 * Trivector.e_123\n"
        "    True"
    ),
    "trivector|grades": (
        "A nonzero trivector is homogeneous of grade 3.\n"
        "\n"
        "Returns:\n"
        "    list[int]: ``[3]`` for a nonzero trivector.\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Trivector.e_123).grades()\n"
        "    [3]"
    ),
    "trivector|magnitude_squared": (
        "Squared magnitude  |T|²  -- the square of the single e₁e₂e₃ component.\n"
        "\n"
        "Returns:\n"
        "    Coef: the squared magnitude.\n"
        "\n"
        "Example:\n"
        "    >>> (2 * Trivector.e_123).magnitude_squared()\n"
        "    4"
    ),
    "trivector|__iter__": (
        "Iterating a trivector yields its single grade-3 component value.\n"
        "\n"
        "Yields:\n"
        "    Coef: the single grade-3 component value."
    ),
    "trivector|isclose": (
        "Numeric near-equality of two trivectors (see the base ``isclose``).\n"
        "\n"
        "Args:\n"
        "    other: the trivector to compare against.\n"
        "\n"
        "Returns:\n"
        "    bool: ``True`` iff the two are within tolerance."
    ),
    "trivector|from_blade_dict": (
        "Build a trivector from a blade→coefficient dict (grade-3 blade only).\n"
        "\n"
        "Args:\n"
        "    blade_coef: a canonical blade -> coefficient mapping.\n"
        "\n"
        "Returns:\n"
        "    Trivector: a trivector holding the grade-3 coefficient."
    ),
    "trivector|to_blade_dict": (
        "This trivector as a blade→coefficient dict (grade-3 blade only).\n"
        "\n"
        "Returns:\n"
        "    BladeCoef: the grade-3 blade -> coefficient mapping."
    ),
    "trivector|__lt__": (
        "Left contraction operator ``<``; see ``left_contraction``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the left contraction ``self < other``."
    ),
    "trivector|__gt__": (
        "Right contraction operator ``>``; see ``right_contraction``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the right contraction ``self > other``."
    ),
    "trivector|__radd__": (
        "Reflected sum  (number) + T  -- adds a scalar part.\n"
        "\n"
        "Args:\n"
        "    lhs: the bare number on the left.\n"
        "\n"
        "Returns:\n"
        "    the mixed multivector ``lhs + T`` (scalar + trivector)."
    ),
    "trivector|__rmul__": (
        "Reflected product  (number) * T  -- scales the trivector.\n"
        "\n"
        "Args:\n"
        "    lhs: the bare number on the left.\n"
        "\n"
        "Returns:\n"
        "    Trivector: the scaled trivector."
    ),
    # ------------------------------------------------------------------
    # Versor (the even subalgebra {0, 2}) -- what actually rotates.  A versor is
    # a scalar + a bivector; apply it with ``sandwich``.  Present in 𝒢₂/𝒢₃.
    # ------------------------------------------------------------------
    "versor|__add__": (
        "Adds two versors component-wise.  Note this is NOT how you compose\n"
        "rotations -- use the geometric product ``*`` for that.\n"
        "\n"
        "Args:\n"
        "    rhs: the versor to add.\n"
        "\n"
        "Returns:\n"
        "    Versor: the component-wise sum (not a composed rotation).\n"
        "\n"
        "Example:\n"
        "    >>> Versor.from_scalar(1) + Versor.from_scalar(2) == Versor.from_scalar(3)\n"
        "    True"
    ),
    "versor|__sub__": (
        "Difference of two versors, component-wise.\n"
        "\n"
        "Args:\n"
        "    rhs: the versor to subtract.\n"
        "\n"
        "Returns:\n"
        "    Versor: the component-wise difference."
    ),
    "versor|__neg__": (
        "Negation -- flips both the scalar and bivector parts.\n"
        "\n"
        "Returns:\n"
        "    Versor: the negated versor."
    ),
    "versor|__mul__": (
        "Geometric product of two versors COMPOSES their rotations.  A rotor times\n"
        "its own reverse is the identity rotor (the reverse is the inverse).\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Versor: the composed rotation (for two versors).\n"
        "\n"
        "Example:\n"
        "    >>> R: Versor = (1 * Bivector.e_12).exp()\n"
        "    >>> R * R.reverse() == Versor.from_scalar(1)\n"
        "    True"
    ),
    "versor|_geometric_product": (
        "The geometric-product primitive (use ``*``); composes two rotations.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the geometric product ``self * rhs``."
    ),
    "versor|sandwich": (
        "Apply this versor to a value:  R x R⁻¹  (the sandwich) -- this is how a\n"
        "versor actually rotates.  The identity versor leaves x unchanged.\n"
        "\n"
        "Args:\n"
        "    x: the value to rotate; the result has ``x``'s own type.\n"
        "\n"
        "Returns:\n"
        "    the rotated value  R x R̃, of ``x``'s own type.\n"
        "\n"
        "Example:\n"
        "    >>> Versor.from_scalar(1).sandwich(1 * Vector.e_1) == 1 * Vector.e_1\n"
        "    True"
    ),
    "versor|plane_of_rotation": (
        "The bivector plane this versor rotates in.\n"
        "\n"
        "Returns:\n"
        "    Bivector: the plane of rotation.\n"
        "\n"
        "Example:\n"
        "    >>> R: Versor = 1 + 1 * Versor.e_12\n"
        "    >>> R.plane_of_rotation() == 1 * Bivector.e_12\n"
        "    True"
    ),
    "versor|grades": (
        "A versor is even: a scalar (grade 0) plus a bivector (grade 2).\n"
        "\n"
        "Returns:\n"
        "    list[int]: the present even grades (``[0, 2]`` for a general versor).\n"
        "\n"
        "Example:\n"
        "    >>> (1 + 1 * Versor.e_12).grades()\n"
        "    [0, 2]"
    ),
    "versor|even_part": (
        "A versor is entirely even, so its even part is itself.\n"
        "\n"
        "Returns:\n"
        "    Versor: the versor itself.\n"
        "\n"
        "Example:\n"
        "    >>> R: Versor = 1 + 1 * Versor.e_12\n"
        "    >>> R.even_part() == R\n"
        "    True"
    ),
    "versor|odd_part": (
        "A versor has no odd part, so it is 0.\n"
        "\n"
        "Returns:\n"
        "    Scalar: 0 (a versor has no odd-grade part).\n"
        "\n"
        "Example:\n"
        "    >>> (1 + 1 * Versor.e_12).odd_part() == Scalar.zero()\n"
        "    True"
    ),
    "versor|scalar_part": (
        "The scalar (grade-0) part of a versor -- cos(θ/2) for a rotation by θ.\n"
        "\n"
        "Returns:\n"
        "    Coef: the grade-0 coefficient (cos(θ/2) for a rotation by θ).\n"
        "\n"
        "Example:\n"
        "    >>> (1 + 1 * Versor.e_12).scalar_part()\n"
        "    1"
    ),
    "versor|r_vector_part": (
        "Extract a grade.  A versor has a grade-0 and a grade-2 part.\n"
        "\n"
        "Args:\n"
        "    r: the grade to extract (0 or 2 for a versor).\n"
        "\n"
        "Returns:\n"
        "    the grade-``r`` part (a scalar for r=0, a bivector for r=2).\n"
        "\n"
        "Example:\n"
        "    >>> (1 + 1 * Versor.e_12).r_vector_part(0) == Scalar.from_scalar(1)\n"
        "    True"
    ),
    "versor|magnitude_squared": (
        "Squared magnitude  |R|² = scalar² + |bivector|²; a rotation rotor is\n"
        "unit.\n"
        "\n"
        "Returns:\n"
        "    Coef: the squared magnitude (1 for a rotation rotor).\n"
        "\n"
        "Example:\n"
        "    >>> (1 + 1 * Versor.e_12).magnitude_squared()\n"
        "    2"
    ),
    "versor|dot": (
        "Inner product of two versors -- a scalar.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the inner product (a scalar)."
    ),
    "versor|inner_product": (
        "Inner product of two versors -- a scalar (see ``dot``).\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the inner product (a scalar)."
    ),
    "versor|left_contraction": (
        "Left contraction (the ``<`` operator).\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the left contraction ``self < rhs``."
    ),
    "versor|right_contraction": (
        "Right contraction (the ``>`` operator).\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the right contraction ``self > rhs``."
    ),
    "versor|outer_product": (
        "Outer (wedge) product.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the outer product ``self ∧ rhs``."
    ),
    "versor|wedge": (
        "Outer (wedge) product.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the outer product ``self ∧ rhs``."
    ),
    "versor|__xor__": (
        "Outer (wedge) product operator ``^``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the outer product ``self ^ other``."
    ),
    "versor|dual": (
        "Dual  R* = R / i (a versor is even, so its dual is even too).\n"
        "\n"
        "Returns:\n"
        "    the dual (an even multivector)."
    ),
    "versor|__iter__": (
        "Iterating a versor yields its component values (scalar then bivector\n"
        "parts).\n"
        "\n"
        "Yields:\n"
        "    Coef: each component value (scalar then bivector parts)."
    ),
    "versor|isclose": (
        "Numeric near-equality of two versors (see the base ``isclose``).\n"
        "\n"
        "Args:\n"
        "    other: the versor to compare against.\n"
        "\n"
        "Returns:\n"
        "    bool: ``True`` iff the two are within tolerance."
    ),
    "versor|from_blade_dict": (
        "Build a versor from a blade→coefficient dict (grade-0 and grade-2 blades\n"
        "kept).\n"
        "\n"
        "Args:\n"
        "    blade_coef: a canonical blade -> coefficient mapping.\n"
        "\n"
        "Returns:\n"
        "    Versor: a versor holding the grade-0 and grade-2 coefficients."
    ),
    "versor|to_blade_dict": (
        "This versor as a blade→coefficient dict (scalar + bivector blades).\n"
        "\n"
        "Returns:\n"
        "    BladeCoef: the grade-0 + grade-2 blade -> coefficient mapping."
    ),
    "versor|__lt__": (
        "Left contraction operator ``<``; see ``left_contraction``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the left contraction ``self < other``."
    ),
    "versor|__gt__": (
        "Right contraction operator ``>``; see ``right_contraction``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the right contraction ``self > other``."
    ),
    "versor|__radd__": (
        "Reflected sum  (number) + R  -- adds to the versor's scalar part.\n"
        "\n"
        "Args:\n"
        "    lhs: the bare number on the left.\n"
        "\n"
        "Returns:\n"
        "    Versor: the versor with ``lhs`` added to its scalar part."
    ),
    "versor|__rmul__": (
        "Reflected product  (number) * R  -- scales the versor.\n"
        "\n"
        "Args:\n"
        "    lhs: the bare number on the left.\n"
        "\n"
        "Returns:\n"
        "    Versor: the scaled versor."
    ),
    # ------------------------------------------------------------------
    # Odd_3 (the odd part {1, 3} of 𝒢₃) -- vectors + trivectors.  A subspace
    # but NOT a subalgebra: odd × odd = even, so a product lands in Versor.
    # ------------------------------------------------------------------
    "odd|__add__": (
        "Sum of two odd multivectors, component-wise (grades {1, 3} stay {1, 3}).\n"
        "\n"
        "Args:\n"
        "    rhs: the odd multivector to add.\n"
        "\n"
        "Returns:\n"
        "    Odd_3: the component-wise sum.\n"
        "\n"
        "Example:\n"
        "    >>> 1 * Odd_3.e_1 + 1 * Odd_3.e_1 == 2 * Odd_3.e_1\n"
        "    True"
    ),
    "odd|__sub__": (
        "Difference of two odd multivectors, component-wise.\n"
        "\n"
        "Args:\n"
        "    rhs: the odd multivector to subtract.\n"
        "\n"
        "Returns:\n"
        "    Odd_3: the component-wise difference."
    ),
    "odd|__neg__": (
        "Negation -- every component sign-flipped.\n"
        "\n"
        "Returns:\n"
        "    Odd_3: the negated odd multivector."
    ),
    "odd|__mul__": (
        "Geometric product.  The product of two ODD multivectors is EVEN (a\n"
        "versor): odd × odd = even, so Odd_3 is a subspace but NOT a subalgebra.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Versor: the product (odd × odd is even).\n"
        "\n"
        "Example:\n"
        "    >>> product: Versor = (1 * Odd_3.e_1) * (1 * Odd_3.e_1)\n"
        "    >>> product == Versor.from_scalar(1)\n"
        "    True"
    ),
    "odd|_geometric_product": (
        "The geometric-product primitive (use ``*``); odd × odd is even.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the geometric product ``self * rhs``."
    ),
    "odd|to_vector": (
        "The grade-1 (vector) part, as a ``Vector`` -- raises if the grade-3 part\n"
        "is nonzero.\n"
        "\n"
        "Returns:\n"
        "    Vector: the grade-1 part.\n"
        "\n"
        "Raises:\n"
        "    ValueError: if the grade-3 (trivector) part is nonzero.\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Odd_3.e_1).to_vector() == 1 * Vector.e_1\n"
        "    True"
    ),
    "odd|to_trivector": (
        "The grade-3 (trivector) part, as a ``Trivector`` -- raises if the grade-1\n"
        "part is nonzero.\n"
        "\n"
        "Returns:\n"
        "    Trivector: the grade-3 part.\n"
        "\n"
        "Raises:\n"
        "    ValueError: if the grade-1 (vector) part is nonzero.\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Odd_3.e_123).to_trivector() == 1 * Trivector.e_123\n"
        "    True"
    ),
    "odd|grades": (
        "An odd multivector of 𝒢₃ carries grades 1 and/or 3.\n"
        "\n"
        "Returns:\n"
        "    list[int]: the present odd grades (``[1, 3]`` for a general Odd_3).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Odd_3.e_1 + 1 * Odd_3.e_123).grades()\n"
        "    [1, 3]"
    ),
    "odd|even_part": (
        "An odd multivector has no even part, so it is 0.\n"
        "\n"
        "Returns:\n"
        "    Scalar: 0 (an odd multivector has no even-grade part).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Odd_3.e_1 + 1 * Odd_3.e_123).even_part() == Scalar.zero()\n"
        "    True"
    ),
    "odd|odd_part": (
        "An odd multivector is entirely odd, so its odd part is itself.\n"
        "\n"
        "Returns:\n"
        "    Odd_3: the odd multivector itself.\n"
        "\n"
        "Example:\n"
        "    >>> O: Odd_3 = 1 * Odd_3.e_1 + 1 * Odd_3.e_123\n"
        "    >>> O.odd_part() == O\n"
        "    True"
    ),
    "odd|r_vector_part": (
        "Extract a grade.  Grade 1 gives the vector part (as a ``Vector``); grade\n"
        "3 gives the trivector part.\n"
        "\n"
        "Args:\n"
        "    r: the grade to extract (1 or 3 for an odd multivector).\n"
        "\n"
        "Returns:\n"
        "    the grade-``r`` part (a Vector for r=1, a Trivector for r=3).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Odd_3.e_1 + 1 * Odd_3.e_123).r_vector_part(1) == 1 * Vector.e_1\n"
        "    True"
    ),
    "odd|scalar_part": (
        "The scalar (grade-0) part of an odd multivector is 0.\n"
        "\n"
        "Returns:\n"
        "    Coef: 0 (an odd multivector has no scalar part).\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Odd_3.e_1 + 1 * Odd_3.e_123).scalar_part()\n"
        "    0"
    ),
    "odd|magnitude_squared": (
        "Squared magnitude  |O|²  -- the sum of squared components.\n"
        "\n"
        "Returns:\n"
        "    Coef: the squared magnitude.\n"
        "\n"
        "Example:\n"
        "    >>> (1 * Odd_3.e_1 + 1 * Odd_3.e_123).magnitude_squared()\n"
        "    2"
    ),
    "odd|dot": (
        "Inner product of two odd multivectors -- a scalar.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the inner product (a scalar)."
    ),
    "odd|inner_product": (
        "Inner product of two odd multivectors -- a scalar (see ``dot``).\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    Scalar: the inner product (a scalar)."
    ),
    "odd|left_contraction": (
        "Left contraction (the ``<`` operator).\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the left contraction ``self < rhs``."
    ),
    "odd|right_contraction": (
        "Right contraction (the ``>`` operator).\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the right contraction ``self > rhs``."
    ),
    "odd|outer_product": (
        "Outer (wedge) product.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the outer product ``self ∧ rhs``."
    ),
    "odd|wedge": (
        "Outer (wedge) product.\n"
        "\n"
        "Args:\n"
        "    rhs: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the outer product ``self ∧ rhs``."
    ),
    "odd|__xor__": (
        "Outer (wedge) product operator ``^``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the outer product ``self ^ other``."
    ),
    "odd|dual": (
        "Dual  O* = O / i -- maps the odd part to the even part (a versor).\n"
        "\n"
        "Returns:\n"
        "    Versor: the dual (maps the odd part to the even part)."
    ),
    "odd|__iter__": (
        "Iterating an odd multivector yields its component values (grade-1 then\n"
        "grade-3).\n"
        "\n"
        "Yields:\n"
        "    Coef: each component value (grade-1 then grade-3)."
    ),
    "odd|isclose": (
        "Numeric near-equality of two odd multivectors (see the base\n"
        "``isclose``).\n"
        "\n"
        "Args:\n"
        "    other: the odd multivector to compare against.\n"
        "\n"
        "Returns:\n"
        "    bool: ``True`` iff every component is within tolerance."
    ),
    "odd|from_blade_dict": (
        "Build an odd multivector from a blade→coefficient dict (grade-1 and\n"
        "grade-3 blades).\n"
        "\n"
        "Args:\n"
        "    blade_coef: a canonical blade -> coefficient mapping.\n"
        "\n"
        "Returns:\n"
        "    Odd_3: an odd multivector holding the grade-1 and grade-3 coefficients."
    ),
    "odd|to_blade_dict": (
        "This odd multivector as a blade→coefficient dict (grade-1 and grade-3\n"
        "blades).\n"
        "\n"
        "Returns:\n"
        "    BladeCoef: the grade-1 + grade-3 blade -> coefficient mapping."
    ),
    "odd|__lt__": (
        "Left contraction operator ``<``; see ``left_contraction``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the left contraction ``self < other``."
    ),
    "odd|__gt__": (
        "Right contraction operator ``>``; see ``right_contraction``.\n"
        "\n"
        "Args:\n"
        "    other: the right operand.\n"
        "\n"
        "Returns:\n"
        "    the right contraction ``self > other``."
    ),
    "odd|__radd__": (
        "Reflected sum  (number) + O -- adds a scalar part (giving a mixed\n"
        "multivector).\n"
        "\n"
        "Args:\n"
        "    lhs: the bare number on the left.\n"
        "\n"
        "Returns:\n"
        "    the mixed multivector ``lhs + O`` (scalar + odd)."
    ),
    "odd|__rmul__": (
        "Reflected product  (number) * O -- scales the odd multivector.\n"
        "\n"
        "Args:\n"
        "    lhs: the bare number on the left.\n"
        "\n"
        "Returns:\n"
        "    Odd_3: the scaled odd multivector."
    ),
}


def _role_for_class(class_name: str, full_name: str) -> str:
    """The grade identity used to key ``CUSTOM_METHOD_DOCS`` for ``class_name``."""
    if class_name == full_name:
        return "full"
    known: dict[str, str] = {
        "Scalar": "scalar",
        "Vector": "vector",
        "Bivector": "bivector",
        "Trivector": "trivector",
        "Versor": "versor",
        "Odd_3": "odd",
    }
    return known.get(class_name, "generic")


def _own_docstring(method: str) -> str | None:
    """The docstring ``method`` defines on ``MultiVectorBase`` or ``Gn``.

    Only a docstring actually written on one of those classes -- never one an
    ``object`` dunder (``__eq__`` etc.) is inherited by accident.
    """
    src: type
    for src in (MultiVectorBase, Gn):
        if method in vars(src):
            doc: str | None = inspect.getdoc(getattr(src, method))
            if doc:
                return doc
    return None


def custom_method_doc(role: str, method: str, n: int) -> str | None:
    """A specialized ``CUSTOM_METHOD_DOCS`` entry for ``method`` on a ``role`` class
    of 𝒢ₙ, or ``None`` if there is none (or n is a generic-only dimension).

    An entry is either literal text or a ``(role, n) -> str`` callable (so one
    function can serve a shared method across every role with a role-appropriate
    example).  A ``role|method`` key wins over the role-agnostic ``*|method``.
    """
    if n not in _CUSTOM_DOC_DIMS:
        return None
    entry: DocEntry | None = CUSTOM_METHOD_DOCS.get(
        f"{role}|{method}"
    ) or CUSTOM_METHOD_DOCS.get(f"*|{method}")
    if isinstance(entry, str):
        return entry
    if entry is not None:
        return entry(role, n)
    return None


def _set_method_docstring(func: ast.FunctionDef, text: str) -> None:
    """Set ``func``'s docstring to ``text``, replacing any existing one."""
    expr: ast.Expr = doc_expr(text)
    if ast.get_docstring(func) is not None:
        func.body[0] = expr
    else:
        func.body.insert(0, expr)


def inject_method_docstrings(nodes: Sequence[ast.stmt], n: int, full_name: str) -> None:
    """Give every method of every generated class a docstring.

    Mutates the class ``ast`` nodes in place.  ``@overload`` stubs are left bare
    (they never render).  Otherwise: a specialized ``CUSTOM_METHOD_DOCS`` entry
    *overrides* whatever the builder emitted (so g1--g3 get grade-aware text),
    and a method with neither a custom entry nor an existing docstring falls back
    to the copied generic base docstring.
    """
    node: ast.stmt
    for node in nodes:
        if not isinstance(node, ast.ClassDef):
            continue
        role: str = _role_for_class(node.name, full_name)
        item: ast.stmt
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            decorators: set[str | None] = {
                getattr(d, "attr", getattr(d, "id", None)) for d in item.decorator_list
            }
            if "overload" in decorators:
                continue
            custom: str | None = custom_method_doc(role, item.name, n)
            if custom is not None:
                _set_method_docstring(item, custom)
            elif ast.get_docstring(item) is None:
                base: str | None = _own_docstring(item.name)
                if base:
                    item.body.insert(0, doc_expr(base))


# The 𝒢₂ quarter turn.  Two forms share one closed form: the generated
# ``Vector.rotate_90_degrees()`` method (ROTATE_90_METHOD_DOC, 8-space method
# indent) and the module-level ``rotate_90_degrees()`` InvertibleFunction
# factory (ROTATE_90_FACTORY_DOC, 4-space function indent).  Both docstrings
# teach the identity the name stands for: in 𝒢₂ a quarter turn IS
# multiplication by the unit pseudoscalar e_12.
ROTATE_90_METHOD_DOC: str = (
    "Rotate this vector a quarter turn (+90°, e₁ toward e₂) in the e₁e₂ plane.\n"
    "\n"
    "        In 𝒢₂ a quarter turn IS multiplication by the unit pseudoscalar:\n"
    "        ``v.rotate_90_degrees() == v * e_12``, i.e. ``(x, y) -> (-y, x)``.\n"
    "        The body is that product's closed form, so the turn is exact (no\n"
    "        ``cos``/``sin``); ``plane_rotation(e_1, e_2)(theta)`` remains the\n"
    "        general-angle versor.  Four turns are the identity; the -90° turn\n"
    "        (``v * -e_12``) is the inverse of the module-level\n"
    "        ``rotate_90_degrees()`` function, which wraps this method as an\n"
    "        ``InvertibleFunction``.  𝒢₂ only: in higher dimensions ``v * e_12``\n"
    "        sends an e₃ component to a trivector, which is why there is no\n"
    "        general-dimension version."
)

ROTATE_90_FACTORY_DOC: str = (
    "Rotate a 𝒢₂ vector a quarter turn (+90°, e₁ toward e₂), packaged as an\n"
    "    :class:`InvertibleFunction` -- so it composes (``f @ f`` is the half\n"
    "    turn; four turns are the identity) and inverts (the -90° turn,\n"
    "    ``v * -e_12``).\n"
    "\n"
    "    ``rotate_90_degrees()(v) == v * e_12``: in 𝒢₂ a quarter turn is\n"
    "    multiplication by the unit pseudoscalar, ``(x, y) -> (-y, x)``, exact\n"
    "    (no ``cos``/``sin``) -- the same closed form as\n"
    "    :meth:`Vector.rotate_90_degrees`.  ``at(t)`` interpolates through\n"
    "    ``plane_rotation(e_1, e_2)(t * pi / 2)`` and is the exact turn at\n"
    "    ``t >= 1``.  Takes a grade-1 ``Vector`` only (``TypeError`` for any\n"
    "    other type); 𝒢₂ only, since in higher dimensions ``v * e_12`` sends an\n"
    "    e₃ component to a trivector.\n"
    "\n"
    "    Example:\n"
    "        >>> from gacalc.g2 import e_1, e_2, e_12, rotate_90_degrees\n"
    "        >>> turn = rotate_90_degrees()\n"
    "        >>> turn(3 * e_1 + 4 * e_2) == -4 * e_1 + 3 * e_2\n"
    "        True\n"
    "        >>> turn(3 * e_1 + 4 * e_2) == (3 * e_1 + 4 * e_2) * e_12\n"
    "        True\n"
    "        >>> (turn @ turn @ turn @ turn)(3 * e_1 + 4 * e_2) == 3 * e_1 + 4 * e_2\n"
    "        True"
)

# The 𝒢₂ signed sine (the scalar, oriented companion to the unsigned, any-dimension
# ``MultiVectorBase.abs_sin``).  Decision 8 in the task: ``sine`` returns a SIGNED
# SCALAR, not a bivector -- "sometimes we just want to know the sine and cosine."
SINE_METHOD_DOC: str = (
    "Signed sine of the angle from this vector to ``other`` (𝒢₂ only).\n"
    "\n"
    "        The wedge of two 𝒢₂ vectors has a single component, the signed area\n"
    "        ``(a ∧ b).coeff_e_12 = a₁b₂ − a₂b₁``; dividing by the two magnitudes\n"
    "        gives a **signed** ``sin θ`` whose sign is the turn direction, so\n"
    "        swapping the arguments negates it -- unlike the unsigned,\n"
    "        any-dimension :meth:`MultiVectorBase.abs_sin`.  The scalar companion\n"
    "        to :meth:`MultiVectorBase.cosine`; raises on a zero-length operand.\n"
    "        𝒢₂ only: in higher dimensions the wedge spans a plane with no single\n"
    "        turn direction, so use ``abs_sin`` there.\n"
    "\n"
    "        Args:\n"
    "            other: the other vector.\n"
    "\n"
    "        Returns:\n"
    "            Coef: the signed sine ``(a ∧ b).coeff_e_12 / (|a| |b|)``.\n"
    "\n"
    "        Example:\n"
    "            >>> (1.0 * Vector.e_1).sine(1.0 * Vector.e_2)\n"
    "            1.0\n"
    "            >>> (1.0 * Vector.e_2).sine(1.0 * Vector.e_1)\n"
    "            -1.0\n"
    "            >>> (1.0 * Vector.e_1).sine(5.0 * Vector.e_1)\n"
    "            0.0"
)

# The unit-bivector plane helpers: `i(a, b)` (classmethod, on Gn/G2/G3/Vector,
# building the plane from two vectors) and `.i()` (instance, on Bivector/Versor,
# getting a value's own plane).  `i(a, b)` normalizes `bivector_from_vectors`
# (on MultiVectorBase); `.i()` normalizes the value's grade-2 part.  Both return
# a BIVECTOR (the unit plane, i*i == -1), never a versor.
I_FROM_VEC_DOC: str = (
    "The unit bivector ``i`` of the plane spanned by vectors ``a``, ``b``\n"
    "        (``i * i == -1``) -- the normalized wedge ``a`` ∧ ``b``.\n"
    "\n"
    "        ``= bivector_from_vectors(a, b).normalize()``.  Raises if ``a`` and\n"
    "        ``b`` are parallel (their wedge is the zero bivector).  This is the\n"
    "        plane you feed a versor builder / ``exp`` -- a bivector, not a versor."
)

I_DOC: str = (
    "The unit bivector ``i`` of this value's plane (``i * i == -1``).\n"
    "\n"
    "        The normalized grade-2 (plane) part -- for a versor\n"
    "        ``cos(t/2) - sin(t/2) * i`` this returns ``i``; for a bivector it is\n"
    "        the bivector normalized.  A bivector, never a versor.  Undefined\n"
    "        (raises) for a zero bivector part."
)


# Two parallel vectors span no plane: their wedge is the *zero* bivector, which
# has no unit direction.  ``i`` raises this explicitly rather than leaking
# ``normalize``'s low-level ``ZeroDivisionError`` -- the same guard and message
# ``transforms.plane_rotation`` uses, so the two entry points agree.
PARALLEL_VECTORS_MSG: str = (
    "the two vectors are parallel (their wedge is zero): they span no plane of rotation"
)


def classmethod_narrowing_overloads(
    method: str, param_names: Sequence[str], precise_ret: str
) -> list[ast.stmt]:
    """Precise + catch-all ``@overload`` stubs for a value-returning classmethod
    whose result is a *fixed grade*: applied to this algebra's ``Vector`` args it
    returns ``precise_ret`` (``bivector_from_vectors``/``i`` -> ``Bivector``,
    ``versor_from_vectors`` -> ``Versor``); the ``MultiVectorBase`` catch-all keeps
    the base's imprecise type for any other input.  Discriminating on the ``Vector``
    param type is what makes the narrowing sound -- the wedge / versor of two
    same-algebra vectors is that algebra's ``Bivector`` / ``Versor`` at runtime.
    Only meaningful where ``precise_ret`` exists (n>=2 -- 𝒢₁ has no bivector), so
    the caller passes it only then."""

    def stub(param_type: str, ret: str) -> ast.stmt:
        return function_def(
            method,
            [ast.Expr(constant(...))],
            params=[argument("cls")]
            + [argument(p, name_ref(param_type)) for p in param_names],
            decorators=[attribute("typing", "overload"), name_ref("classmethod")],
            returns=name_ref(ret),
        )

    return [stub("Vector", precise_ret), stub("MultiVectorBase", "MultiVectorBase")]


def inherited_classmethod_narrowing(
    method: str, param_names: Sequence[str], precise_ret: str
) -> list[ast.stmt]:
    """Narrowing override of an *inherited* base classmethod
    (``bivector_from_vectors`` / ``versor_from_vectors``): base types it
    ``-> MultiVectorBase``, but applied to this algebra's vectors it always yields
    ``precise_ret``.  Emit the precise + catch-all ``@overload`` stubs plus a thin
    impl that delegates to ``super()`` -- runtime is unchanged; base does the work,
    only the static return type is narrowed (same shape as
    ``transform_factory_overrides``)."""
    return [
        *classmethod_narrowing_overloads(method, param_names, precise_ret),
        function_def(
            method,
            [return_stmt(super_call(method, [name_ref(p) for p in param_names]))],
            params=[argument("cls")] + [argument(p) for p in param_names],
            decorators=[name_ref("classmethod")],
            returns=name_ref("MultiVectorBase"),
        ),
    ]


def i_classmethod(precise_ret: str | None = None) -> list[ast.stmt]:
    """Emit the ``i(a, b)`` classmethod (unit bivector of the plane two vectors
    span) for the full classes + Vector: normalize ``bivector_from_vectors``,
    raising a clear ``ValueError`` (``PARALLEL_VECTORS_MSG``) on parallel vectors
    instead of leaking ``normalize``'s ``ZeroDivisionError``.  When ``precise_ret``
    is given (n>=2) prepend the narrowing ``@overload`` stubs so
    ``Vector.i(a, b) -> Bivector``; 𝒢₁ (no bivector) passes ``None`` and stays
    ``-> MultiVectorBase``."""
    impl: ast.stmt = function_def(
        "i",
        [
            class_doc_stmt(I_FROM_VEC_DOC),
            assign(
                "plane",
                call(
                    attribute("cls", "bivector_from_vectors"),
                    [name_ref("a"), name_ref("b")],
                ),
            ),
            ast.If(
                ast.Compare(
                    name_ref("plane"),
                    [ast.Eq()],
                    [call(attribute(call("type", [name_ref("plane")]), "zero"), [])],
                ),
                [
                    ast.Raise(
                        exc=call("ValueError", [constant(PARALLEL_VECTORS_MSG)]),
                        cause=None,
                    )
                ],
                [],
            ),
            return_stmt(call(attribute("plane", "normalize"), [])),
        ],
        params=[
            argument("cls"),
            argument("a", name_ref("MultiVectorBase")),
            argument("b", name_ref("MultiVectorBase")),
        ],
        returns=name_ref("MultiVectorBase"),
        decorators=[name_ref("classmethod")],
    )
    return (
        [impl]
        if precise_ret is None
        else [*classmethod_narrowing_overloads("i", ["a", "b"], precise_ret), impl]
    )


def i_extractor(inner_method: str, precise_ret: str) -> ast.FunctionDef:
    """Emit the ``.i()`` instance method (a value's own unit plane) via
    ``inner_method`` (``normalize`` on Bivector, ``plane_of_rotation`` on Versor).
    Returns ``precise_ret`` -- always this algebra's ``Bivector`` (a value's unit
    plane is grade 2); both callers (Bivector, Versor) exist only for n>=2, so the
    ``Bivector`` type is present."""
    return function_def(
        "i",
        [
            class_doc_stmt(I_DOC),
            return_stmt(call(attribute("self", inner_method), [])),
        ],
        returns=name_ref(precise_ret),
    )


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


def scalar_spec(n: int) -> TypeSpec:
    """The grade-0 (``Scalar``) type of 𝒢ₙ — ``Scalar``.

    Per-algebra (not one shared type) so its dual is precise: grade 0 -> grade n
    is that algebra's pseudoscalar (``Scalar.dual -> Vector``, ``Scalar ->
    Bivector``, ``Scalar -> Trivector``), which lives in the same module.  Its
    ``dim`` is n (the shared ``Scalar`` was dimensionless, dim 0)."""
    return TypeSpec("Scalar", ((),), n, "scalar")


# Class name for each grade-pure blade type.  The three entrenched low-grade
# names, then a number-word ``<N>Vector`` scheme that scales without a lookup
# anyone has to recall (gacalc's basis constants stop at ``e_10``, so grade 10 is
# the ceiling; ``grade_name`` falls back to ``KVector{k}`` beyond the table).
GRADE_NAMES: dict[int, str] = {
    0: "Scalar",
    1: "Vector",
    2: "Bivector",
    3: "Trivector",
    4: "FourVector",
    5: "FiveVector",
    6: "SixVector",
    7: "SevenVector",
    8: "EightVector",
    9: "NineVector",
    10: "TenVector",
}


def grade_name(k: int) -> str:
    """Class name for the grade-``k`` pure blade type (``Scalar``, ``Vector``,
    ``Bivector``, ``Trivector``, ``FourVector`` …).  See ``GRADE_NAMES``."""
    return GRADE_NAMES.get(k, f"KVector{k}")


def graded_specs(n: int) -> list[TypeSpec]:
    """The graded (grade-pure + even/Versor) types of 𝒢ₙ, per the Phase 1 registry."""
    blades: list[Blade] = blades_for_dim(n)

    def blades_of_grade(grade: int) -> tuple[Blade, ...]:
        return tuple(b for b in blades if len(b) == grade)

    # One grade-pure type per grade 1..n (Vector, Bivector, …, grade_name(n) = the
    # pseudoscalar); grade 0 (Scalar) is emitted separately by generate_scalar.
    specs: list[TypeSpec] = [
        TypeSpec(grade_name(grade), blades_of_grade(grade), n, "graded")
        for grade in range(1, n + 1)
    ]
    if n >= 2:  # even subalgebra (Versor); for n==1 the even part is just the scalar
        even: tuple[Blade, ...] = tuple(b for b in blades if len(b) % 2 == 0)
        specs.append(TypeSpec("Versor", even, n, "graded"))
    if n == 3:
        # The odd part {1,3} of 𝒢₃ -- the mirror of Versor (the even part {0,2}), but a
        # *subspace*, NOT a subalgebra: odd * odd = even, so Odd_3 * Odd_3 -> Versor,
        # landing outside Odd_3 (fine -- Vector/Bivector/Trivector aren't closed either;
        # see tasks/reference/graded-subspaces-vs-subalgebras.md).  Gated to n == 3 so
        # the literal name stays honest; the general higher-dim odd/mixed types are a
        # follow-up (tasks/model-odd-graded-type.md).
        odd_1_3: tuple[Blade, ...] = tuple(b for b in blades if len(b) in (1, 3))
        specs.append(TypeSpec("Odd_3", odd_1_3, n, "graded"))
    return specs


def full_spec(n: int, full_name: str) -> TypeSpec:
    return TypeSpec(full_name, tuple(blades_for_dim(n)), n, "full")


def registry_for_dim(n: int, full_name: str) -> list[TypeSpec]:
    """Scalar + graded types + the full G_n -- every type a result can resolve to."""
    return [scalar_spec(n), *graded_specs(n), full_spec(n, full_name)]


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


def _is_neg_term(term: sympy.Expr, rename: Mapping[str, tuple[str, str]]) -> bool:
    return ast.unparse(expr_to_ast(term, rename)).lstrip().startswith("-")


def summed_value(expr: sympy.Expr, rename: Mapping[str, tuple[str, str]]) -> ast.expr:
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


def result_value(expr: sympy.Expr, rename: Mapping[str, tuple[str, str]]) -> ast.expr:
    """Constructor field value for the graded dispatch (mirrors result_block)."""
    e: sympy.Expr = sympy.sympify(expr)
    return (
        cast_coef(expr_to_ast(e, rename))
        if e.is_Mul and (-e).is_Symbol
        else summed_value(e, rename)
    )


def unary_value(expr: sympy.Expr, rename: Mapping[str, tuple[str, str]]) -> ast.expr:
    """Constructor field value for unary results (mirrors unary_return)."""
    e: sympy.Expr = sympy.sympify(expr)
    return expr_to_ast(e, rename) if e.is_Symbol else cast_coef(expr_to_ast(e, rename))


# ==========================================================================
# Shared class / method builders (used by every generated class)
# ==========================================================================


#: coordinate-accessor names, by basis index: x = e_1, y = e_2, z = e_3.
AXIS_NAMES: tuple[str, ...] = ("x", "y", "z")


def coordinate_property_defs(spec: TypeSpec) -> list[ast.stmt]:
    """``x``/``y``/``z`` read-only properties on grade-1 (vector) types.

    A vector's coordinates ARE its basis coefficients; these are ergonomic
    views over ``coeff_e_1``/``coeff_e_2``/``coeff_e_3`` for consumers that
    speak coordinates.  **Read-only**: the value types are ``frozen`` (immutable),
    so "changing a coordinate" means rebinding a new vector
    (``v = Vector(-v.x, v.y)``), not ``v.x = …``.  Only grade-1 types get them --
    ``x`` on a versor or a full multivector would suggest a coordinate tuple it
    doesn't have."""
    if any(len(b) != 1 for b in spec.blades):
        return []
    defs: list[ast.stmt] = []
    blade: Blade
    for blade in spec.blades:
        if blade[0] - 1 >= len(AXIS_NAMES):
            # e_4 and beyond have no conventional axis letter (x/y/z only) -- a
            # grade-1 value in 𝒢₄₊ reaches those coordinates via ``coeff_e_4`` /
            # ``.coefficient(...)``, not a letter property.
            continue
        axis: str = AXIS_NAMES[blade[0] - 1]
        field: str = field_name(blade)
        defs.append(
            function_def(
                axis,
                [
                    ast.Expr(
                        ast.Constant(
                            f"The {axis} coordinate -- the ``{field}``"
                            " basis coefficient (read-only; the type is frozen)."
                        )
                    ),
                    return_stmt(attribute("self", field)),
                ],
                decorators=[name_ref("property")],
                returns=name_ref("Coef"),
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


def eq_method(fields: Sequence[str]) -> ast.FunctionDef:
    """The generated simplify-aware ``__eq__`` as nodes.

    Two paths.  A **same-type fast path** (``type(self) is type(other)``) compares
    the coefficient fields directly, skipping the blade-dict construction and
    key-set union -- pure overhead when the fields already line up one-to-one.  It
    defers each field to ``base._coef_eq``, which tries a native ``==`` first and
    reaches ``simplify(sympify(l) - sympify(r)) == 0`` **only when a side is
    symbolic** -- so structurally-different but mathematically-equal symbolic
    coefficients (``(x + 1)**2`` vs ``x**2 + 2*x + 1``) still compare equal, while a
    numeric multivector never touches sympy at all, whether its coefficients match
    or differ.  Float ``==`` stays EXACT on purpose (``0.1 + 0.2 != 0.3``);
    tolerance is ``isclose``'s job, not ``==``'s (and a tolerant ``==`` would not
    even be transitive).  The blade-dict
    generator is the **fallback** for the cross-type / cross-representation cases
    (``Vector == G``, specialized ``== Gn``).  ``type(self) is type(other)`` (exact
    identity, not ``isinstance``) is safe because every generated type is
    ``@typing.final``.
    """

    def field_equal(field: str) -> ast.expr:
        """``_coef_eq(self.<field>, other.<field>)``.

        The rule itself lives in the hand-written ``base._coef_eq`` (native ``==``
        first, sympy only when a side is symbolic) so both this same-type path and
        the blade-dict fallback below share one implementation.
        """
        return call(
            name_ref("_coef_eq"), [attribute("self", field), attribute("other", field)]
        )

    gen: ast.GeneratorExp = ast.GeneratorExp(
        elt=call(
            name_ref("_coef_eq"),
            [
                call(attribute("left", "get"), [name_ref("blade"), constant(0)]),
                call(attribute("right", "get"), [name_ref("blade"), constant(0)]),
            ],
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
        # Same-type fast path: fields line up one-to-one, so compare them directly
        # and skip the blade-dict interchange + key-union below.  ``all([...])`` (a
        # list, not a chained ``and``) reads consistently across dimensions -- tidy
        # for 𝒢₅'s 32-field ``G``.
        ast.If(
            test=ast.Compare(
                left=call("type", [name_ref("self")]),
                ops=[ast.Is()],
                comparators=[call("type", [name_ref("other")])],
            ),
            body=[
                return_stmt(
                    call(
                        "all",
                        [
                            ast.List(
                                elts=[field_equal(f) for f in fields], ctx=ast.Load()
                            )
                        ],
                    )
                )
            ],
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
            # No ``cast(Coef, ...)`` here: ``d`` is a ``BladeCoef`` (= dict[Blade,
            # Coef]) and the default is ``0`` (an int, ⊆ Coef), so ``d.get(b, 0)``
            # is already ``Coef``.  Casting is redundant -- and ty flags it as such
            # on the large generated modules (harmless warning, but it fails the
            # ``ty check`` gate once g4/g5 are generated).
            value=call(attribute("d", "get"), [constant(b), constant(0)]),
        )
        for b in blades
    ]
    body: list[ast.stmt] = [
        annotated_assign(
            "d", name_ref("BladeCoef"), call("dict", [name_ref("blade_coef")])
        ),
        # loud rejection of a non-canonical key (base's shared validator) --
        # canonical-but-foreign keys still fall through the ``d.get``s below
        # (the documented graded silent-drop)
        ast.Expr(value=call("_require_canonical_blades", [name_ref("d")])),
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


def class_header_stmts(
    doc: str, n: int, name: str, blades: Sequence[Blade]
) -> list[ast.stmt]:
    """The common class prefix: docstring, the class variables (DIMENSION + basis
    constants), the instance-variable fields, interchange, __eq__.

    DIMENSION and the ``e_*`` basis-constant ClassVars are emitted contiguously
    (before the ``coeff_*`` fields) so ``inject_region_markers`` can wrap them in
    one ``<Class> cls variables`` region, mirroring ``<Class> instance variables``.
    """
    return [
        class_doc_stmt(doc),
        dimension_decl(n),
        *basis_classvar_decls(name, blades),
        *field_decls(blades),
        from_blade_dict_method(blades),
        to_blade_dict_method(blades),
        eq_method([field_name(b) for b in blades]),
    ]


def is_close_method(type_name: str, fields: Sequence[str]) -> ast.FunctionDef:
    """``isclose``: defer to the ABC for a foreign type, else the
    symmetric ``math.isclose`` per field.

    Carries the same ``rel_tol``/``abs_tol`` params as
    ``MultiVectorBase.isclose`` and threads them to both the
    ``super()`` fallback and each per-field comparison.
    """
    return function_def(
        "isclose",
        [
            ast.If(
                not_(isinstance_(name_ref("other"), name_ref(type_name))),
                [
                    return_stmt(
                        super_call(
                            "isclose",
                            [
                                name_ref("other"),
                                name_ref("rel_tol"),
                                name_ref("abs_tol"),
                            ],
                        )
                    )
                ],
                [],
            ),
            return_stmt(call("bool", [bool_and([isclose_call(f) for f in fields])])),
        ],
        params=[
            argument("self"),
            argument("other"),
            argument("rel_tol"),
            argument("abs_tol"),
        ],
        defaults=[constant(0.0), constant(0.0)],
        returns=name_ref("bool"),
    )


def iter_method(blades: Sequence[Blade]) -> ast.FunctionDef:
    """``__iter__``: yield the component VALUES, one per field, in blade order.

    A value (vector, versor, full multivector, ...) reads as the numbers it holds,
    so ``list(v)`` / ``tuple(v)`` / ``np.array([list(v), ...])`` give the
    coefficients -- not one single-blade multivector per term.  All fields are
    yielded (dense, fixed length), so e.g. ``list(Vector(3, 0)) == [3, 0]``.
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
    """``return <TypeName>(...)`` as nodes.

    Only the full class ``G_n`` uses this (its same-type results: the linear ops,
    reverse, grade parts).  ``G_n`` is ``@typing.final``, so it constructs the
    concrete class directly -- the same as the graded/scalar types -- and its
    ``-> Self`` still holds (``Self`` is exactly ``G_n`` for a final class)."""
    return [return_stmt(construct(type_name, pairs))]


def isclose_call(field: str, other: str = "other") -> ast.expr:
    """``math.isclose(_require_float(self.<f>), _require_float(other.<f>),
    rel_tol=rel_tol, abs_tol=abs_tol)`` -- the symmetric per-field test, reading
    the enclosing ``isclose``'s ``rel_tol``/``abs_tol`` params and
    raising a clear error on a symbolic field via ``_require_float``."""
    return call(
        attribute("math", "isclose"),
        [
            call("_require_float", [attribute("self", field)]),
            call("_require_float", [attribute(other, field)]),
        ],
        rel_tol=name_ref("rel_tol"),
        abs_tol=name_ref("abs_tol"),
    )


def super_call(method: str, args: Sequence[ast.expr]) -> ast.expr:
    """``super().<method>(<args>)``."""
    return call(attribute(call("super", []), method), args)


def dim_mismatch_guard(cls_name: str, dim: int) -> ast.stmt:
    """``if n != <dim>: raise ValueError(...)``.

    A fixed-dimension type's dual is intrinsically at its own dimension (grade
    r -> n−r), so a mismatched ``n`` is an error -- there is no cross-dimension
    fallback.  ``n`` defaults to this algebra's dimension (so ``x.dual()`` just
    works); passing anything else is the error this guards."""
    return ast.If(
        ast.Compare(name_ref("n"), [ast.NotEq()], [constant(dim)]),
        [
            ast.Raise(
                exc=call(
                    "ValueError",
                    [constant(f"{cls_name}.dual is fixed at dimension {dim}")],
                ),
                cause=None,
            )
        ],
        [],
    )


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
    rename: Mapping[str, tuple[str, str]],
    cast: Callable[[ast.expr], ast.Call] = cast_self,
    owner: str | None = None,
    via_var: str | None = None,
) -> list[ast.stmt]:
    """cse temps + ``return cast(<T>, RType(...))`` (= result_block, as nodes).

    ``cast`` defaults to ``cast_self``; the versor sandwich passes ``cast_operand``
    so the return is typed as the operand (``_OperandT``), not ``Self``.
    When ``owner`` equals the result type (a same-type product, e.g.
    Versor * Versor -> Versor), construct via ``type(self)`` so subclasses
    are preserved; widening/grade-changing results keep the concrete class
    (a Vector subclass has no say over a Versor result).
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
    else:
        # Same-type OR grade-changing: both construct the concrete @typing.final
        # result type directly.  Same-type has no subclass to preserve via
        # type(self); grade-changing returns MultiVectorBase, so no cast (the old
        # cast(Self, Versor(...)) was unsound).  Every value type -- graded, scalar,
        # and the full G_n -- is now final, so the two arms coincide.
        stmts.append(return_stmt(construct(result_spec.name, pairs)))
    return stmts


def unary_stmt(
    result_spec: TypeSpec,
    out_exprs: Sequence[sympy.Expr],
    rename: Mapping[str, tuple[str, str]],
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
    # same-type result (owner == result) -> the concrete (now-final) class directly,
    # no type(self) needed; any other result wraps with cast.
    return (
        return_stmt(construct(result_spec.name, pairs))
        if owner is not None and owner == result_spec.name
        else return_stmt(cast(construct(result_spec.name, pairs)))
    )


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
    ``Self`` (the products).  The versor sandwich overrides ``param_name='x'``,
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
            self_spec, scalar_spec(n), gn_product, n, full_name
        )
        num_rename: Mapping[str, tuple[str, str]] = rename_map(
            self_spec.blades, scalar_spec(n).blades, param_name
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
    for rhs_spec in [scalar_spec(n), *graded_specs(n)]:
        # The same-type arm is NOT emitted when the exact-type early-out (#1
        # below, cast_self only) already covers it: the classes are
        # @typing.final, so no legal subtype can reach a ``case T()`` the
        # ``type(x) is T`` check missed -- the arm would be dead code repeating
        # the closed form.  A finality-violating runtime subclass falls to
        # ``case _`` and widens via ``_coerce`` -- correct, just not narrow.
        if cast is cast_self and rhs_spec == self_spec:
            continue
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
    # It fully replaces the same-type ``case T()`` arm (skipped in the loop above):
    # the classes are @typing.final, so nothing legal can be isinstance-T without
    # being exactly T.  Only for the Self-returning ops -- NOT the operand-typed
    # sandwich (cast_operand), where the same-type operand is rare so the extra
    # check would not pay for itself (its match keeps the same-type arm).
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
    type, each returning the **resolved concrete type** (e.g. ``Vector * Vector``
    -> ``Versor``).  So the operator/method types precisely at a known-type call
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
        # = Self), for ``+``/``-`` it adds a scalar (e.g. Bivector + scalar ->
        # Versor).  Both fall out of ``product_result(self, Scalar)``.
        num_spec: TypeSpec
        num_spec, _ = product_result(
            self_spec, scalar_spec(n), gn_product, n, full_name
        )
        stubs.append(stub(_number_union(), name_ref(num_spec.name)))
    rhs_spec: TypeSpec
    for rhs_spec in [scalar_spec(n), *graded_specs(n)]:
        result_spec: TypeSpec
        result_spec, _ = product_result(self_spec, rhs_spec, gn_product, n, full_name)
        stubs.append(stub(name_ref(rhs_spec.name), name_ref(result_spec.name)))
    stubs.append(stub(name_ref("MultiVectorBase"), name_ref(full_name)))
    return stubs


def alias_dispatch(
    alias: str,
    target: str,
    self_spec: TypeSpec,
    gn_product: Callable[[Gn, Gn], Gn],
    n: int,
    full_name: str,
    param_name: str = "rhs",
) -> list[ast.stmt]:
    """A precise-typed **alias**: ``@overload`` stubs (resolved per rhs, the same
    as ``target``'s) plus a one-line impl that delegates to ``target`` and returns
    ``MultiVectorBase``.

    For the methods/operators that are *defined as* a delegation of a dispatched
    product -- ``wedge``/``__xor__`` -> ``outer_product``, ``dot`` ->
    ``inner_product``, ``__lt__`` -> ``left_contraction``, ``__gt__`` ->
    ``right_contraction`` -- so the alias types as precisely as the method it
    forwards to instead of inheriting the base's imprecise ``-> Self``.  The body
    is a delegation (not a duplicated ``match``): the target already dispatches.
    """
    return [
        *product_overload_stubs(
            alias, self_spec, gn_product, n, full_name, param_name=param_name
        ),
        function_def(
            alias,
            [return_stmt(call(attribute("self", target), [name_ref(param_name)]))],
            params=[argument("self"), argument(param_name)],
            returns=name_ref("MultiVectorBase"),
        ),
    ]


def transform_factory_overrides(
    self_spec: TypeSpec,
    onto_types: Sequence[tuple[int, str]],
    method: str,
    param_name: str,
    wrapper: str,
    max_onto_grade: int,
) -> list[ast.stmt]:
    """Precise-typed override of a grade-preserving transform-*factory* classmethod
    (``project`` / ``reject`` / ``reflect``) on a **vector** graded type.

    ``base`` types these ``-> ComposableFunction[MultiVectorBase]`` (project/reject)
    / ``InvertibleFunction[MultiVectorBase]`` (reflect) -- imprecise, because the
    returned function's grade-preservation is invisible to the type.  A *vector*
    projected/rejected/reflected onto a **blade of any grade** stays a vector, so
    the factory applied to a ``Vector_n`` yields a ``Vector_n``.  Emit one precise
    ``@overload`` stub per grade-pure blade type in ``onto_types`` whose grade the
    method's runtime supports (``max_onto_grade`` -- all grades for ``project``;
    only <= 2, i.e. up to ``Bivector``, for ``reject``/``reflect`` until the
    higher-grade runtime lands, see ``generalize-reject-reflect-higher-grade``),
    each ``<param>: <BladeType> -> wrapper[Vector_n]``, then the ``MultiVectorBase |
    Sequence[MultiVectorBase]`` catch-all, then a one-line impl that delegates to
    ``super().<method>`` (runtime unchanged; base does the real work).  ``wrapper``
    is ``ComposableFunction`` for project/reject, ``InvertibleFunction`` for the
    involutive reflect.
    """
    vec: str = self_spec.name  # the value type these factories act on (Vector)
    catch_all_param: ast.expr = ast.BinOp(
        name_ref("MultiVectorBase"),
        ast.BitOr(),
        subscript(name_ref("Sequence"), name_ref("MultiVectorBase")),
    )

    def stub(param_ann: ast.expr, ret: ast.expr) -> ast.stmt:
        return function_def(
            method,
            [ast.Expr(constant(...))],
            params=[argument("cls"), argument(param_name, param_ann)],
            decorators=[attribute("typing", "overload"), name_ref("classmethod")],
            returns=ret,
        )

    precise_stubs: list[ast.stmt] = [
        stub(name_ref(blade_type), subscript(name_ref(wrapper), name_ref(vec)))
        for grade, blade_type in onto_types
        if grade <= max_onto_grade
    ]
    return [
        *precise_stubs,
        stub(
            catch_all_param,
            subscript(name_ref(wrapper), name_ref("MultiVectorBase")),
        ),
        function_def(
            method,
            [
                return_stmt(
                    call(attribute(call("super"), method), [name_ref(param_name)])
                )
            ],
            params=[argument("cls"), argument(param_name)],
            decorators=[name_ref("classmethod")],
            # Impl return is ``wrapper[Any]``, not ``wrapper[MultiVectorBase]``:
            # ``ComposableFunction``/``InvertibleFunction`` are INVARIANT in their
            # type param (``func: Callable[[V], V]`` uses V as input AND output), so
            # a precise overload return ``wrapper[Vector]`` is NOT assignable to
            # ``wrapper[MultiVectorBase]`` -- ty (correctly) rejects that as an
            # invalid overload.  ``wrapper[Any]`` is the gradual impl type every
            # overload return IS assignable to; the impl is never called directly
            # (only the overloads are), so ``Any`` here is harmless and callers
            # still get the precise ``wrapper[Vector]``.
            returns=subscript(name_ref(wrapper), attribute("typing", "Any")),
        ),
    ]


def passthrough_method_overrides(
    self_spec: TypeSpec,
    onto_types: Sequence[tuple[int, str]],
    method: str,
    param_name: str,
    max_onto_grade: int,
) -> list[ast.stmt]:
    """Precise-typed override of a project/reject/reflect PASS-THROUGH *instance*
    method (``projected_onto`` / ``rejected_away_from`` / ``reflected_across``) on a
    vector graded type.

    ``base`` types these ``-> MultiVectorBase`` (the factory's own imprecision); but a
    *vector* projected/rejected/reflected onto a blade stays a vector, so on a
    ``Vector_n`` the result is a ``Vector_n``.  The instance-method analog of
    :func:`transform_factory_overrides`: one precise ``@overload`` per grade-pure blade
    type the method's runtime supports (``max_onto_grade``), then the ``MultiVectorBase
    | Sequence[MultiVectorBase]`` catch-all, then a one-line impl delegating to
    ``super()`` (runtime unchanged; base does the real work).  The return is the plain
    *value* type (``Vector_n`` / ``MultiVectorBase``), NOT a ``ComposableFunction``
    wrapper -- so, unlike the factory case, the impl can return ``MultiVectorBase``
    directly (no invariance issue: ``Vector_n`` is assignable to it).
    """
    vec: str = self_spec.name
    catch_all_param: ast.expr = ast.BinOp(
        name_ref("MultiVectorBase"),
        ast.BitOr(),
        subscript(name_ref("Sequence"), name_ref("MultiVectorBase")),
    )

    def stub(param_ann: ast.expr, ret: ast.expr) -> ast.stmt:
        return function_def(
            method,
            [ast.Expr(constant(...))],
            params=[argument("self"), argument(param_name, param_ann)],
            decorators=[attribute("typing", "overload")],
            returns=ret,
        )

    precise_stubs: list[ast.stmt] = [
        stub(name_ref(blade_type), name_ref(vec))
        for grade, blade_type in onto_types
        if grade <= max_onto_grade
    ]
    return [
        *precise_stubs,
        stub(catch_all_param, name_ref("MultiVectorBase")),
        function_def(
            method,
            [
                return_stmt(
                    call(attribute(call("super"), method), [name_ref(param_name)])
                )
            ],
            params=[argument("self"), argument(param_name)],
            decorators=[],
            returns=name_ref("MultiVectorBase"),
        ),
    ]


# ==========================================================================
# The four generators (one per emitted construct)
# ==========================================================================


def generate_scalar(n: int, name: str, full_name: str) -> list[ast.stmt]:
    """The grade-0 ``ScalarN`` type of 𝒢ₙ, hand-built as `ast` nodes (level C).

    One per algebra (``Scalar``), emitted into that
    algebra's ``gN.py`` -- so ``dual`` can name the same-module pseudoscalar type
    (``Scalar.dual -> Trivector``) without a circular import.  ``full_name`` is
    the algebra's full class (``G``), needed by ``unary_result`` to
    resolve the dual's result type."""
    self_scalar_field: ast.expr = attribute("self", field_name(()))

    def scalar_const(
        value: ast.expr,
    ) -> ast.expr:  # ScalarN(coeff_scalar=value) -- ScalarN is @final, so concrete
        return construct(name, [(field_name(()), value)])

    def scalar_const_coef(
        value: ast.expr,
    ) -> ast.expr:  # cast(typing.Self, Scalar(coeff_scalar=cast(Coef, value)))
        return scalar_const(cast_coef(value))

    def mul_expr(a: ast.expr, b: ast.expr) -> ast.BinOp:
        return ast.BinOp(left=a, op=ast.Mult(), right=b)

    # @final ScalarN: annotate the concrete class, not ``typing.Self``.  ty does
    # not reliably collapse ``Self`` to the class even under ``@final`` on a large
    # module, so ``return Scalar(...)`` against ``-> typing.Self`` is (wrongly, but
    # unavoidably) flagged there; ``-> Scalar`` matches exactly and is a valid
    # override of base's ``-> Self`` (for the receiver, Self ≡ the class).
    self_ann: ast.expr = name_ref(name)
    coef_ann: ast.expr = name_ref("Coef")
    # The *implementation* return type of an overloaded product/sum method: its
    # per-rhs overloads return the resolved concrete types (Vector, Bivector,
    # ...), siblings under MultiVectorBase, so the impl's own return must be their
    # common supertype -- exactly as the graded types do (see generate_graded_type).
    mvb_ann: ast.expr = name_ref("MultiVectorBase")
    number_types: list[ast.expr] = [
        name_ref("int"),
        name_ref("float"),
        attribute("sympy", "Expr"),
    ]
    # dual: grade 0 -> grade n = THIS algebra's pseudoscalar type, resolved
    # symbolically (Scalar.dual -> Vector, Scalar -> Bivector, Scalar ->
    # Trivector).  Declared precisely (no unsound Self cast), mirroring the graded
    # types' ``dual_method``.
    dual_spec: TypeSpec
    dual_exprs: list[sympy.Expr]
    dual_spec, dual_exprs = unary_result(
        scalar_spec(n), lambda a: a.dual(n), n, full_name
    )
    dual_rename: Mapping[str, tuple[str, str]] = rename_map(scalar_spec(n).blades, ())

    body: list[ast.stmt] = [
        class_doc_stmt(scalar_doc(n)),
        dimension_decl(n),
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
        eq_method([field_name(())]),
        # The products/sums are the same machinery the graded types use
        # (product_overload_stubs + dispatch_method): per-rhs @overloads for a
        # precise static type (Scalar * Vector -> Vector, Scalar + Bivector ->
        # Versor, ...), an impl that constructs the resolved concrete type, and a
        # ``case _`` that coerces a foreign/Gn operand to G_n.  This replaces the
        # old bespoke bodies whose ``cast(Self, coeff * rhs)`` mis-claimed Scalar_n.
        *product_overload_stubs(
            "__mul__",
            scalar_spec(n),
            lambda a, b: a * b,
            n,
            full_name,
            number_case=True,
        ),
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
            returns=mvb_ann,
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
        *product_overload_stubs(
            "_geometric_product", scalar_spec(n), lambda a, b: a * b, n, full_name
        ),
        dispatch_method(
            scalar_spec(n),
            "_geometric_product",
            lambda a, b: a * b,
            n,
            full_name,
            ast.BinOp(name_ref("left"), ast.Mult(), name_ref("right")),
            return_type=mvb_ann,
        ),
        *product_overload_stubs(
            "outer_product",
            scalar_spec(n),
            lambda a, b: a.outer_product(b),
            n,
            full_name,
        ),
        dispatch_method(
            scalar_spec(n),
            "outer_product",
            lambda a, b: a.outer_product(b),
            n,
            full_name,
            call(attribute("left", "outer_product"), [name_ref("right")]),
            return_type=mvb_ann,
        ),
        # ``a ^ b`` (wedge operator) and the ``wedge`` alias -> outer_product
        # (base returns Self; ScalarN did not override either until now).
        *alias_dispatch(
            "__xor__",
            "outer_product",
            scalar_spec(n),
            lambda a, b: a.outer_product(b),
            n,
            full_name,
            param_name="other",
        ),
        *alias_dispatch(
            "wedge",
            "outer_product",
            scalar_spec(n),
            lambda a, b: a.outer_product(b),
            n,
            full_name,
        ),
        # inner_product: scalar . X == 0 under the Hestenes dot (grade 0 excluded),
        # so every overload resolves to Scalar_n (the zero) and the impl builds it.
        *product_overload_stubs(
            "inner_product",
            scalar_spec(n),
            lambda a, b: a.inner_product(b),
            n,
            full_name,
        ),
        dispatch_method(
            scalar_spec(n),
            "inner_product",
            lambda a, b: a.inner_product(b),
            n,
            full_name,
            call(attribute("left", "inner_product"), [name_ref("right")]),
            return_type=mvb_ann,
        ),
        # ``dot`` is the ``inner_product`` alias (base returns Self).
        *alias_dispatch(
            "dot",
            "inner_product",
            scalar_spec(n),
            lambda a, b: a.inner_product(b),
            n,
            full_name,
        ),
        # left/right contraction (Taylor p.103) + the ``<`` / ``>`` operators that
        # delegate to them -- same overloads + dispatch as the graded types, so
        # ``Scalar < Vector`` types precisely instead of the inherited -> Self.
        *product_overload_stubs(
            "left_contraction",
            scalar_spec(n),
            lambda a, b: a.left_contraction(b),
            n,
            full_name,
        ),
        dispatch_method(
            scalar_spec(n),
            "left_contraction",
            lambda a, b: a.left_contraction(b),
            n,
            full_name,
            call(attribute("left", "left_contraction"), [name_ref("right")]),
            return_type=mvb_ann,
        ),
        *alias_dispatch(
            "__lt__",
            "left_contraction",
            scalar_spec(n),
            lambda a, b: a.left_contraction(b),
            n,
            full_name,
            param_name="other",
        ),
        *product_overload_stubs(
            "right_contraction",
            scalar_spec(n),
            lambda a, b: a.right_contraction(b),
            n,
            full_name,
        ),
        dispatch_method(
            scalar_spec(n),
            "right_contraction",
            lambda a, b: a.right_contraction(b),
            n,
            full_name,
            call(attribute("left", "right_contraction"), [name_ref("right")]),
            return_type=mvb_ann,
        ),
        *alias_dispatch(
            "__gt__",
            "right_contraction",
            scalar_spec(n),
            lambda a, b: a.right_contraction(b),
            n,
            full_name,
            param_name="other",
        ),
        # +/- narrow by grade too: Scalar + Vector -> G, Scalar + Bivector ->
        # Versor, etc.  Same overloads + dispatch as the graded types.
        *product_overload_stubs(
            "__add__",
            scalar_spec(n),
            lambda a, b: a + b,
            n,
            full_name,
            number_case=True,
        ),
        dispatch_method(
            scalar_spec(n),
            "__add__",
            lambda a, b: a + b,
            n,
            full_name,
            ast.BinOp(name_ref("left"), ast.Add(), name_ref("right")),
            number_case=True,
            return_type=mvb_ann,
        ),
        function_def(
            "__radd__",
            [return_stmt(call(attribute("self", "__add__"), [name_ref("lhs")]))],
            params=[argument("self"), argument("lhs")],
            returns=self_ann,
        ),
        *product_overload_stubs(
            "__sub__",
            scalar_spec(n),
            lambda a, b: a - b,
            n,
            full_name,
            number_case=True,
        ),
        dispatch_method(
            scalar_spec(n),
            "__sub__",
            lambda a, b: a - b,
            n,
            full_name,
            ast.BinOp(name_ref("left"), ast.Sub(), name_ref("right")),
            number_case=True,
            return_type=mvb_ann,
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
            "isclose",
            [
                ast.If(
                    not_(isinstance_(name_ref("other"), name_ref(name))),
                    [
                        return_stmt(
                            call(
                                attribute(call("super", []), "isclose"),
                                [
                                    name_ref("other"),
                                    name_ref("rel_tol"),
                                    name_ref("abs_tol"),
                                ],
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
                                attribute("math", "isclose"),
                                [
                                    call("_require_float", [self_scalar_field]),
                                    call(
                                        "_require_float",
                                        [attribute("other", field_name(()))],
                                    ),
                                ],
                                rel_tol=name_ref("rel_tol"),
                                abs_tol=name_ref("abs_tol"),
                            )
                        ],
                    )
                ),
            ],
            params=[
                argument("self"),
                argument("other"),
                argument("rel_tol"),
                argument("abs_tol"),
            ],
            defaults=[constant(0.0), constant(0.0)],
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
                                construct(name, [(field_name(()), self_scalar_field)])
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
        # dual is now dimension-fixed (this ScalarN knows its algebra), so it
        # returns the resolved pseudoscalar type and raises on a mismatched n --
        # same shape as the graded types' dual_method.
        function_def(
            "dual",
            [
                dim_mismatch_guard(name, n),
                unary_stmt(
                    dual_spec,
                    dual_exprs,
                    dual_rename,
                    owner=name,
                    cast=lambda node: node,
                ),
            ],
            params=[argument("self"), argument("n", name_ref("int"))],
            defaults=[constant(n)],
            returns=name_ref(dual_spec.name),
        ),
    ]
    return [
        class_def(
            name,
            body,
            decorators=[
                attribute("typing", "final"),
                dataclass_decorator(eq=False, slots=True, frozen=True, repr=False),
            ],
        )
    ]


def generate_class(n: int, name: str) -> list[ast.stmt]:
    """The full all-blades G_n class, hand-built as `ast` nodes (level C)."""
    blades: list[Blade] = blades_for_dim(n)
    fields: list[str] = [field_name(b) for b in blades]
    rename: Mapping[str, tuple[str, str]] = rename_map(blades, blades)
    a_mv: Gn = Gn.from_blade_dict(
        {b: sympy.Symbol("a_" + blade_label(b)) for b in blades}
    )
    b_mv: Gn = Gn.from_blade_dict(
        {b: sympy.Symbol("b_" + blade_label(b)) for b in blades}
    )
    by_grade: dict[int, list[Blade]] = {
        g: [b for b in blades if len(b) == g] for g in range(n + 1)
    }
    # @final full class G: annotate the concrete class, not ``typing.Self`` (see
    # the ScalarN note).  ``return G(...)`` matches ``-> G`` exactly, and the
    # coerce-foreign-rhs branch's ``cast(Self, Gn*Gn)`` still matches since
    # ``Self <: G``.
    self_ann: ast.expr = name_ref(name)

    def bilinear(method: str, cross_node: ast.expr, result_mv: Gn) -> ast.FunctionDef:
        """A dense full-class product method (geometric/inner/outer/contraction):
        the closed form over ALL blades (cse'd), with an isinstance guard that
        coerces a foreign rhs to ``Gn`` and delegates via ``cross_node``."""
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
        """A full-class linear op (``__add__`` / ``__sub__``): normalize a bare
        number to the scalar part, coerce a foreign rhs through ``Gn``, else
        combine the fields pairwise with ``op_cls``."""
        return function_def(
            method,
            [
                # A bare number/Expr is the scalar part -- the
                # ``MultiVectorBase.__add__`` contract, which this override
                # must honor (the graded types' dispatch already does).
                # Normalize it before the representation check, which would
                # otherwise call ``.to_blade_dict()`` on a non-multivector.
                ast.If(
                    isinstance_(
                        name_ref("rhs"),
                        [
                            name_ref("int"),
                            name_ref("float"),
                            attribute("sympy", "Expr"),
                        ],
                    ),
                    [
                        assign(
                            "rhs",
                            call(attribute(name, "from_coef"), [name_ref("rhs")]),
                        )
                    ],
                    [],
                ),
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
        sign: int = pseudoscalar_squared_sign(len(b))
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
            [(field_name(b), constant(value if b == one_blade else 0)) for b in blades],
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
                    dim_mismatch_guard(name, n),
                    *result_stmts(
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
                ],
                params=[argument("self"), argument("n", name_ref("int"))],
                defaults=[constant(n)],
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
                        [ast.Expr(ast.YieldFrom(super_call("bases", [name_ref("n")])))],
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
        *class_header_stmts(docstring_for(n), n, name, blades),
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
        bilinear(
            "left_contraction",
            call(attribute("left", "left_contraction"), [name_ref("right")]),
            a_mv.left_contraction(b_mv),
        ),
        bilinear(
            "right_contraction",
            call(attribute("left", "right_contraction"), [name_ref("right")]),
            a_mv.right_contraction(b_mv),
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
        # i(a, b): the unit bivector of the plane two vectors span (classmethod);
        # narrowed to Bivector where one exists (n>=2), MultiVectorBase in 𝒢₁.
        *i_classmethod("Bivector" if n >= 2 else None),
    ]
    return [
        class_def(
            name,
            body,
            # @typing.final: nothing subclasses the full G_n (the graded types are
            # the value types; the general representation is Gn in gn.py), so it is
            # a leaf like the graded/scalar types -- which lets its methods construct
            # the concrete class directly instead of through type(self).
            decorators=[
                attribute("typing", "final"),
                dataclass_decorator(eq=False, slots=True, frozen=True, repr=False),
            ],
        ),
        *basis_constant_assignments(name, blades),
    ]


def generate_graded_type(spec: TypeSpec, n: int, full_name: str) -> list[ast.stmt]:
    """A graded subtype (Vector/Bivector/Trivector/Versor), as nodes (level C)."""
    blades: list[Blade] = list(spec.blades)
    fields: list[str] = [field_name(b) for b in blades]
    has_scalar: bool = () in blades
    unary_rename: Mapping[str, tuple[str, str]] = rename_map(spec.blades, ())
    numlike: list[ast.expr] = [
        name_ref("int"),
        name_ref("float"),
        attribute("sympy", "Expr"),
    ]
    # @final graded type: annotate the concrete class, not ``typing.Self`` (see the
    # ScalarN / full-class notes) -- e.g. ``Vector.reverse -> Vector``.
    self_ann: ast.expr = name_ref(spec.name)
    # The *implementation* return type of an overloaded product/sum method.  Its
    # overloads return the resolved concrete types (Versor, Bivector, ...), which
    # are NOT subtypes of one another nor of the full class G_n (all are siblings
    # under MultiVectorBase) -- so the impl's own return must be their one common
    # supertype, ``MultiVectorBase``, to stay consistent with its overloads (and
    # honest: the old ``-> Self`` claimed Vector while returning a Versor).
    mvb_ann: ast.expr = name_ref("MultiVectorBase")
    # ``self +/- scalar`` result type (e.g. Bivector + scalar -> Versor).  Used to
    # type __radd__/__rsub__, whose left operand is always a bare number, so their
    # return narrows by grade just like __add__'s scalar arm.  ``a - self`` and
    # ``self + a`` span the same grades ({0} plus self's), so one spec serves both.
    add_scalar_spec: TypeSpec
    add_scalar_spec, _ = product_result(
        spec, scalar_spec(n), lambda a, b: a + b, n, full_name
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
        # simply *declares* its resolved return type (e.g. Vector.even_part ->
        # Scalar) -- a valid narrowing of base's MultiVectorBase.  The impl
        # constructs that type directly (identity cast -> no unsound Self cast).
        result_spec, _ = unary_result(spec, gn_unary, n, full_name)
        return function_def(
            method,
            [unary_body(gn_unary, cast=lambda node: node)],
            returns=name_ref(result_spec.name),
        )

    def dual_method() -> ast.FunctionDef:
        # Like parity_part (declare the resolved grade-(n−r) type, construct it
        # directly, no unsound Self cast), but dual keeps the ``n`` param, which
        # DEFAULTS to this algebra's dimension (g2 -> 2, g3 -> 3), so ``x.dual()``
        # just works.  It is dimension-fixed, so any OTHER ``n`` raises rather than
        # falling back to G_n (dropping the old ``_coerce(self, G_n).dual(n)`` branch).
        result_spec, _ = unary_result(spec, lambda a: a.dual(n), n, full_name)
        return function_def(
            "dual",
            [
                dim_mismatch_guard(spec.name, n),
                unary_body(lambda a: a.dual(n), cast=lambda node: node),
            ],
            params=[argument("self"), argument("n", name_ref("int"))],
            defaults=[constant(n)],
            returns=name_ref(result_spec.name),
        )

    rev_pairs: list[tuple[str, ast.expr]] = []
    b: Blade
    for b in blades:
        f: str = field_name(b)
        sign: int = pseudoscalar_squared_sign(len(b))
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
    # Versor grade 2 -> Bivector; absent grade -> Scalar, the returned zero), so
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
        return_stmt(
            construct(scalar_spec(n).name, [(field_name(()), cast_coef(constant(0)))])
        )
    )

    body: list[ast.stmt] = [
        *class_header_stmts(graded_docstring(spec), n, spec.name, blades),
        # scalar-aware __mul__ / __rmul__ (the ABC versions would drop the scalar
        # for a type with no scalar field, so they are overridden here).  The
        # @overload stubs give the operator its precise result type per rhs (e.g.
        # Vector * Vector -> Versor) -- sound, since the impl returns exactly that
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
        # need no cast (the old cast(Self, Versor(...)) was unsound).
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
        # ``a ^ b`` (the wedge operator) and the ``wedge`` alias both delegate to
        # outer_product; give them its precise overloads (base returns Self).
        *alias_dispatch(
            "__xor__",
            "outer_product",
            spec,
            lambda a, b: a.outer_product(b),
            n,
            full_name,
            param_name="other",
        ),
        *alias_dispatch(
            "wedge",
            "outer_product",
            spec,
            lambda a, b: a.outer_product(b),
            n,
            full_name,
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
        # ``dot`` is the ``inner_product`` alias (base returns Self).
        *alias_dispatch(
            "dot",
            "inner_product",
            spec,
            lambda a, b: a.inner_product(b),
            n,
            full_name,
        ),
        # left/right contraction (Taylor p.103): grade-changing bilinear ops, so
        # they get the same precise overloads + fast dispatch as the products, and
        # the ``<`` / ``>`` operators delegate to them (as ``^`` does to wedge).
        *product_overload_stubs(
            "left_contraction", spec, lambda a, b: a.left_contraction(b), n, full_name
        ),
        dispatch_method(
            spec,
            "left_contraction",
            lambda a, b: a.left_contraction(b),
            n,
            full_name,
            call(attribute("left", "left_contraction"), [name_ref("right")]),
            return_type=mvb_ann,
        ),
        *alias_dispatch(
            "__lt__",
            "left_contraction",
            spec,
            lambda a, b: a.left_contraction(b),
            n,
            full_name,
            param_name="other",
        ),
        *product_overload_stubs(
            "right_contraction",
            spec,
            lambda a, b: a.right_contraction(b),
            n,
            full_name,
        ),
        dispatch_method(
            spec,
            "right_contraction",
            lambda a, b: a.right_contraction(b),
            n,
            full_name,
            call(attribute("left", "right_contraction"), [name_ref("right")]),
            return_type=mvb_ann,
        ),
        *alias_dispatch(
            "__gt__",
            "right_contraction",
            spec,
            lambda a, b: a.right_contraction(b),
            n,
            full_name,
            param_name="other",
        ),
        # +/- also narrow by grade: scalar + bivector -> Versor, etc.  Overload them
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
            # type (e.g. Bivector + scalar -> Versor); just forward.
            [return_stmt(call(attribute("self", "__add__"), [name_ref("lhs")]))],
            params=[argument("self"), argument("lhs", _number_union())],
            returns=radd_ann,
        ),
        function_def(
            "__rsub__",
            [
                return_stmt(
                    call(
                        attribute(ast.UnaryOp(ast.USub(), name_ref("self")), "__add__"),
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
        dual_method(),
    ]

    def bivector_extras() -> list[ast.stmt]:
        extras: list[ast.stmt] = []
        # exp of a bivector is a versor -- the exponential map onto the even
        # subalgebra.  A thin narrowing override (like ``dual``): the closed
        # form is transcendental, so the body delegates to the shared
        # ``MultiVectorBase.exp`` and only narrows the static return type to
        # this algebra's Versor (which the dispatching-add construction already
        # produces at runtime).
        extras.append(
            function_def(
                "exp",
                method_doc_stmts("exp")
                + [
                    return_stmt(
                        call(
                            attribute("typing", "cast"),
                            [
                                name_ref("Versor"),
                                call(
                                    attribute("MultiVectorBase", "exp"),
                                    [name_ref("self")],
                                ),
                            ],
                        )
                    )
                ],
                returns=name_ref("Versor"),
            )
        )
        # .i(): the bivector's unit plane -- itself, normalized (-> Bivector).
        extras.append(i_extractor("normalize", "Bivector"))
        return extras

    def versor_extras() -> list[ast.stmt]:
        extras: list[ast.stmt] = []
        extras.append(
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
                # grade-2 part normalized: r_vector_part(2) -> Bivector (Literal
                # overload), normalize -> Self, so the unit plane is a Bivector.
                returns=name_ref("Bivector"),
            )
        )
        # Versor conjugation  R x R^-1  -- the versor sandwich, GRADE-PRESERVING:
        # the derived closed form's support is exactly x's grades (the would-be
        # higher grades cancel symbolically), so each operand returns its own
        # type (Vector->Vector, Bivector->Bivector, ...) with no projection.
        extras.append(
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
        # .i(): the versor's unit plane of rotation (alias of plane_of_rotation);
        # -> Bivector.
        extras.append(i_extractor("plane_of_rotation", "Bivector"))
        return extras

    def odd3_extras() -> list[ast.stmt]:
        extras: list[ast.stmt] = []
        # The "cast" half of the opt-in query+cast: an Odd_3 value (grades {1,3}) is
        # a Vector when its grade-3 part vanishes and a Trivector when its grade-1
        # part vanishes.  The product return type stays Odd_3 (operation-based -- see
        # tasks/reference/generated-product-typing.md); these narrow explicitly,
        # raising if the discarded grade is nonzero.  The "query" half is the
        # inherited is_vector()/is_trivector()/grades().
        cast_name: str
        pred: str
        target: str
        pairs: Sequence[tuple[str, ast.expr]]
        why: str
        for cast_name, pred, target, pairs, why in (
            (
                "to_vector",
                "is_vector",
                "Vector",
                [
                    ("coeff_e_1", attribute("self", "coeff_e_1")),
                    ("coeff_e_2", attribute("self", "coeff_e_2")),
                    ("coeff_e_3", attribute("self", "coeff_e_3")),
                ],
                "grade-3 (e_123) part is nonzero",
            ),
            (
                "to_trivector",
                "is_trivector",
                "Trivector",
                [("coeff_e_123", attribute("self", "coeff_e_123"))],
                "grade-1 (vector) part is nonzero",
            ),
        ):
            extras.append(
                function_def(
                    cast_name,
                    [
                        class_doc_stmt(
                            f"Narrow this ``Odd_3`` to ``{target}`` -- raises "
                            f"``ValueError`` if the {why}."
                        ),
                        ast.If(
                            test=ast.UnaryOp(
                                op=ast.Not(),
                                operand=call(attribute("self", pred), []),
                            ),
                            body=[
                                ast.Raise(
                                    exc=call(
                                        "ValueError",
                                        [
                                            constant(
                                                f"Odd_3 is not a {target}: its {why}."
                                            )
                                        ],
                                    ),
                                    cause=None,
                                )
                            ],
                            orelse=[],
                        ),
                        return_stmt(construct(target, pairs)),
                    ],
                    params=[argument("self")],
                    returns=name_ref(target),
                )
            )
        return extras

    def vector_extras() -> list[ast.stmt]:
        extras: list[ast.stmt] = []
        # project/reject/reflect of a vector onto a blade are grade-preserving (the
        # result is a vector), so narrow the base's MultiVectorBase-typed factory
        # classmethods to the precise vector type -- one @overload per grade-pure
        # blade type the method's runtime supports.  project works onto ANY blade
        # grade; reject/reflect only up to a bivector today (grade 3+ raises at
        # runtime -- see generalize-reject-reflect-higher-grade), so they cap at
        # grade 2.  reflect is an involution -> InvertibleFunction; project/reject
        # -> ComposableFunction.
        onto_types: list[tuple[int, str]] = [
            (len(bs.blades[0]), bs.name)
            for bs in graded_specs(n)
            if len({len(b) for b in bs.blades}) == 1  # grade-pure (excludes Versor)
        ]
        extras.extend(
            transform_factory_overrides(
                spec, onto_types, "project", "onto", "ComposableFunction", n
            )
        )
        extras.extend(
            transform_factory_overrides(
                spec, onto_types, "reject", "away_from", "ComposableFunction", 2
            )
        )
        extras.extend(
            transform_factory_overrides(
                spec, onto_types, "reflect", "across", "InvertibleFunction", 2
            )
        )
        # The value-returning pass-through instance methods (base delegates them to
        # the factories above): narrow their -> MultiVectorBase to the concrete vector
        # type, same grade caps as the factories (project any grade; reject/reflect
        # <= bivector).
        extras.extend(
            passthrough_method_overrides(spec, onto_types, "projected_onto", "onto", n)
        )
        extras.extend(
            passthrough_method_overrides(
                spec, onto_types, "rejected_away_from", "away_from", 2
            )
        )
        extras.extend(
            passthrough_method_overrides(
                spec, onto_types, "reflected_across", "across", 2
            )
        )
        # i(a, b): the unit bivector of the plane two vectors span (classmethod).
        # Narrow it, plus the two inherited from-vectors builders, to this
        # algebra's fixed-grade result -- but only where that grade exists (n>=2;
        # 𝒢₁ has no bivector/versor, so they stay MultiVectorBase there).
        precise_bivector: str | None = "Bivector" if n >= 2 else None
        extras.extend(i_classmethod(precise_bivector))
        if n >= 2:
            # bivector_from_vectors(a, b) -> Bivector, versor_from_vectors(from, to)
            # -> Versor: base types both -> MultiVectorBase, but the wedge / versor
            # of two same-algebra vectors is that algebra's Bivector / Versor.
            extras.extend(
                inherited_classmethod_narrowing(
                    "bivector_from_vectors", ["a", "b"], "Bivector"
                )
            )
            extras.extend(
                inherited_classmethod_narrowing(
                    "versor_from_vectors", ["from_vector", "to_vector"], "Versor"
                )
            )
        if n == 2:
            # rotate_90_degrees() = v * e_12 -- 𝒢₂ only.  There the e₁e₂ plane is
            # the whole space, so right-multiplying by the unit pseudoscalar is a
            # pure quarter turn; in 𝒢₃+ the same product sends an e₃ component to
            # a trivector -- the footgun that got the old general-dimension
            # version removed (transforms.py, module docstring).  Emitted as the
            # derived closed form of that product (unary_result over symbolic
            # coefficients, like cross), so the turn is exact: no versor, no
            # cos/sin.  Vector -> Vector; the module-level rotate_90_degrees()
            # factory (generate_quarter_turn) wraps it as an InvertibleFunction.
            turn_spec: TypeSpec
            turn_exprs: list[sympy.Expr]
            turn_spec, turn_exprs = unary_result(
                spec,
                lambda a: a * Gn.from_blade_dict({(1, 2): 1}),
                n,
                full_name,
            )
            extras.append(
                function_def(
                    "rotate_90_degrees",
                    [class_doc_stmt(ROTATE_90_METHOD_DOC)]
                    + result_block_stmts(
                        turn_spec,
                        turn_exprs,
                        rename_map(spec.blades, []),
                        owner=spec.name,
                    ),
                    returns=name_ref(turn_spec.name),
                )
            )
            # sine(a, b) = (a ∧ b).coeff_e_12 / (|a| |b|) -- the SIGNED sine of
            # the angle from a to b, 𝒢₂ only (Decision 8 in the task doc: a
            # scalar, not a bivector -- "sometimes we just want the number").  In
            # 𝒢₂ the wedge has one component (the signed area a₁b₂ − a₂b₁), so this
            # is a signed scalar; swapping a, b negates it -- the oriented turn
            # direction mvp uses for which-side-of-an-edge tests, unlike the
            # unsigned MultiVectorBase.abs_sin.  Mirrors cosine/abs_sin's
            # `* abs**-1` idiom and reuses the generated wedge; raises on a
            # zero-length operand (division), matching cosine.  Vector -> Coef.
            extras.append(
                function_def(
                    "sine",
                    [class_doc_stmt(SINE_METHOD_DOC)]
                    + [
                        # The angle (hence its sine) is undefined for the zero vector;
                        # raise a clear ValueError rather than let the `* abs**-1`
                        # division fail cryptically -- matching MultiVectorBase.cosine /
                        # abs_sin and the Lean proofs' nonzero hypothesis.
                        ast.If(
                            parse_expr(
                                "self == type(self).zero()"
                                " or other == type(other).zero()"
                            ),
                            [
                                ast.Raise(
                                    exc=call(
                                        "ValueError",
                                        [
                                            constant(
                                                "sine (the angle) is undefined for"
                                                " the zero vector"
                                            )
                                        ],
                                    ),
                                    cause=None,
                                )
                            ],
                            [],
                        ),
                        return_stmt(
                            parse_expr(
                                "(self ^ other).coeff_e_12"
                                " * (abs(self) ** (-1)) * (abs(other) ** (-1))"
                            )
                        ),
                    ],
                    params=[
                        argument("self"),
                        argument("other", name_ref(spec.name)),
                    ],
                    returns=name_ref("Coef"),
                )
            )
        if n == 3:
            # cross(a, b) = (a ∧ b) I₃⁻¹ -- 𝒢₃ only (only there is the dual of a
            # bivector a vector).  A narrowing override of the base pass-through
            # (which delegates to vectorcalc.cross): the same-algebra Vector arm
            # gets the derived closed form (no runtime wedge/dual objects); every
            # other operand falls back to MultiVectorBase.cross, which handles Gn
            # mixing and raises vectorcalc's guard errors.  Typed like the
            # products: a precise Vector -> Vector overload plus a MultiVectorBase
            # catch-all over a MultiVectorBase-typed impl (Liskov-compatible).
            cross_spec: TypeSpec
            cross_exprs: list[sympy.Expr]
            cross_spec, cross_exprs = product_result(
                spec,
                spec,
                # dual() is typed MultiVectorBase on base; on a Gn operand it is a
                # Gn at runtime, which product_result's signature wants.
                lambda a, b: cast(Gn, a.outer_product(b).dual(3)),
                n,
                full_name,
            )
            cross_rename: Mapping[str, tuple[str, str]] = rename_map(
                spec.blades, spec.blades, "other"
            )

            def cross_stub(param_ann: ast.expr, ret: ast.expr) -> ast.stmt:
                return function_def(
                    "cross",
                    [ast.Expr(constant(...))],
                    params=[argument("self"), argument("other", param_ann)],
                    decorators=[attribute("typing", "overload")],
                    returns=ret,
                )

            extras.append(cross_stub(name_ref(spec.name), name_ref(cross_spec.name)))
            extras.append(
                cross_stub(name_ref("MultiVectorBase"), name_ref("MultiVectorBase"))
            )
            extras.append(
                function_def(
                    "cross",
                    method_doc_stmts("cross")
                    + [
                        # exact-type early-out, same idiom as the products: the
                        # classes are @typing.final, so `type(other) is Vector`
                        # is the whole same-algebra test.
                        ast.If(
                            test=ast.Compare(
                                call("type", [name_ref("other")]),
                                [ast.Is()],
                                [name_ref(spec.name)],
                            ),
                            body=result_block_stmts(
                                cross_spec, cross_exprs, cross_rename, owner=spec.name
                            ),
                            orelse=[],
                        ),
                        return_stmt(
                            call(
                                attribute("MultiVectorBase", "cross"),
                                [name_ref("self"), name_ref("other")],
                            )
                        ),
                    ],
                    params=[
                        argument("self"),
                        argument("other", name_ref("MultiVectorBase")),
                    ],
                    returns=name_ref("MultiVectorBase"),
                )
            )
        return extras

    # Per-type extras: each grade's special methods, built above as a named phase
    # that RETURNS its statements (reading the enclosing scope but never mutating it),
    # appended here so the whole decision reads as one unit.
    match spec.name:
        case "Bivector":
            body += bivector_extras()
        case "Versor":
            body += versor_extras()
        case "Odd_3":
            body += odd3_extras()
        case "Vector":
            body += vector_extras()
        case _:
            # grade-pure types with no extras (Trivector, Scalar, higher KVectors)
            pass
    return [
        class_def(
            spec.name,
            body,
            decorators=[
                attribute("typing", "final"),
                dataclass_decorator(eq=False, slots=True, frozen=True, repr=False),
            ],
        ),
        *basis_constant_assignments(spec.name, blades),
    ]


def generate_quarter_turn(name: str) -> list[ast.stmt]:
    """The module-level ``rotate_90_degrees()`` factory -- 𝒢₂ only (level C).

    Emits::

        def rotate_90_degrees() -> InvertibleFunction[Vector]:
            def forward(vector: Vector) -> Vector:   # guard + the method
            def backward(vector: Vector) -> Vector:  # guard + closed form of v * -e_12
            def interpolate(t: float) -> ComposableFunction[Vector]:
                # plane_rotation(e_1, e_2)(t * pi / 2); the exact turn at t >= 1
            return InvertibleFunction(func=forward, inverse=backward, ...,
                                      linearity=Linearity.LINEAR)

    Both nested functions reject anything that is not exactly a ``Vector`` with a
    ``TypeError`` (the classes are ``@typing.final``, so ``type(x) is Vector`` is
    the whole test), matching ``plane_rotation``'s grade check.  The inverse's
    body is derived like the method's -- ``unary_result`` over ``v * -e_12`` --
    not hand-written, so the two closed forms cannot drift apart.  The whole
    function and its body carry ``rotate_90_degrees factory`` / ``... body``
    doc-region markers for a book to ``literalinclude``.
    """
    vspec: TypeSpec = resolve([(1,), (2,)], 2, name)
    vec: str = vspec.name

    def guard() -> ast.stmt:
        return ast.If(
            ast.Compare(
                call("type", [name_ref("vector")]), [ast.IsNot()], [name_ref(vec)]
            ),
            [
                ast.Raise(
                    exc=call(
                        "TypeError",
                        [
                            ast.BinOp(
                                constant(
                                    "rotate_90_degrees takes a grade-1 "
                                    f"{vec} of 𝒢₂; got "
                                ),
                                ast.Add(),
                                attribute(
                                    call("type", [name_ref("vector")]), "__name__"
                                ),
                            )
                        ],
                    ),
                    cause=None,
                )
            ],
            [],
        )

    inv_spec: TypeSpec
    inv_exprs: list[sympy.Expr]
    inv_spec, inv_exprs = unary_result(
        vspec, lambda a: a * Gn.from_blade_dict({(1, 2): -1}), 2, name
    )
    inv_rename: Mapping[str, tuple[str, str]] = {
        "a_" + blade_label(b): ("vector", field_name(b)) for b in vspec.blades
    }
    forward: ast.stmt = function_def(
        "forward",
        [guard(), return_stmt(call(attribute("vector", "rotate_90_degrees")))],
        params=[argument("vector", name_ref(vec))],
        returns=name_ref(vec),
    )
    backward: ast.stmt = function_def(
        "backward",
        [guard()] + result_block_stmts(inv_spec, inv_exprs, inv_rename, owner=vec),
        params=[argument("vector", name_ref(vec))],
        returns=name_ref(vec),
    )
    interpolate: ast.stmt = function_def(
        "interpolate",
        [
            ast.If(
                ast.Compare(name_ref("t"), [ast.GtE()], [constant(1.0)]),
                [return_stmt(call("rotate_90_degrees"))],
                [],
            ),
            return_stmt(
                call(
                    call("plane_rotation", [name_ref("e_1"), name_ref("e_2")]),
                    [
                        ast.BinOp(
                            ast.BinOp(
                                name_ref("t"), ast.Mult(), attribute("math", "pi")
                            ),
                            ast.Div(),
                            constant(2),
                        )
                    ],
                )
            ),
        ],
        params=[argument("t", name_ref("float"))],
        returns=subscript(name_ref("ComposableFunction"), name_ref(vec)),
    )
    body: list[ast.stmt] = [
        class_doc_stmt(ROTATE_90_FACTORY_DOC),
        marker("doc-region-begin rotate_90_degrees body"),
        forward,
        backward,
        interpolate,
        # ast.Call by hand: astbuild.call's own first parameter is named
        # ``func``, which collides with InvertibleFunction's ``func=`` keyword.
        return_stmt(
            ast.Call(
                func=name_ref("InvertibleFunction"),
                args=[],
                keywords=[
                    ast.keyword(arg="func", value=name_ref("forward")),
                    ast.keyword(arg="latex_repr", value=constant(r"R_{\pi/2}")),
                    ast.keyword(arg="inverse", value=name_ref("backward")),
                    ast.keyword(arg="latex_repr_inv", value=constant(r"R_{-\pi/2}")),
                    ast.keyword(arg="interpolate", value=name_ref("interpolate")),
                    ast.keyword(
                        arg="linearity", value=attribute("Linearity", "LINEAR")
                    ),
                ],
            )
        ),
        marker("doc-region-end rotate_90_degrees body"),
    ]
    return [
        marker("doc-region-begin rotate_90_degrees factory"),
        function_def(
            "rotate_90_degrees",
            body,
            params=[],
            returns=subscript(name_ref("InvertibleFunction"), name_ref(vec)),
        ),
        marker("doc-region-end rotate_90_degrees factory"),
    ]


def generate_constants(n: int, name: str) -> list[ast.stmt]:
    """Module-level basis constants for one algebra, hand-built as nodes (level C).

    Each constant is emitted at its **resolved graded type** -- the smallest
    registered type covering its blade (``zero``/``one`` -> ``Scalar_n``, a lone
    vector blade -> ``Vector_n``, ``e_12`` -> ``Bivector_n``, the pseudoscalar ->
    the top-grade type), not the full class ``G_n``.  So ``3 * e_1 + 4 * e_2``
    stays a ``Vector`` (matching the printed ``3e₁ + 4e₂``), while a general
    multivector is still reachable via the full class's own constant ``G_n.e_1``
    or a direct ``G_n(...)`` / ``Gn`` construction.  ``gn.py`` is generated
    separately and keeps its ``Gn`` constants (it has no graded subtypes)."""
    nonempty: list[Blade] = [b for b in blades_for_dim(n) if b != ()]
    scalar_name: str = scalar_spec(n).name
    nodes: list[ast.stmt] = [
        annotated_assign(
            "zero",
            name_ref(scalar_name),
            call(attribute(scalar_name, "from_scalar"), [constant(0)]),
        ),
        annotated_assign(
            "one",
            name_ref(scalar_name),
            call(attribute(scalar_name, "from_scalar"), [constant(1)]),
        ),
    ]
    b: Blade
    for b in nonempty:
        graded_name: str = resolve([b], n, name).name
        nodes.append(
            annotated_assign(
                blade_label(b),
                name_ref(graded_name),
                call(
                    attribute(graded_name, "from_blade_dict"),
                    [ast.Dict(keys=[constant(b)], values=[constant(1)])],
                ),
            )
        )
    exported: list[str] = [
        name,
        scalar_spec(n).name,
        *(s.name for s in graded_specs(n)),
        "zero",
        "one",
    ]
    exported += [blade_label(b) for b in nonempty]
    if n == 2:
        # the 𝒢₂-only InvertibleFunction factory (generate_quarter_turn)
        exported.append("rotate_90_degrees")
    nodes.append(
        assign("__all__", ast.List(elts=[constant(s) for s in exported], ctx=_LOAD))
    )
    return nodes


# ==========================================================================
# File headers, constants, and the generation driver
# ==========================================================================


def header(name: str, n: int) -> str:
    # _OperandT (the sandwich operand TypeVar) is only used by the Versor class,
    # which exists for n >= 2; importing it for G would be unused (F401).
    operand_import: str = "\n    _OperandT," if n >= 2 else ""
    # The 𝒢₂ rotate_90_degrees() factory (generate_quarter_turn) needs Linearity
    # and plane_rotation (for its interpolation law); importing them elsewhere
    # would be unused (F401).  transforms imports only base/functions, so g2
    # importing it is acyclic.
    functions_import: str = "from gacalc.functions import Linearity\n" if n == 2 else ""
    transforms_import: str = (
        "from gacalc.transforms import plane_rotation\n" if n == 2 else ""
    )
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
import math
import typing
from collections.abc import Generator, Sequence

import numpy as np
import sympy

from gacalc.base import (
    ComposableFunction,
    InvertibleFunction,
    MultiVectorBase,
    BladeCoef,
    Coef,
    _coef_eq,
    _coerce,
    _require_canonical_blades,
    _require_float,{operand_import}
)
{functions_import}from gacalc.gn import Gn
{transforms_import}"""


# Every algebra the generator knows how to emit.  Which of these are actually
# generated on a given run is chosen by the ``GACALC_DIMS`` env var (below), so
# the expensive high dimensions are NOT built on every ``make shell``.
ALL_ALGEBRAS: list[tuple[int, str, str]] = [
    (1, "G", "g1.py"),
    (2, "G", "g2.py"),
    (3, "G", "g3.py"),
    (4, "G", "g4.py"),
    (5, "G", "g5.py"),
]


def selected_dims() -> set[int]:
    """Dimensions to generate this run, from ``GACALC_DIMS`` (default ``1,2,3``).

    Generation cost grows superlinearly (𝒢₃ ≈ 23 s, 𝒢₄ ≈ 5 min, 𝒢₅ ≈ 87 min --
    see ``tasks/reference/generated-algebra-generation-cost.md``), so 𝒢₄/𝒢₅ are
    **release-only**: dev (``make shell`` / ``make generate``) uses the default and
    builds only g1--g3, while ``make dist`` / ``make release`` set
    ``GACALC_DIMS=1,2,3,4,5`` so g4/g5 are generated once at publish and baked into
    the sdist/wheel.  ``make generate-all`` / ``make test-all-dims`` opt in locally.
    """
    raw: str = os.environ.get("GACALC_DIMS", "1,2,3")
    return {int(part) for part in raw.split(",") if part.strip()}


ALGEBRAS: list[tuple[int, str, str]] = [
    entry for entry in ALL_ALGEBRAS if entry[0] in selected_dims()
]


def ruff_format(paths: Sequence[str]) -> None:
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
    """Generate every algebra in ``ALGEBRAS`` into ``src/gacalc/gN.py``.

    For each ``(n, name, filename)``: build the module body as ``ast`` nodes
    (``ScalarN``, then the full ``G_n``, then the graded types, then the module
    constants), wrap it in doc-region markers, render to text with the raw header
    prepended, write the file; finally ruff-format all of them.  See the module
    docstring for the pipeline this drives.
    """
    written: list[str] = []
    # Each module's body is a list of `ast` statement nodes (the per-construct
    # generators build them directly), rendered to source with `ast.unparse`
    # (module_source).  The file header -- copyright comment + imports -- stays raw
    # text (comments can't live in an AST) and is prepended.

    n: int
    name: str
    filename: str
    for n, name, filename in ALGEBRAS:
        # The full G first, then Scalar (grade 0), then the graded types (which
        # construct Scalar results).  All in the one module, so Scalar.dual can name
        # the pseudoscalar type with no cross-module (circular) import.  Emission
        # order is cosmetic: `from __future__ import annotations` makes annotations
        # lazy and method bodies resolve names at call time; only generate_constants
        # must stay last (its module-level bindings run at import).
        nodes: list[ast.stmt] = generate_class(n, name)
        nodes += generate_scalar(n, "Scalar", name)
        spec: TypeSpec
        for spec in graded_specs(n):
            nodes += generate_graded_type(spec, n, name)
        if n == 2:
            nodes += generate_quarter_turn(name)
        nodes += generate_constants(n, name)
        # Fill in a docstring on every generated method that lacks one (see
        # CUSTOM_METHOD_DOCS): specialized text for g1--g3, copied base docstrings
        # otherwise.  Runs before marker injection / rendering.
        inject_method_docstrings(nodes, n, name)
        module_body: str = module_source(inject_region_markers(nodes))
        source: str = header(name, n) + "\n\n" + module_body + "\n"
        with open(out_path(filename), "w") as f:
            f.write(source)
        written.append(out_path(filename))
        sys.stdout.write(f"wrote {os.path.normpath(out_path(filename))}\n")
    ruff_format(written)


if __name__ == "__main__":
    main()
