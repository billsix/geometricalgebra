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

"""Notebook helpers for the book: show a product term by term, and plot symbolic values.

``show_mult(a, b)`` shows the distribution of ``a * b`` the way a student
multiplies ``(x + 2) * (x + 3)`` by hand: every term of ``a`` times every term of
``b``, one table row per pair, then the sum. It needs only sympy and IPython, so
the book's notebooks (which draw with ePiX, not matplotlib) can use it without
importing the plotting helpers in ``gacalc.nbplotutils``, which re-exports it.

``show_cancellation(left, right, left_name, right_name)`` shows both sides of an
identity, then their difference blade by blade, with each pair of cancelling terms
marked by the same number, so a reader watches the terms disappear.

``at_values(value, values)`` substitutes numbers for the symbols in a symbolic
result. The book's notebooks compute every step with symbolic coordinates and use
numbers only to draw the figures, and to show a drawn step at those numbers.
"""

import typing
from collections.abc import Mapping, Sequence

import sympy
from IPython.display import Markdown, Math, display

from gacalc.base import Blade, MultiVectorBase, Real, blade_dict_latex, blade_latex

V = typing.TypeVar("V", bound=MultiVectorBase)


@typing.overload
def at_values(value: V, values: Sequence[tuple[sympy.Symbol, Real]]) -> V: ...
@typing.overload
def at_values(value: Real, values: Sequence[tuple[sympy.Symbol, Real]]) -> Real: ...
def at_values(
    value: MultiVectorBase | Real, values: Sequence[tuple[sympy.Symbol, Real]]
) -> MultiVectorBase | Real:
    """``value`` with each ``(symbol, number)`` pair of ``values`` substituted.

    A multivector keeps its type, with every coefficient substituted and
    simplified; a number is substituted and simplified.

    Args:
        value: a symbolic number or multivector.
        values: the ``(symbol, number)`` pairs, e.g. ``[(a_1, 1), (a_2, 4)]``.

    Returns:
        MultiVectorBase | Real: ``value`` at those numbers.

    >>> import sympy
    >>> from gacalc.g2 import Scalar, e_1, e_2
    >>> a_1, a_2 = sympy.symbols("a_1 a_2", real=True)
    >>> a = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
    >>> at_values(a, [(a_1, 1), (a_2, 4)]) == 1 * e_1 + 4 * e_2
    True
    >>> at_values(a.magnitude(), [(a_1, 3), (a_2, 4)])
    5
    """

    def number_at(r: Real) -> Real:
        return sympy.simplify(sympy.sympify(r).subs(values))

    match value:
        case MultiVectorBase():
            return type(value).from_blade_dict(
                {blade: number_at(c) for blade, c in value.to_blade_dict().items()}
            )
        case _:
            return number_at(value)


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
    | $1\\vec{\\mathbf{e}}_{1}$ | * | $3\\vec{\\mathbf{e}}_{1}$ | = | $3$ |
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


def _signed_terms(coefficient: Real) -> list[sympy.Expr]:
    """The monomials of ``coefficient`` once expanded, in sympy's order (no zeros).

    >>> a, b = sympy.symbols("a b")
    >>> _signed_terms(a * (b - 2))
    [-2*a, a*b]
    >>> _signed_terms(0)
    []
    """
    return [
        term for term in sympy.Add.make_args(sympy.expand(coefficient)) if term != 0
    ]


def _join_terms(parts: Sequence[tuple[bool, str]]) -> str:
    """Join ``(negative, latex)`` terms into one signed sum (``0`` when empty)."""
    if not parts:
        return "0"
    pieces: list[str] = [
        ("- " if negative else "+ ") + latex for negative, latex in parts
    ]
    first: str = pieces[0]
    return " ".join([first[2:] if first.startswith("+ ") else first, *pieces[1:]])


