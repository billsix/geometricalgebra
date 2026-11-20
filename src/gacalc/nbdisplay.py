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

from gacalc.base import (
    LATEX_LINE_WIDTH,
    Blade,
    MultiVectorBase,
    Real,
    blade_dict_latex,
    blade_latex,
    latex_broken,
)

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


#: The visible characters a product-table cell holds before its math is broken.
TABLE_CELL_WIDTH: int = 24


def _latex(mv: MultiVectorBase, width: int = LATEX_LINE_WIDTH) -> str:
    """``mv`` as LaTeX with its math delimiters (from ``blade_dict_latex``), each
    numerator expanded (``_expand_numerators_dict``), broken into rows past
    ``width`` visible characters."""
    return blade_dict_latex(_expand_numerators_dict(mv), width=width)


def _math_body(latex: str) -> str:
    """``latex`` without its surrounding ``$`` / ``$$`` delimiters.

    ``IPython.display.Math`` adds its own; a delimiter left inside breaks the
    equation environment the book's PDF build puts it in.

    >>> _math_body("$$3 e_{1}$$")
    '3 e_{1}'
    """
    return latex.strip().strip("$").strip()


def _row_products(
    a: MultiVectorBase, b: MultiVectorBase
) -> list[tuple[MultiVectorBase, MultiVectorBase, dict[Blade, list[sympy.Expr]]]]:
    """Every (left term, right term, product) of ``a * b``, the product as its
    expanded monomials per blade."""
    rows: list[
        tuple[MultiVectorBase, MultiVectorBase, dict[Blade, list[sympy.Expr]]]
    ] = []
    left: MultiVectorBase
    right: MultiVectorBase
    for left in _blade_terms(a):
        for right in _blade_terms(b):
            rows.append(
                (
                    left,
                    right,
                    {
                        blade: _signed_terms(coefficient)
                        for blade, coefficient in sorted(
                            (left * right).to_blade_dict().items(),
                            key=lambda item: (len(item[0]), item[0]),
                        )
                    },
                )
            )
    return rows


def _cancelling_labels(
    products: Sequence[Mapping[Blade, Sequence[sympy.Expr]]],
) -> dict[tuple[int, Blade, int], int]:
    """Number the monomials of the table's products that cancel in the sum.

    A monomial cancels a monomial of the same blade, in another row or the same
    one, that is its negative. Each pair gets the next number, the same on both;
    the key is ``(row, blade, index of the monomial)``.

    >>> a, b = sympy.symbols("a b")
    >>> _cancelling_labels([{(1, 2): [a * b]}, {(1, 2): [-a * b]}, {(): [a]}])
    {(0, (1, 2), 0): 1, (1, (1, 2), 0): 1}
    """
    entries: list[tuple[tuple[int, Blade, int], sympy.Expr]] = [
        ((row, blade, index), term)
        for row, product in enumerate(products)
        for blade, terms in product.items()
        for index, term in enumerate(terms)
    ]
    labels: dict[tuple[int, Blade, int], int] = {}
    key: tuple[int, Blade, int]
    term: sympy.Expr
    for key, term in entries:
        if key in labels:
            continue
        partner: tuple[int, Blade, int] | None = next(
            (
                other_key
                for other_key, other in entries
                if other_key not in labels
                and other_key != key
                and other_key[1] == key[1]
                and other == -term
            ),
            None,
        )
        if partner is not None:
            label: int = len(labels) // 2 + 1
            labels[key] = label
            labels[partner] = label
    return labels


def _marked_product_latex(
    row: int,
    product: Mapping[Blade, Sequence[sympy.Expr]],
    labels: Mapping[tuple[int, Blade, int], int],
) -> str:
    """One table product as inline LaTeX, each cancelling monomial under its
    numbered ``\\underbrace``, broken into rows past ``TABLE_CELL_WIDTH``."""
    tokens: list[str] = []
    blade: Blade
    terms: Sequence[sympy.Expr]
    for blade, terms in product.items():
        coefficient: list[str] = _marked_tokens(
            terms, [labels.get((row, blade, index)) for index in range(len(terms))]
        )
        if blade != ():
            coefficient[0] = "(" + coefficient[0]
            coefficient[-1] = coefficient[-1] + ") " + blade_latex(blade)
        if tokens:
            coefficient[0] = "+ " + coefficient[0]
        tokens.extend(coefficient)
    return "$" + latex_broken(tokens, TABLE_CELL_WIDTH) + "$"


def _with_operator(operator: str, latex: str) -> str:
    """``latex`` (``$...$``) with ``operator`` in front, inside the same math.

    >>> _with_operator("*", "$3$")
    '$* \\\\; 3$'
    """
    return "$" + operator + " \\; " + _math_body(latex) + "$"


