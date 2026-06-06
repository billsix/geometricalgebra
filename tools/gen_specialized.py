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

import inspect
import os
import re
import subprocess
import sys
from collections import namedtuple
from itertools import chain, combinations

import sympy

# allow running from the repo root without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from geometricalgebra.base import AbstractMultiVector  # noqa: E402
from geometricalgebra.gn import Gn  # noqa: E402


def emit_docstring(lines, method_name, indent="        ") -> None:
    """Copy ``AbstractMultiVector.<method_name>``'s docstring onto the generated
    override, so the specialized classes carry the *same* Hestenes notation as the
    shared base.  ``base.py`` is the single source of truth; this is a no-op when
    the base method has no docstring (keeps pure-plumbing overrides clean).
    """
    member = getattr(AbstractMultiVector, method_name, None)
    doc = inspect.getdoc(member) if member is not None else None
    if not doc:
        return
    lines.append(f'{indent}"""')
    for line in doc.splitlines():
        lines.append(f"{indent}{line}".rstrip())
    lines.append(f'{indent}"""')


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


def format_assignment(lhs: str, expr, indent: str, render) -> list[str]:
    """Render ``<lhs>=<expr>,`` for a constructor kwarg, wrapping long sums.

    Additive terms are ordered by grade (see ``term_grade_key``) for readability;
    this only reorders the written source -- the computed value is unchanged.
    Short expressions stay on one line; long ones are split across lines one
    additive term at a time so no line exceeds the formatter's limit.  ``render``
    turns a sympy expression into source text (e.g. ``self.e_1 * rhs.e_2``).
    """
    expr = sympy.sympify(expr)
    if not expr.free_symbols:
        # a constant component (e.g. an identically-zero blade) -- cast to the
        # field type so the checker doesn't see a bare Literal.
        return [f"{indent}{lhs}=typing.cast(numbers.Real, {render(expr)}),"]

    terms = (
        sorted(expr.as_ordered_terms(), key=term_grade_key) if expr.is_Add else [expr]
    )
    fragments: list[str] = []
    for i, term in enumerate(terms):
        s = render(term)
        if i == 0:
            fragments.append(s)
        elif s.startswith("-"):
            fragments.append(f"- {s[1:].lstrip()}")
        else:
            fragments.append(f"+ {s}")

    inline = f"{indent}{lhs}={' '.join(fragments)},"
    if len(inline) <= 88:
        return [inline]

    cont = indent + "    "
    return [f"{indent}{lhs}=(", *(f"{cont}{frag}" for frag in fragments), f"{indent}),"]


def blade_literal(blade: tuple[int, ...]) -> str:
    """Python source for the blade tuple key, e.g. '()' or '(1,)' or '(1, 2)'."""
    if blade == ():
        return "()"
    if len(blade) == 1:
        return f"({blade[0]},)"
    return "(" + ", ".join(str(i) for i in blade) + ")"


def _sub(k: int) -> str:
    return "".join("₀₁₂₃₄₅₆₇₈₉"[int(d)] for d in str(k))


def _sup(k: int) -> str:
    return "".join("⁰¹²³⁴⁵⁶⁷⁸⁹"[int(d)] for d in str(k))


def generic_docstring(n: int) -> str:
    """Standard class docstring for any dimension (fallback for unknown n)."""
    bl = blades_for_dim(n)
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


def emit_construct_return(lines, name, pairs, indent="        ") -> None:
    """Emit ``result = name(field=expr, ...)`` then a Self-cast return."""
    ap = lines.append
    ap(f"{indent}result = {name}(")
    for field, expr in pairs:
        ap(f"{indent}    {field}={expr},")
    ap(f"{indent})")
    ap(f"{indent}return typing.cast(typing.Self, result)")


def emit_bilinear(
    lines, name, method, cross, result_mv, blades, fields, render
) -> None:
    """Emit a closed-form bilinear method (product / inner / outer) from a Gn result.

    ``cross`` is the expression used when ``rhs`` is some other representation:
    both operands are coerced to Gn and the general op is run (decision 3).
    """
    ap = lines.append
    rd = result_mv.to_blade_dict()
    out_exprs = [sympy.sympify(rd.get(b, 0)) for b in blades]
    replacements, reduced = sympy.cse(out_exprs)
    ap(f"    def {method}(self, rhs) -> typing.Self:")
    emit_docstring(lines, method)
    ap(f"        if not isinstance(rhs, {name}):")
    ap("            left = Gn.from_blade_dict(self.to_blade_dict())")
    ap("            right = Gn.from_blade_dict(rhs.to_blade_dict())")
    ap(f"            return typing.cast(typing.Self, {cross})")
    for tmp, expr in replacements:
        ap(f"        {render(tmp)} = {render(expr)}")
    ap(f"        result = {name}(")
    for field, expr in zip(fields, reduced):
        lines.extend(format_assignment(field, expr, "            ", render))
    ap("        )")
    ap("        return typing.cast(typing.Self, result)")
    ap("")