def cancellation_latex(left: MultiVectorBase, right: MultiVectorBase) -> list[str]:
    """One LaTeX line per blade showing ``left − right`` cancel term by term.

    Each coefficient is expanded into monomials. A monomial of ``left`` that also
    appears in ``right`` is a cancelling pair: both copies are marked
    ``\\underbrace{…}_{k}`` with the same number ``k``, so a reader can match them.
    Whatever does not cancel is left unmarked, and the line ends with the residual,
    ``0`` for an identity.

    Args:
        left: the left side of the claimed identity.
        right: the right side.

    Returns:
        list[str]: one line per blade present on either side, grade then blade
        order: ``<blade>: (left terms) - (right terms) = residual``.

    Example:
        ``a * b + a * c`` against ``a * c + a * b``: the terms pair up across the
        sides, and the difference is zero.

        >>> from gacalc.g2 import Scalar, e_1
        >>> a, b, c = sympy.symbols("a b c")
        >>> [line] = cancellation_latex(
        ...     Scalar(a * b + a * c) * e_1, Scalar(a * c + a * b) * e_1
        ... )
        >>> line.count("underbrace"), line.endswith("= 0")
        (4, True)
    """
    left_coefficients: Mapping[Blade, Real] = left.to_blade_dict()
    right_coefficients: Mapping[Blade, Real] = right.to_blade_dict()

    def line(blade: Blade) -> str:
        left_terms: list[sympy.Expr] = _signed_terms(left_coefficients.get(blade, 0))
        right_terms: list[sympy.Expr] = _signed_terms(right_coefficients.get(blade, 0))
        # pair each left term with the first equal, still-unpaired right term
        right_labels: dict[int, int] = {}
        left_labels: list[int | None] = []
        term: sympy.Expr
        for term in left_terms:
            match_index: int | None = next(
                (
                    j
                    for j, other in enumerate(right_terms)
                    if j not in right_labels and other == term
                ),
                None,
            )
            if match_index is None:
                left_labels.append(None)
            else:
                right_labels[match_index] = len(right_labels) + 1
                left_labels.append(right_labels[match_index])

        def part(term: sympy.Expr, label: int | None) -> tuple[bool, str]:
            negative: bool = term.could_extract_minus_sign()
            body: str = sympy.latex(-term if negative else term)
            return negative, (
                body if label is None else f"\\underbrace{{{body}}}_{{{label}}}"
            )

        residual: Real = sympy.expand(
            left_coefficients.get(blade, 0) - right_coefficients.get(blade, 0)
        )
        name: str = "\\text{scalar}" if blade == () else blade_latex(blade)
        left_sum: str = _join_terms(
            [part(t, k) for t, k in zip(left_terms, left_labels, strict=True)]
        )
        right_sum: str = _join_terms(
            [part(t, right_labels.get(j)) for j, t in enumerate(right_terms)]
        )
        return f"{name}:\\quad ({left_sum}) - ({right_sum}) = {sympy.latex(residual)}"

    return [
        line(blade)
        for blade in sorted(
            set(left_coefficients) | set(right_coefficients),
            key=lambda blade: (len(blade), blade),
        )
    ]


def show_cancellation(
    left: MultiVectorBase,
    right: MultiVectorBase,
    left_name: str,
    right_name: str,
) -> None:
    """Display (in a notebook) both sides of an identity, then their difference
    cancelling term by term.

    Shows ``left`` and ``right`` expanded, then one line per blade from
    ``cancellation_latex``, where matching terms carry the same number under an
    ``\\underbrace``, so the reader watches the terms disappear instead of being
    handed a bare ``0``.

    Args:
        left: the left side, already computed.
        right: the right side, already computed.
        left_name: LaTeX for how the left side was built, e.g. ``a * (b + c)``.
        right_name: LaTeX for the right side.
    """
    display(Markdown("**The left side**"))
    display(Math(f"{left_name} = " + _math_body(_latex(left))))
    display(Markdown("**The right side**"))
    display(Math(f"{right_name} = " + _math_body(_latex(right))))
    display(
        Markdown(
            "**Their difference, blade by blade.** Terms with the same number cancel:"
        )
    )
    text: str
    for text in cancellation_latex(left, right):
        display(Math(text))