def product_table_markdown(a: MultiVectorBase, b: MultiVectorBase) -> str:
    """A Markdown table of every term of ``a`` times every term of ``b``.

    One row per pair: the left term, ``*`` and the right term, ``=`` and their
    product (three columns, so the PDF's table spends no column on an operator),
    terms in grade-then-blade order. Summing the last column gives ``a * b``.
    Terms of the products that cancel in that sum (a term and its negative, of the
    same blade) carry the same number under an ``\\underbrace``, so a reader sees
    which products drop out. A cell wider than ``TABLE_CELL_WIDTH`` breaks into
    rows.

    >>> from gacalc.g2 import e_1, e_2
    >>> lines = product_table_markdown(1 * e_1 + 2 * e_2, 3 * e_1).splitlines()
    >>> print(lines[0])
    | Left Component | * Right Component | = Product |
    >>> len(lines)  # header, separator, then 2 * 1 = 2 term pairs
    4
    >>> print(lines[2])
    | $1\\vec{\\mathbf{e}}_{1}$ | $* \\; 3\\vec{\\mathbf{e}}_{1}$ | $= \\; 3$ |

    The two cross terms of ``(e_1 + e_2) * (e_1 + e_2)`` cancel:

    >>> table = product_table_markdown(1 * e_1 + 1 * e_2, 1 * e_1 + 1 * e_2)
    >>> table.count("underbrace{1}_{1}")
    2
    """
    header: str = "| Left Component | * Right Component | = Product |"
    separator: str = "|---|---|---|"
    rows: list[
        tuple[MultiVectorBase, MultiVectorBase, dict[Blade, list[sympy.Expr]]]
    ] = _row_products(a, b)
    labels: dict[tuple[int, Blade, int], int] = _cancelling_labels(
        [product for _, _, product in rows]
    )
    marked_rows: set[int] = {row for row, _, _ in labels}
    lines: list[str] = [
        f"| {_latex(left, TABLE_CELL_WIDTH)} "
        f"| {_with_operator('*', _latex(right, TABLE_CELL_WIDTH))} | "
        + _with_operator(
            "=",
            _marked_product_latex(row, product, labels)
            if row in marked_rows
            else _latex(left * right, TABLE_CELL_WIDTH),
        )
        + " |"
        for row, (left, right, product) in enumerate(rows)
    ]
    return "\n".join([header, separator, *lines])


