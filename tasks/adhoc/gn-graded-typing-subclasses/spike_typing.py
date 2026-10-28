"""Static-typing spike: does a TypeGuard / TypeIs narrow a Gn to a graded subtype?

Task: tasks/gn-graded-typing-subclasses.md. Throwaway (git rm'd at archive).
Run: ty check tasks/adhoc/gn-graded-typing-subclasses/spike_typing.py
The `reveal_type` lines make ty print what it inferred in each branch.
"""

from __future__ import annotations

import typing

from gacalc.gn import Gn


class Vector(Gn):
    """Narrowing subtype, no new fields."""

    __slots__ = ()


def is_vector_guard(v: Gn) -> typing.TypeGuard[Vector]:
    """TypeGuard flavour (narrows the positive branch only)."""
    return v.is_vector()


def is_vector_is(v: Gn) -> typing.TypeIs[Vector]:
    """TypeIs flavour (narrows both branches; requires Vector <: Gn)."""
    return v.is_vector()


def use_guard(v: Gn) -> None:
    """Expect: Vector inside the branch, Gn after."""
    if is_vector_guard(v):
        typing.reveal_type(v)
    typing.reveal_type(v)


def use_is(v: Gn) -> None:
    """Expect: Vector inside the branch, narrowed (Gn & ~Vector) in else."""
    if is_vector_is(v):
        typing.reveal_type(v)
    else:
        typing.reveal_type(v)
