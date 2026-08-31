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

r"""Custom blade **display** symbols (``set_blade_symbols`` / ``blade_latex`` /
``blade_dict_latex``'s ``symbols`` parameter) -- LaTeX rendering only.

The layered design (``tasks/custom-symbols-and-vector-calc.md``): a pure
``symbols`` parameter underneath (what these tests mostly use, so they stay
deterministic), one module-global session map on top -- required because Jupyter
invokes ``_repr_latex_()`` with no arguments, so plain cell output can only be
customized through state the method can reach.  Rename-only, canonical keys,
``__repr__`` and the blade-tuple interchange format untouched.
"""

from collections.abc import Iterator

import pytest

from gacalc.base import blade_dict_latex, blade_latex, set_blade_symbols
from gacalc.gn import e_1, e_2

IJK: dict[tuple[int, ...], str] = {
    (1,): r"\mathbf{i}",
    (2,): r"\mathbf{j}",
    (3,): r"\mathbf{k}",
}


@pytest.fixture(autouse=True)
def _reset_session_symbols() -> Iterator[None]:
    """Every test leaves the session map as it found it: empty (the default)."""
    yield
    set_blade_symbols({})


def test_default_rendering_unchanged() -> None:
    assert blade_latex((1,), symbols={}) == r"\mathbf{\vec{e}}_{1}"
    assert blade_dict_latex({(1,): 2}) == r"$2\mathbf{\vec{e}}_{1}$"


def test_scalar_blade_renders_as_one() -> None:
    assert blade_latex((), symbols={}) == "1"


def test_explicit_symbols_parameter() -> None:
    assert blade_latex((1,), symbols=IJK) == r"\mathbf{i}"
    assert blade_dict_latex({(1,): 2}, symbols=IJK) == r"$2\mathbf{i}$"


def test_unmapped_blade_falls_back_to_e_notation() -> None:
    assert (
        blade_dict_latex({(1, 2): 5}, symbols=IJK)
        == r"$5\mathbf{\vec{e}}_{1} \mathbf{\vec{e}}_{2}$"
    )


def test_session_map_applies_to_repr_latex() -> None:
    """The top-of-notebook workflow: set once, every later display honors it."""
    set_blade_symbols(IJK)
    assert (2 * e_1 + 3 * e_2)._repr_latex_() == r"$2\mathbf{i} +  3\mathbf{j}$"


def test_reset_restores_default_rendering() -> None:
    set_blade_symbols(IJK)
    set_blade_symbols({})
    assert (
        2 * e_1 + 3 * e_2
    )._repr_latex_() == r"$2\mathbf{\vec{e}}_{1} +  3\mathbf{\vec{e}}_{2}$"


def test_explicit_parameter_bypasses_session_map() -> None:
    """``symbols={}`` means "no custom symbols" even while the session map is
    set -- the pure layer tests lean on exactly this."""
    set_blade_symbols(IJK)
    assert blade_dict_latex({(1,): 2}, symbols={}) == r"$2\mathbf{\vec{e}}_{1}$"


def test_non_canonical_key_raises() -> None:
    with pytest.raises(ValueError, match="not canonical"):
        set_blade_symbols({(2, 1): "x"})


def test_plain_repr_is_untouched() -> None:
    """Display-only: ``__repr__`` (and the stored value) never see the symbols."""
    set_blade_symbols(IJK)
    assert r"\mathbf" not in repr(2 * e_1 + 3 * e_2)
