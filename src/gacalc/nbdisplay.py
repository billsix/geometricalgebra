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

"""Display-only notebook helpers: show a geometric product as math, term by term.

``show_mult(a, b)`` shows the distribution of ``a * b`` the way a student
multiplies ``(x + 2) * (x + 3)`` by hand: every term of ``a`` times every term of
``b``, one table row per pair, then the sum. It needs only sympy and IPython, so
the book's notebooks (which draw with ePiX, not matplotlib) can use it without
importing the plotting helpers in ``gacalc.nbplotutils``, which re-exports it.
"""

from collections.abc import Mapping

import sympy
from IPython.display import Markdown, Math, display

from gacalc.base import Blade, MultiVectorBase, Real, blade_dict_latex


def _blade_terms(mv: MultiVectorBase) -> list[MultiVectorBase]:
    """The single-blade multivectors that sum to ``mv`` (its product-table terms),
    ordered by grade, then by blade.

    Iteration yields coefficient values, so the decomposition goes through
    ``to_blade_dict``.

    >>> from gacalc.g2 import e_1, e_2
    >>> [term.to_blade_dict() for term in _blade_terms(2 * e_1 + 3 * e_2)]
    [{(1,): 2}, {(2,): 3}]
    """
    return [
        type(mv).from_blade_dict({blade: coef})
        for blade, coef in sorted(
            mv.to_blade_dict().items(), key=lambda item: (len(item[0]), item[0])
        )
    ]


def _expand_numerators_dict(mv: MultiVectorBase) -> Mapping[Blade, Real]:
    """``mv``'s blade dict with each coefficient's numerator expanded and its
    denominator left factored, for display.

    It expands the raw ``to_blade_dict()`` coefficients without rebuilding the
    multivector. The eager-simplifying ``Gn``'s ``from_blade_dict`` re-runs
    ``sympy.simplify``, which would re-factor the distributed numerator (back to
    ``a0*(b0*c0 + ...)``); expanding the dict keeps the distributed form on every
    representation.
    """
    out: dict[Blade, Real] = {}
    blade: Blade
    coef: Real
    for blade, coef in mv.to_blade_dict().items():
        numerator: sympy.Expr
        denominator: sympy.Expr
        numerator, denominator = sympy.fraction(sympy.together(coef))
        out[blade] = sympy.expand(numerator) / denominator
    return out


def _latex(mv: MultiVectorBase) -> str:
    """``mv`` as LaTeX with its math delimiters (from ``blade_dict_latex``), each
    numerator expanded (``_expand_numerators_dict``)."""
    return blade_dict_latex(_expand_numerators_dict(mv))


def _math_body(latex: str) -> str:
    """``latex`` without its surrounding ``$`` / ``$$`` delimiters.

    ``IPython.display.Math`` adds its own; a delimiter left inside breaks the
    equation environment the book's PDF build puts it in.

    >>> _math_body("$$3 e_{1}$$")
    '3 e_{1}'
    """
    return latex.strip().strip("$").strip()


def product_table_markdown(a: MultiVectorBase, b: MultiVectorBase) -> str:
    """A Markdown table of every term of ``a`` times every term of ``b``.

    One row per pair (left term, right term, their product), terms in grade-then-
    blade order. Summing the last column gives ``a * b``.

    >>> from gacalc.g2 import e_1, e_2
    >>> lines = product_table_markdown(1 * e_1 + 2 * e_2, 3 * e_1).splitlines()
    >>> print(lines[0])
    | Left Component | * | Right Component | = | Product |
    >>> len(lines)  # header, separator, then 2 * 1 = 2 term pairs
    4
    >>> print(lines[2])
    | $1\\mathbf{\\vec{e}}_{1}$ | * | $3\\mathbf{\\vec{e}}_{1}$ | = | $3$ |
    """
    header: str = "| Left Component | * | Right Component | = | Product |"
    separator: str = "|---|---|---|---|---|"
    rows: list[str] = [
        f"| {_latex(left)} | * | {_latex(right)} | = | {_latex(left * right)} |"
        for left in _blade_terms(a)
        for right in _blade_terms(b)
    ]
    return "\n".join([header, separator, *rows])


def show_mult(a: MultiVectorBase, b: MultiVectorBase) -> None:
    """Display (in a notebook) the full distributive expansion of ``a * b``.

    Shows the product to evaluate, the table of every term-by-term product
    (``product_table_markdown``), then the sum, all rendered as LaTeX.
    """
    display(Markdown("**We want to evaluate**"))
    left: str = _math_body(a._repr_latex_())
    right: str = _math_body(b._repr_latex_())
    display(Math(f"({left}) * ({right})"))
    display(Markdown("**Multivector Multiplication is distributive over addition**"))
    display(Markdown(product_table_markdown(a, b)))
    display(Markdown("**Summing all the products up, we get**"))
    display(Math(_math_body(_latex(a * b))))