def emit_structural(lines, name, blades, fields, n) -> None:
    """Emit the closed-form linear / grade / comparison methods.

    These replace the AbstractMultiVector versions that route through the
    to_blade_dict / from_blade_dict interchange.
    """
    ap = lines.append
    by_grade = {g: [field_name(b) for b in blades if len(b) == g] for g in range(n + 1)}
    coerce = [
        "            left = Gn.from_blade_dict(self.to_blade_dict())",
        "            right = Gn.from_blade_dict(rhs.to_blade_dict())",
    ]

    ap("    def __add__(self, rhs) -> typing.Self:")
    ap(f"        if not isinstance(rhs, {name}):")
    lines.extend(coerce)
    ap("            return typing.cast(typing.Self, left + right)")
    emit_construct_return(lines, name, [(f, f"self.{f} + rhs.{f}") for f in fields])
    ap("")

    ap("    def __sub__(self, rhs) -> typing.Self:")
    ap(f"        if not isinstance(rhs, {name}):")
    lines.extend(coerce)
    ap("            return typing.cast(typing.Self, left - right)")
    emit_construct_return(lines, name, [(f, f"self.{f} - rhs.{f}") for f in fields])
    ap("")

    ap("    def __neg__(self) -> typing.Self:")
    emit_construct_return(
        lines, name, [(f, f"typing.cast(numbers.Real, -self.{f})") for f in fields]
    )
    ap("")

    ap("    def scalar_part(self) -> numbers.Real:")
    emit_docstring(lines, "scalar_part")
    ap("        return self.scalar")
    ap("")

    ap("    def grades(self) -> list[int]:")
    ap("        present: list[int] = []")
    for g in range(n + 1):
        cond = " or ".join(f"self.{f} != 0" for f in by_grade[g])
        ap(f"        if {cond}:")
        ap(f"            present.append({g})")
    ap("        return present")
    ap("")

    ap("    def r_vector_part(self, r: int) -> typing.Self:")
    emit_docstring(lines, "r_vector_part")
    ap("        match r:")
    for g in range(n + 1):
        ap(f"            case {g}:")
        emit_construct_return(
            lines,
            name,
            [(f, f"self.{f}") for f in by_grade[g]],
            indent="                ",
        )
    ap("            case _:")
    emit_construct_return(lines, name, [], indent="                ")
    ap("")

    ap("    def reverse(self) -> typing.Self:")
    emit_docstring(lines, "reverse")
    rev_pairs = []
    for b in blades:
        f = field_name(b)
        sign = (-1) ** ((len(b) * (len(b) - 1)) // 2)
        expr = f"self.{f}" if sign == 1 else f"typing.cast(numbers.Real, -self.{f})"
        rev_pairs.append((f, expr))
    emit_construct_return(lines, name, rev_pairs)
    ap("")

    ap("    def even_part(self) -> typing.Self:")
    emit_docstring(lines, "even_part")
    emit_construct_return(
        lines,
        name,
        [(field_name(b), f"self.{field_name(b)}") for b in blades if len(b) % 2 == 0],
    )
    ap("")

    ap("    def odd_part(self) -> typing.Self:")
    emit_docstring(lines, "odd_part")
    emit_construct_return(
        lines,
        name,
        [(field_name(b), f"self.{field_name(b)}") for b in blades if len(b) % 2 == 1],
    )
    ap("")

    ap("    def is_close(self, other) -> bool:")
    ap(f"        if not isinstance(other, {name}):")
    ap("            return super().is_close(other)")
    ap("        return bool(")
    for i, f in enumerate(fields):
        prefix = "" if i == 0 else "and "
        ap(
            f"            {prefix}np.isclose("
            f"float(self.{f}), float(other.{f}), rtol=1e-5, atol=1e-5)"
        )
    ap("        )")
    ap("")

    ap("    def __iter__(self):")
    for b in blades:
        f = field_name(b)
        ap(f"        if self.{f} != 0:")
        ap(f"            yield {name}({f}=self.{f})")
    ap("")


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
    bl = blades_for_dim(n)

    def by_grade(g: int) -> tuple:
        return tuple(b for b in bl if len(b) == g)

    specs = [TypeSpec(f"Vector{n}", by_grade(1), n, "graded")]
    if n >= 2:
        specs.append(TypeSpec(f"Bivector{n}", by_grade(2), n, "graded"))
    if n >= 3:
        specs.append(TypeSpec(f"Trivector{n}", by_grade(3), n, "graded"))
    if n >= 2:  # even subalgebra (Rotor); for n==1 the even part is just the scalar
        even = tuple(b for b in bl if len(b) % 2 == 0)
        specs.append(TypeSpec(f"Rotor{n}", even, n, "graded"))
    return specs


def full_spec(n: int, full_name: str) -> TypeSpec:
    return TypeSpec(full_name, tuple(blades_for_dim(n)), n, "full")


def registry_for_dim(n: int, full_name: str) -> list[TypeSpec]:
    """Scalar + graded types + the full G_n -- every type a result can resolve to."""
    return [SCALAR, *graded_specs(n), full_spec(n, full_name)]


def resolve(support, n: int, full_name: str) -> TypeSpec:
    """Smallest registered type covering ``support`` (the full G_n always does)."""
    want = set(support)
    candidates = [t for t in registry_for_dim(n, full_name) if want <= set(t.blades)]
    return min(
        candidates,
        key=lambda t: (len(t.blades), 0 if t.kind == "scalar" else 1, t.name),
    )


def _renamer(blades_self, blades_rhs):
    """A (render, ) pair mapping a_<field> -> self.<field>, b_<field> -> rhs.<field>."""
    rename = {}
    for b in blades_self:
        rename["a_" + field_name(b)] = "self." + field_name(b)
    for b in blades_rhs:
        rename["b_" + field_name(b)] = "rhs." + field_name(b)
    if not rename:
        return lambda expr: sympy.sstr(sympy.sympify(expr))
    token = re.compile(r"\b(" + "|".join(re.escape(k) for k in rename) + r")\b")

    def render(expr) -> str:
        return token.sub(lambda m: rename[m.group(1)], sympy.sstr(sympy.sympify(expr)))

    return render


def product_result(t1: TypeSpec, t2: TypeSpec, gn_op, n: int, full_name: str):
    """(result_spec, output exprs over result's blades, render) for t1 <op> t2."""
    a_syms = {b: sympy.Symbol("a_" + field_name(b)) for b in t1.blades}
    b_syms = {b: sympy.Symbol("b_" + field_name(b)) for b in t2.blades}
    result_mv = gn_op(Gn.from_blade_dict(a_syms), Gn.from_blade_dict(b_syms))
    rd = result_mv.to_blade_dict()
    support = [b for b in blades_for_dim(n) if sympy.sympify(rd.get(b, 0)) != 0]
    rspec = resolve(support, n, full_name)
    out_exprs = [sympy.sympify(rd.get(b, 0)) for b in rspec.blades]
    render = _renamer(t1.blades, t2.blades)
    return rspec, out_exprs, render


def unary_result(t1: TypeSpec, gn_fn, n: int, full_name: str):
    """(result_spec, output exprs, render) for a unary op (dual / grade projection)."""
    a_syms = {b: sympy.Symbol("a_" + field_name(b)) for b in t1.blades}
    result_mv = gn_fn(Gn.from_blade_dict(a_syms))
    rd = result_mv.to_blade_dict()
    support = [b for b in blades_for_dim(n) if sympy.sympify(rd.get(b, 0)) != 0]
    rspec = resolve(support, n, full_name)
    out_exprs = [sympy.sympify(rd.get(b, 0)) for b in rspec.blades]
    render = _renamer(t1.blades, ())
    return rspec, out_exprs, render


def _emit_unary_return(lines, indent, rspec, out_exprs, render) -> None:
    """Emit ``return cast(Self, ResultType(field=cast(Real, ±field), ...))``.

    Unary results (dual / grade projection) are always ``±field`` or ``0``, so
    each component is cast to ``numbers.Real`` (a bare ``-self.e_1`` is otherwise
    inferred as ``_RealLike``, not ``Real``).
    """
    ap = lines.append
    ap(f"{indent}return typing.cast(")
    ap(f"{indent}    typing.Self,")
    ap(f"{indent}    {rspec.name}(")
    for field, expr in zip([field_name(b) for b in rspec.blades], out_exprs):
        e = sympy.sympify(expr)
        rendered = render(e)
        # a bare field (``self.e_1``) is already Real -- casting it is redundant;
        # constants and negations (``-self.e_1`` -> _RealLike) do need the cast.
        if e.is_Symbol:
            value = rendered
        else:
            value = f"typing.cast(numbers.Real, {rendered})"
        ap(f"{indent}        {field}={value},")
    ap(f"{indent}    ),")
    ap(f"{indent})")


def generate_class(n: int, name: str) -> str:
    blades = blades_for_dim(n)
    fields = [field_name(b) for b in blades]

    # symbolic operands for self/rhs; rendered straight back to attribute access
    # (``a_e_1`` -> ``self.e_1``, ``b_e_12`` -> ``rhs.e_12``) so the generated
    # product has no pointless alias locals.
    a_syms = {b: sympy.Symbol("a_" + field_name(b)) for b in blades}
    b_syms = {b: sympy.Symbol("b_" + field_name(b)) for b in blades}

    rename = {}
    for b in blades:
        rename["a_" + field_name(b)] = "self." + field_name(b)
        rename["b_" + field_name(b)] = "rhs." + field_name(b)
    token = re.compile(r"\b(" + "|".join(re.escape(k) for k in rename) + r")\b")

    def render(expr) -> str:
        return token.sub(lambda m: rename[m.group(1)], sympy.sstr(expr))

    a_mv = Gn.from_blade_dict(a_syms)
    b_mv = Gn.from_blade_dict(b_syms)

    lines: list[str] = []
    ap = lines.append

    ap("@dataclasses.dataclass(eq=False, slots=True)")
    ap(f"class {name}(AbstractMultiVector):")
    ap(f'    """{docstring_for(n)}"""')
    ap("")
    ap(f"    DIMENSION: typing.ClassVar[int] = {n}")
    ap("")
    for b in blades:
        ap(f"    {field_name(b)}: numbers.Real = typing.cast(numbers.Real, 0)")
    ap("")

    # from_blade_dict
    ap("    @classmethod")
    ap("    def from_blade_dict(cls, blade_coef) -> typing.Self:")
    ap("        d = dict(blade_coef)")
    ap("        return cls(")
    for b in blades:
        ap(
            f"            {field_name(b)}=typing.cast("
            f"numbers.Real, d.get({blade_literal(b)}, 0)),"
        )
    ap("        )")
    ap("")

    # to_blade_dict
    ap("    def to_blade_dict(self) -> BladeCoef:")
    ap("        return {")
    ap("            blade: coef")
    ap("            for blade, coef in (")
    for b in blades:
        ap(f"                ({blade_literal(b)}, self.{field_name(b)}),")
    ap("            )")
    ap("            if coef != 0")
    ap("        }")
    ap("")

    # __eq__ (simplify lazily, here -- works against any representation)
    ap("    def __eq__(self, other) -> bool:")
    ap("        if not isinstance(other, AbstractMultiVector):")
    ap("            return NotImplemented")
    ap("        left = self.to_blade_dict()")
    ap("        right = other.to_blade_dict()")
    ap("        return all(")
    ap("            sympy.simplify(")
    ap(
        "                sympy.sympify(left.get(blade, 0))"
        " - sympy.sympify(right.get(blade, 0))"
    )
    ap("            )")
    ap("            == 0")
    ap("            for blade in (set(left.keys()) | set(right.keys()))")
    ap("        )")
    ap("")

    # closed-form bilinear products, each derived from the Gn reference op
    emit_bilinear(
        lines,
        name,
        "_geometric_product",
        "left * right",
        a_mv * b_mv,
        blades,
        fields,
        render,
    )
    emit_bilinear(
        lines,
        name,
        "inner_product",
        "left.inner_product(right)",
        a_mv.inner_product(b_mv),
        blades,
        fields,
        render,
    )
    emit_bilinear(
        lines,
        name,
        "outer_product",
        "left.outer_product(right)",
        a_mv.outer_product(b_mv),
        blades,
        fields,
        render,
    )

    # closed-form linear / grade / comparison methods (no interchange round-trip)
    emit_structural(lines, name, blades, fields, n)

    # dimension-fixed convenience overrides: n defaults to this algebra's
    # DIMENSION, but an explicit n is still accepted for compatibility.
    ap("    def dual(self, n: int | None = None) -> typing.Self:")
    emit_docstring(lines, "dual")
    ap("        return super().dual(self.DIMENSION if n is None else n)")
    ap("")
    ap("    @classmethod")
    ap("    def unit_pseudoscalar(cls, n: int | None = None) -> typing.Self:")
    emit_docstring(lines, "unit_pseudoscalar")
    ap("        return super().unit_pseudoscalar(cls.DIMENSION if n is None else n)")
    ap("")
    ap("    @classmethod")
    ap("    def unit_pseudoscalar_squared(cls, n: int | None = None) -> typing.Self:")
    ap("        return super().unit_pseudoscalar_squared(")
    ap("            cls.DIMENSION if n is None else n")
    ap("        )")
    ap("")
    ap("    @classmethod")
    ap("    def bases(cls, n: int | None = None) -> Generator[typing.Self]:")
    ap("        return super().bases(cls.DIMENSION if n is None else n)")
    ap("")
    ap("    @classmethod")
    ap("    def symbolic_multivector(")
    ap('        cls, n: int | None = None, prefix: str = "a"')
    ap("    ) -> typing.Self:")
    ap("        return super().symbolic_multivector(")
    ap("            cls.DIMENSION if n is None else n, prefix")
    ap("        )")

    return "\n".join(lines)


def _emit_eq(ap) -> None:
    """The simplify-aware, cross-representation __eq__ (shared by every type)."""
    ap("    def __eq__(self, other) -> bool:")
    ap("        if not isinstance(other, AbstractMultiVector):")
    ap("            return NotImplemented")
    ap("        left = self.to_blade_dict()")
    ap("        right = other.to_blade_dict()")
    ap("        return all(")
    ap("            sympy.simplify(")
    ap(
        "                sympy.sympify(left.get(blade, 0))"
        " - sympy.sympify(right.get(blade, 0))"
    )
    ap("            )")
    ap("            == 0")
    ap("            for blade in (set(left.keys()) | set(right.keys()))")
    ap("        )")
    ap("")


def _emit_scaled(ap, name, fields, scalar_expr, indent="        ") -> None:
    """Emit ``return cast(Self, Name(field=cast(Real, <field>*scalar), ...))``."""
    ap(f"{indent}return typing.cast(")
    ap(f"{indent}    typing.Self,")
    ap(f"{indent}    {name}(")
    for f in fields:
        ap(f"{indent}        {f}=typing.cast(numbers.Real, {scalar_expr(f)}),")
    ap(f"{indent}    ),")
    ap(f"{indent})")


def _emit_result_block(lines, indent, rspec, out_exprs, render) -> None:
    """Emit ``return cast(Self, ResultType(field=expr, ...))`` (cse-factored)."""
    ap = lines.append
    replacements, reduced = sympy.cse(out_exprs)
    for tmp, expr in replacements:
        ap(f"{indent}{render(tmp)} = {render(expr)}")
    ap(f"{indent}return typing.cast(")
    ap(f"{indent}    typing.Self,")
    ap(f"{indent}    {rspec.name}(")
    for field, expr in zip([field_name(b) for b in rspec.blades], reduced):
        e = sympy.sympify(expr)
        # a bare ``-self.x`` reads as _RealLike to the type checker, so cast it;
        # bare/positive symbols and arithmetic sums are already Real.
        if e.is_Mul and (-e).is_Symbol:
            ap(f"{indent}        {field}=typing.cast(numbers.Real, {render(e)}),")
        else:
            lines.extend(format_assignment(field, expr, indent + "        ", render))
    ap(f"{indent}    ),")
    ap(f"{indent})")


def _emit_dispatch(
    lines, t1, method, gn_op, n, full_name, fallback_op, number_case=False
) -> None:
    """Emit a method that matches on the rhs type (the grade product/sum table).

    Return type per branch comes from ``resolve`` (the tightest covering type);
    ``number_case`` prepends a scalar-literal branch (used by + / -, which unlike
    * have no separate scalar wrapper)."""
    ap = lines.append
    ap(f"    def {method}(self, rhs) -> typing.Self:")
    ap("        match rhs:")
    if number_case:
        ap("            case int() | float() | sympy.Expr():")
        ap(f"                return self.{method}(")
        ap("                    Scalar(scalar=typing.cast(numbers.Real, rhs))")
        ap("                )")
    for t2 in [SCALAR, *graded_specs(n)]:
        rspec, out_exprs, render = product_result(t1, t2, gn_op, n, full_name)
        ap(f"            case {t2.name}():")
        _emit_result_block(lines, "                ", rspec, out_exprs, render)
    ap("            case _:")
    ap(f"                left = _coerce(self, {full_name})")
    ap(f"                right = _coerce(rhs, {full_name})")
    ap(f"                return typing.cast(typing.Self, {fallback_op})")
    ap("")


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


def generate_graded_type(spec: TypeSpec, n: int, full_name: str) -> str:
    blades = list(spec.blades)
    fields = [field_name(b) for b in blades]
    has_scalar = () in blades
    lines: list[str] = []
    ap = lines.append

    ap("@dataclasses.dataclass(eq=False)")
    ap(f"class {spec.name}(AbstractMultiVector):")
    ap(f'    """{graded_docstring(spec)}"""')
    ap("")
    ap(f"    DIMENSION: typing.ClassVar[int] = {n}")
    ap("")
    for f in fields:
        ap(f"    {f}: numbers.Real = typing.cast(numbers.Real, 0)")
    ap("")

    # from_blade_dict / to_blade_dict (only this type's blades)
    ap("    @classmethod")
    ap("    def from_blade_dict(cls, blade_coef) -> typing.Self:")
    ap("        d = dict(blade_coef)")
    ap("        return cls(")
    for b in blades:
        ap(
            f"            {field_name(b)}=typing.cast("
            f"numbers.Real, d.get({blade_literal(b)}, 0)),"
        )
    ap("        )")
    ap("")
    ap("    def to_blade_dict(self) -> BladeCoef:")
    ap("        return {")
    ap("            blade: coef")
    ap("            for blade, coef in (")
    for b in blades:
        ap(f"                ({blade_literal(b)}, self.{field_name(b)}),")
    ap("            )")
    ap("            if coef != 0")
    ap("        }")
    ap("")

    _emit_eq(ap)

    # scalar-aware __mul__ / __rmul__ (the ABC versions would drop the scalar
    # for a type with no scalar field, so they are overridden here)
    ap("    def __mul__(self, rhs) -> typing.Self:")
    ap("        if isinstance(rhs, (int, float, sympy.Expr)):")
    _emit_scaled(ap, spec.name, fields, lambda f: f"self.{f} * rhs", "            ")
    ap("        return self._geometric_product(rhs)")
    ap("")
    ap("    def __rmul__(self, lhs) -> typing.Self:")
    ap("        if isinstance(lhs, (int, float, sympy.Expr)):")
    _emit_scaled(ap, spec.name, fields, lambda f: f"lhs * self.{f}", "            ")
    ap("        return self._geometric_product(lhs)")
    ap("")

    # the three bilinear products, each a match on the rhs type
    _emit_dispatch(
        lines,
        spec,
        "_geometric_product",
        lambda a, b: a * b,
        n,
        full_name,
        "left * right",
    )
    _emit_dispatch(
        lines,
        spec,
        "outer_product",
        lambda a, b: a.outer_product(b),
        n,
        full_name,
        "left.outer_product(right)",
    )
    _emit_dispatch(
        lines,
        spec,
        "inner_product",
        lambda a, b: a.inner_product(b),
        n,
        full_name,
        "left.inner_product(right)",
    )

    # linear ops also narrow to the tightest covering type (so e.g.
    # Scalar + Bivector2 -> Rotor2, and values build by linear combination)
    _emit_dispatch(
        lines,
        spec,
        "__add__",
        lambda a, b: a + b,
        n,
        full_name,
        "left + right",
        number_case=True,
    )
    _emit_dispatch(
        lines,
        spec,
        "__sub__",
        lambda a, b: a - b,
        n,
        full_name,
        "left - right",
        number_case=True,
    )
    ap("    def __radd__(self, lhs) -> typing.Self:")
    ap("        return self.__add__(lhs)")
    ap("")
    ap("    def __rsub__(self, lhs) -> typing.Self:")
    ap("        return typing.cast(typing.Self, (-self).__add__(lhs))")
    ap("")

    ap("    def __neg__(self) -> typing.Self:")
    _emit_scaled(ap, spec.name, fields, lambda f: f"-self.{f}")
    ap("")

    # reverse: sign (-1)**(k(k-1)/2) per blade; stays in this type
    ap("    def reverse(self) -> typing.Self:")
    ap("        return typing.cast(")
    ap("            typing.Self,")
    ap(f"            {spec.name}(")
    for b in blades:
        f = field_name(b)
        sign = (-1) ** ((len(b) * (len(b) - 1)) // 2)
        rhs_e = f"self.{f}" if sign == 1 else f"typing.cast(numbers.Real, -self.{f})"
        ap(f"                {f}={rhs_e},")
    ap("            ),")
    ap("        )")
    ap("")

    ap("    def scalar_part(self) -> numbers.Real:")
    if has_scalar:
        ap("        return self.scalar")
    else:
        ap("        return typing.cast(numbers.Real, 0)")
    ap("")

    ap("    def grades(self) -> list[int]:")
    ap("        present: list[int] = []")
    for g in sorted({len(b) for b in blades}):
        cond = " or ".join(f"self.{field_name(b)} != 0" for b in blades if len(b) == g)
        ap(f"        if {cond}:")
        ap(f"            present.append({g})")
    ap("        return present")
    ap("")

    ap("    def is_close(self, other) -> bool:")
    ap(f"        if not isinstance(other, {spec.name}):")
    ap("            return super().is_close(other)")
    ap("        return bool(")
    for i, f in enumerate(fields):
        prefix = "" if i == 0 else "and "
        ap(
            f"            {prefix}np.isclose("
            f"float(self.{f}), float(other.{f}), rtol=1e-5, atol=1e-5)"
        )
    ap("        )")
    ap("")

    ap("    def __iter__(self):")
    for b in blades:
        f = field_name(b)
        ap(f"        if self.{f} != 0:")
        ap(f"            yield {spec.name}({f}=self.{f})")
    ap("")

    # grade-changing / projection ops: narrow to the tightest covering type via
    # resolve(), the same way the products do (e.g. dual(Bivector3) -> Vector3)
    ap("    def even_part(self) -> typing.Self:")
    _emit_unary_return(
        lines, "        ", *unary_result(spec, lambda a: a.even_part(), n, full_name)
    )
    ap("")
    ap("    def odd_part(self) -> typing.Self:")
    _emit_unary_return(
        lines, "        ", *unary_result(spec, lambda a: a.odd_part(), n, full_name)
    )
    ap("")
    ap("    def r_vector_part(self, r: int) -> typing.Self:")
    for r in range(n + 1):
        ap(f"        if r == {r}:")
        _emit_unary_return(
            lines,
            "            ",
            *unary_result(spec, lambda a, r=r: a.r_vector_part(r), n, full_name),
        )
    ap(
        "        return typing.cast(typing.Self, "
        "Scalar(scalar=typing.cast(numbers.Real, 0)))"
    )
    ap("")
    # dual is a fixed product with the pseudoscalar; closed-form for this type's
    # own dimension, defer to the full type for an explicit foreign n
    ap("    def dual(self, n: int | None = None) -> typing.Self:")
    ap(f"        if n is None or n == {n}:")
    _emit_unary_return(
        lines, "            ", *unary_result(spec, lambda a: a.dual(n), n, full_name)
    )
    ap(f"        return typing.cast(typing.Self, _coerce(self, {full_name}).dual(n))")

    if spec.name.startswith("Rotor"):
        ap("")
        ap("    def plane_of_rotation(self) -> AbstractMultiVector:")
        ap('        """The unit bivector (2-blade) this rotor rotates in.')
        ap("")
        ap("        A rotor is ``cos(t/2) - sin(t/2) * B`` for a unit bivector B --")
        ap("        the oriented plane of rotation.  This returns B, the normalized")
        ap("        bivector part.  In 2D that 2-blade is also the pseudoscalar; in 3D")
        ap("        it is a bivector plane, not the trivector.  Undefined for the")
        ap('        identity rotor (no rotation)."""')
        ap("        return self.r_vector_part(2).normalize()")

    return "\n".join(lines)


def generate_scalar() -> str:
    """The shared grade-0 ``Scalar`` type (dimension-agnostic)."""
    lines: list[str] = []
    ap = lines.append
    ap("@dataclasses.dataclass(eq=False)")
    ap("class Scalar(AbstractMultiVector):")
    ap(
        '    """The grade-0 type -- a scalar, shared across every 𝒢ₙ.\n\n'
        "    ``Scalar * x`` scales ``x`` and returns x's type; pure-scalar product\n"
        "    results (e.g. Bivector2 * Bivector2) land here.  AUTO-GENERATED by\n"
        '    tools/gen_specialized.py."""'
    )
    ap("")
    ap("    scalar: numbers.Real = typing.cast(numbers.Real, 0)")
    ap("")
    ap("    @classmethod")
    ap("    def from_blade_dict(cls, blade_coef) -> typing.Self:")
    ap("        d = dict(blade_coef)")
    ap("        return cls(scalar=typing.cast(numbers.Real, d.get((), 0)))")
    ap("")
    ap("    def to_blade_dict(self) -> BladeCoef:")
    ap("        return {(): self.scalar} if self.scalar != 0 else {}")
    ap("")
    _emit_eq(ap)
    ap("    def __mul__(self, rhs) -> typing.Self:")
    ap("        if isinstance(rhs, (int, float, sympy.Expr)):")
    ap(
        "            return typing.cast(typing.Self, "
        "Scalar(scalar=typing.cast(numbers.Real, self.scalar * rhs)))"
    )
    ap("        return self._geometric_product(rhs)")
    ap("")
    ap("    def __rmul__(self, lhs) -> typing.Self:")
    ap("        if isinstance(lhs, (int, float, sympy.Expr)):")
    ap(
        "            return typing.cast(typing.Self, "
        "Scalar(scalar=typing.cast(numbers.Real, lhs * self.scalar)))"
    )
    ap("        return self._geometric_product(lhs)")
    ap("")
    ap("    def _geometric_product(self, rhs) -> typing.Self:")
    ap("        if isinstance(rhs, Scalar):")
    ap(
        "            return typing.cast(typing.Self, "
        "Scalar(scalar=typing.cast(numbers.Real, self.scalar * rhs.scalar)))"
    )
    ap("        if isinstance(rhs, AbstractMultiVector):")
    ap("            return typing.cast(typing.Self, self.scalar * rhs)")
    ap(
        "        return typing.cast(typing.Self, "
        "Scalar(scalar=typing.cast(numbers.Real, self.scalar * rhs)))"
    )
    ap("")
    ap("    def outer_product(self, rhs) -> typing.Self:")
    ap("        return self._geometric_product(rhs)")
    ap("")
    ap("    def inner_product(self, rhs) -> typing.Self:")
    ap("        left = Gn.from_blade_dict(self.to_blade_dict())")
    ap("        right = Gn.from_blade_dict(rhs.to_blade_dict())")
    ap("        return typing.cast(typing.Self, left.inner_product(right))")
    ap("")
    ap("    def __add__(self, rhs) -> typing.Self:")
    ap("        if isinstance(rhs, (int, float, sympy.Expr)):")
    ap(
        "            return typing.cast(typing.Self, "
        "Scalar(scalar=typing.cast(numbers.Real, self.scalar + rhs)))"
    )
    ap("        if isinstance(rhs, Scalar):")
    ap(
        "            return typing.cast(typing.Self, "
        "Scalar(scalar=self.scalar + rhs.scalar))"
    )
    ap("        if isinstance(rhs, AbstractMultiVector):")
    ap("            return typing.cast(typing.Self, rhs + self)")
    ap("        return typing.cast(typing.Self, NotImplemented)")
    ap("")
    ap("    def __radd__(self, lhs) -> typing.Self:")
    ap("        return self.__add__(lhs)")
    ap("")
    ap("    def __sub__(self, rhs) -> typing.Self:")
    ap("        return self + (-1 * rhs)")
    ap("")
    ap("    def __rsub__(self, lhs) -> typing.Self:")
    ap("        return (-self) + lhs")
    ap("")
    ap("    def __neg__(self) -> typing.Self:")
    ap(
        "        return typing.cast(typing.Self, "
        "Scalar(scalar=typing.cast(numbers.Real, -self.scalar)))"
    )
    ap("")
    ap("    def reverse(self) -> typing.Self:")
    ap("        return typing.cast(typing.Self, Scalar(scalar=self.scalar))")
    ap("")
    ap("    def scalar_part(self) -> numbers.Real:")
    ap("        return self.scalar")
    ap("")
    ap("    def grades(self) -> list[int]:")
    ap("        return [0] if self.scalar != 0 else []")
    ap("")
    ap("    def is_close(self, other) -> bool:")
    ap("        if not isinstance(other, Scalar):")
    ap("            return super().is_close(other)")
    ap(
        "        return bool(np.isclose("
        "float(self.scalar), float(other.scalar), rtol=1e-5, atol=1e-5))"
    )
    ap("")
    ap("    def __iter__(self):")
    ap("        if self.scalar != 0:")
    ap("            yield Scalar(scalar=self.scalar)")
    ap("")
    ap("    def even_part(self) -> typing.Self:")
    ap("        return typing.cast(typing.Self, Scalar(scalar=self.scalar))")
    ap("")
    ap("    def odd_part(self) -> typing.Self:")
    ap(
        "        return typing.cast(typing.Self, "
        "Scalar(scalar=typing.cast(numbers.Real, 0)))"
    )
    ap("")
    ap("    def r_vector_part(self, r: int) -> typing.Self:")
    ap("        if r == 0:")
    ap("            return typing.cast(typing.Self, Scalar(scalar=self.scalar))")
    ap(
        "        return typing.cast(typing.Self, "
        "Scalar(scalar=typing.cast(numbers.Real, 0)))"
    )
    ap("")
    ap("    def dual(self, n: int | None = None) -> typing.Self:")
    ap("        if n is None:")
    ap('            raise ValueError("Scalar.dual needs an explicit dimension n")')
    ap(
        "        return typing.cast(typing.Self, "
        "Gn.from_blade_dict(self.to_blade_dict()).dual(n))"
    )
    return "\n".join(lines)


def generate_constants(n: int, name: str) -> str:
    """Module-level basis constants for one algebra, each of that algebra's type."""
    nonempty = [b for b in blades_for_dim(n) if b != ()]
    lines: list[str] = []
    ap = lines.append
    ap(f"zero: {name} = {name}.from_scalar(0)")
    ap(f"one: {name} = {name}.from_scalar(1)")
    for b in nonempty:
        ap(
            f"{field_name(b)}: {name} = "
            f"{name}.from_blade_dict({{{blade_literal(b)}: 1}})"
        )
    ap("")
    exported = [repr(name), repr("Scalar")]
    exported += [repr(s.name) for s in graded_specs(n)]
    exported += [repr("zero"), repr("one")]
    exported += [repr(field_name(b)) for b in nonempty]
    ap(f"__all__ = [{', '.join(exported)}]")
    return "\n".join(lines)


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
        subprocess.run(["ruff", "check", "--fix", "--quiet", *paths], check=False)
        subprocess.run(
            ["ruff", "format", "--quiet", "--line-length=88", *paths], check=True
        )
    except FileNotFoundError:
        sys.stdout.write("warning: ruff not found; generated files left unformatted\n")
        return
    sys.stdout.write("formatted with ruff\n")


def main() -> None:
    written: list[str] = []
    # the shared Scalar module first (the graded types import it)
    scalar_source = "\n".join(
        [SCALAR_HEADER, "", generate_scalar(), "", "", '__all__ = ["Scalar"]', ""]
    )
    with open(out_path("scalar.py"), "w") as f:
        f.write(scalar_source)
    written.append(out_path("scalar.py"))
    sys.stdout.write(f"wrote {os.path.normpath(out_path('scalar.py'))}\n")

    for n, name, filename in ALGEBRAS:
        parts = [header(name, n), "", generate_class(n, name), ""]
        for spec in graded_specs(n):
            parts += ["", generate_graded_type(spec, n, name), ""]
        parts += ["", generate_constants(n, name), ""]
        source = "\n".join(parts)
        with open(out_path(filename), "w") as f:
            f.write(source)
        written.append(out_path(filename))
        sys.stdout.write(f"wrote {os.path.normpath(out_path(filename))}\n")
    ruff_format(written)


if __name__ == "__main__":
    main()