def show_mult(a: MultiVectorBase, b: MultiVectorBase) -> None:
    """Display (in a notebook) the full distributive expansion of ``a * b``.

    Shows the product to evaluate, the table of every term-by-term product
    (``product_table_markdown``, where terms that cancel in the sum carry the same
    number), then the sum, all rendered as LaTeX.
    """
    display(Markdown("**We want to evaluate**"))
    left: str = _math_body(_latex(a, LATEX_LINE_WIDTH // 2))
    right: str = _math_body(_latex(b, LATEX_LINE_WIDTH // 2))
    display(Math(latex_broken([f"({left})", f"* ({right})"])))
    display(Markdown("**Multivector Multiplication is distributive over addition**"))
    table: str = product_table_markdown(a, b)
    display(Markdown(table))
    if "underbrace" in table:
        display(Markdown("Terms with the same number cancel in the sum."))
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


def _pair_labels(
    left_terms: Sequence[sympy.Expr], right_terms: Sequence[sympy.Expr]
) -> tuple[list[int | None], list[int | None]]:
    """Number the pairs of equal terms that cancel in ``(left) - (right)``.

    Each left term is paired with the first equal, still-unpaired right term; a
    pair gets the next number, the same on both of its terms. A term left over
    gets ``None``. (Terms on one side never cancel each other: sympy has already
    combined them when it expanded the side.)

    >>> a, b, c = sympy.symbols("a b c")
    >>> _pair_labels([a, b], [b, a])
    ([1, 2], [2, 1])
    >>> _pair_labels([a, c], [b])
    ([None, None], [None])
    """
    right_labels: dict[int, int] = {}
    left_labels: list[int | None] = []
    term: sympy.Expr
    for term in left_terms:
        match_index: int | None = next(
            (
                index
                for index, other in enumerate(right_terms)
                if index not in right_labels
                and (other == term or sympy.expand(other - term) == 0)
            ),
            None,
        )
        if match_index is None:
            left_labels.append(None)
        else:
            right_labels[match_index] = len(right_labels) + 1
            left_labels.append(right_labels[match_index])
    return left_labels, [right_labels.get(index) for index in range(len(right_terms))]


def _marked_tokens(
    terms: Sequence[sympy.Expr], labels: Sequence[int | None]
) -> list[str]:
    """``terms`` as signed LaTeX pieces of one sum (``["0"]`` when empty), each
    labelled term under a numbered ``\\underbrace``.

    >>> a, b = sympy.symbols("a b")
    >>> _marked_tokens([a, -b], [1, None])
    ['\\\\underbrace{a}_{1}', '- b']
    """

    def part(position: int, term: sympy.Expr, label: int | None) -> str:
        negative: bool = term.could_extract_minus_sign()
        body: str = sympy.latex(-term if negative else term)
        marked: str = body if label is None else f"\\underbrace{{{body}}}_{{{label}}}"
        return ("- " if negative else ("" if position == 0 else "+ ")) + marked

    return [
        part(position, term, label)
        for position, (term, label) in enumerate(zip(terms, labels, strict=True))
    ] or ["0"]


def _common_denominator(left: Real, right: Real) -> sympy.Expr:
    """The least common multiple of the denominators of the expanded terms of
    ``left`` and ``right``.

    >>> a, b = sympy.symbols("a b", positive=True)
    >>> _common_denominator(a / b, 1 / (a * b))
    a*b
    >>> _common_denominator(a / (a + b) + b / (a + b), 1)
    a + b
    >>> _common_denominator(a, b)
    1
    """
    return sympy.lcm(
        [
            sympy.fraction(term)[1]
            for term in [*_signed_terms(left), *_signed_terms(right)]
        ]
        or [sympy.Integer(1)]
    )


#: The longest cancellation line, in LaTeX characters, worth showing term by term.
#: A longer one (sides that cancel only through a square-root or trigonometric
#: identity, expanded into hundreds of terms) is shown by its residual alone.
LONGEST_CANCELLATION_LINE: int = 3000


def _paired_line(
    left: sympy.Expr, right: sympy.Expr, prefix: str
) -> tuple[str, sympy.Expr]:
    """``(left terms) - (right terms) = residual`` with the cancelling pairs
    numbered, and the residual of the expansion."""
    left_terms: list[sympy.Expr] = _signed_terms(left)
    right_terms: list[sympy.Expr] = _signed_terms(right)
    left_labels: list[int | None]
    right_labels: list[int | None]
    left_labels, right_labels = _pair_labels(left_terms, right_terms)
    residual: sympy.Expr = sympy.expand(left - right)
    # the residual as its own terms, so a long one can break across rows too
    result: list[str] = _marked_tokens(
        _signed_terms(residual), [None] * len(_signed_terms(residual))
    )
    result[0] = "= " + result[0]
    simplest: sympy.Expr = sympy.simplify(residual)
    if simplest != residual:
        result.append("= " + sympy.latex(simplest))
    tokens: list[str] = _marked_tokens(left_terms, left_labels)
    if right_terms:
        right_tokens: list[str] = _marked_tokens(right_terms, right_labels)
        tokens[0] = "(" + tokens[0]
        tokens[-1] = tokens[-1] + ")"
        right_tokens[0] = "- (" + right_tokens[0]
        right_tokens[-1] = right_tokens[-1] + ")"
        tokens.extend(right_tokens)
    tokens.extend(result)
    tokens[0] = prefix + tokens[0]
    return latex_broken(tokens), residual


def _difference_latex(left: Real, right: Real, name: str) -> str:
    """One LaTeX line showing the number ``left - right`` cancel term by term.

    Each side is simplified, then both are expanded into monomials and the
    cancelling pairs numbered (``_pair_labels``). If the terms do not cancel as
    written because the sides are fractions, both sides are first multiplied by
    their common denominator ``D``, and the line says so. Whatever is left is the
    residual; when it is not visibly ``0``, the line also shows what it simplifies
    to. A line longer than ``LONGEST_CANCELLATION_LINE`` shows only the residual and
    what it simplifies to. ``name`` (the blade, or empty for a number) starts the
    line.
    """
    # each side in its simplest form first: a computed side (a round trip through
    # a frame, say) can be a large unsimplified expression whose expansion is slow
    left = sympy.simplify(sympy.sympify(left))
    right = sympy.simplify(sympy.sympify(right))
    prefix: str = name + ":\\quad " if name else ""
    line: str
    residual: sympy.Expr
    line, residual = _paired_line(left, right, prefix)
    if residual != 0:
        denominator: sympy.Expr = _common_denominator(left, right)
        if denominator != 1:
            factor: str = sympy.latex(denominator)
            if denominator.is_Add:
                factor = f"({factor})"
            scaled_prefix: str = (
                ",\\ ".join(
                    [*([name] if name else []), f"\\text{{both sides}} * {factor}"]
                )
                + ":\\quad "
            )
            scaled_line: str
            scaled_residual: sympy.Expr
            scaled_line, scaled_residual = _paired_line(
                sympy.cancel(left * denominator),
                sympy.cancel(right * denominator),
                scaled_prefix,
            )
            if scaled_residual == 0:
                line = scaled_line
    if len(line) > LONGEST_CANCELLATION_LINE:
        difference: sympy.Expr = sympy.simplify(left - right)
        line = f"{prefix}\\text{{left}} - \\text{{right}} = {sympy.latex(difference)}"
    return line


def _coefficients(value: MultiVectorBase | Real) -> Mapping[Blade, Real]:
    """``value``'s blade dict; a number is a scalar-blade dict (empty for ``0``)."""
    match value:
        case MultiVectorBase():
            return value.to_blade_dict()
        case _:
            return {} if sympy.sympify(value) == 0 else {(): value}


def cancellation_latex(
    left: MultiVectorBase | Real, right: MultiVectorBase | Real
) -> list[str]:
    """LaTeX lines showing ``left − right`` cancel term by term.

    Each coefficient is expanded into monomials. A monomial of ``left`` that also
    appears in ``right`` is a cancelling pair: both copies are marked
    ``\\underbrace{…}_{k}`` with the same number ``k``, so a reader can match them
    (and, on paper, cross them off). Whatever does not cancel is left unmarked, and
    the line ends with the residual, ``0`` for an identity. Each side is simplified
    first, and sides that are fractions may be multiplied by their common
    denominator (``_difference_latex``).

    Either side may be a multivector or a number. Two numbers give one line; a
    multivector gives one line per blade, named by the blade.

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

        Two numbers: each side is simplified first, so a sum of fractions that is
        ``1`` shows as ``1``.

        >>> cancellation_latex(a / (a + b) + b / (a + b), 1)
        ['(\\\\underbrace{1}_{1}) - (\\\\underbrace{1}_{1}) = 0']
    """
    if not isinstance(left, MultiVectorBase) and not isinstance(right, MultiVectorBase):
        return [_difference_latex(left, right, "")]
    left_coefficients: Mapping[Blade, Real] = _coefficients(left)
    right_coefficients: Mapping[Blade, Real] = _coefficients(right)
    # a blade whose coefficient is 0 on both sides (stored, but simplifying to 0)
    # has nothing to show
    blades: list[Blade] = [
        blade
        for blade in sorted(
            set(left_coefficients) | set(right_coefficients),
            key=lambda blade: (len(blade), blade),
        )
        if sympy.simplify(sympy.sympify(left_coefficients.get(blade, 0))) != 0
        or sympy.simplify(sympy.sympify(right_coefficients.get(blade, 0))) != 0
    ]
    return [
        _difference_latex(
            left_coefficients.get(blade, 0),
            right_coefficients.get(blade, 0),
            "\\text{scalar}" if blade == () else blade_latex(blade),
        )
        for blade in blades
    ] or ["0 - 0 = 0"]


def _side_latex(value: MultiVectorBase | Real) -> str:
    """``value`` as LaTeX without delimiters: a multivector through ``_latex``, a
    number with each numerator expanded."""
    match value:
        case MultiVectorBase():
            return _math_body(_latex(value))
        case _:
            numerator: sympy.Expr
            denominator: sympy.Expr
            numerator, denominator = sympy.fraction(
                sympy.together(sympy.sympify(value))
            )
            return sympy.latex(sympy.expand(numerator) / denominator)


def show_difference(
    left: MultiVectorBase | Real, right: MultiVectorBase | Real
) -> None:
    """Display (in a notebook) ``left − right`` cancelling term by term.

    For a check whose two sides the notebook has just shown: one line per blade
    (a single line for numbers) from ``cancellation_latex``, where matching terms
    carry the same number under an ``\\underbrace``, so the reader watches the
    terms disappear instead of being handed a bare ``0``.

    Args:
        left: the left side, already computed.
        right: the right side.
    """
    display(Markdown("Terms with the same number cancel:"))
    text: str
    for text in cancellation_latex(left, right):
        display(Math(text))


def show_cancellation(
    left: MultiVectorBase | Real,
    right: MultiVectorBase | Real,
    left_name: str,
    right_name: str,
) -> None:
    """Display (in a notebook) both sides of an identity, then their difference
    cancelling term by term.

    Shows ``left`` and ``right`` expanded, then one line per blade from
    ``cancellation_latex``, where matching terms carry the same number under an
    ``\\underbrace``, so the reader watches the terms disappear instead of being
    handed a bare ``0``. Either side may be a multivector or a number.

    Args:
        left: the left side, already computed.
        right: the right side, already computed.
        left_name: LaTeX for how the left side was built, e.g. ``a * (b + c)``.
        right_name: LaTeX for the right side.
    """
    display(Markdown("**The left side**"))
    display(Math(f"{left_name} = " + _side_latex(left)))
    display(Markdown("**The right side**"))
    display(Math(f"{right_name} = " + _side_latex(right)))
    display(
        Markdown(
            "**Their difference, blade by blade.** Terms with the same number cancel:"
        )
    )
    text: str
    for text in cancellation_latex(left, right):
        display(Math(text))
