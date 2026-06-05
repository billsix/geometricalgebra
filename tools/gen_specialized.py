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
import sys
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


def format_assignment(lhs: str, expr, indent: str, render) -> list[str]:
    """Render ``<lhs>=<expr>,`` for a constructor kwarg, wrapping long sums.

    Short expressions stay on one line; long ones are split across lines one
    additive term at a time so no line exceeds the formatter's limit.  ``render``
    turns a sympy expression into source text (e.g. ``self.e_1 * rhs.e_2``).
    """
    expr = sympy.sympify(expr)
    rendered = render(expr)
    if not expr.free_symbols:
        # a constant component (e.g. an identically-zero blade) -- cast to the
        # field type so the checker doesn't see a bare Literal.
        rendered = f"typing.cast(numbers.Real, {rendered})"
    inline = f"{indent}{lhs}={rendered},"
    if len(inline) <= 88:
        return [inline]

    terms = expr.as_ordered_terms() if expr.is_Add else [expr]
    cont = indent + "    "
    lines = [f"{indent}{lhs}=("]
    for i, term in enumerate(terms):
        s = render(term)
        if i == 0:
            lines.append(f"{cont}{s}")
        elif s.startswith("-"):
            lines.append(f"{cont}- {s[1:].lstrip()}")
        else:
            lines.append(f"{cont}+ {s}")
    lines.append(f"{indent}),")
    return lines


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
    for g in range(n + 1):
        ap(f"        if r == {g}:")
        emit_construct_return(
            lines, name, [(f, f"self.{f}") for f in by_grade[g]], indent="            "
        )
    emit_construct_return(lines, name, [])
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

    ap("@dataclasses.dataclass(eq=False)")
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
    exported = [repr(name), repr("zero"), repr("one")]
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
"""


ALGEBRAS = [(1, "G1", "g1.py"), (2, "G2", "g2.py"), (3, "G3", "g3.py")]


def main() -> None:
    for n, name, filename in ALGEBRAS:
        source = "\n".join(
            [
                header(name, n),
                "",
                generate_class(n, name),
                "",
                "",
                generate_constants(n, name),
                "",
            ]
        )
        with open(out_path(filename), "w") as f:
            f.write(source)
        sys.stdout.write(f"wrote {os.path.normpath(out_path(filename))}\n")


if __name__ == "__main__":
    main()
