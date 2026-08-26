"""Shared helpers for the gacalc test suite."""

import random

from gacalc.gn import Gn, e_1, e_2, e_3


def random_vector(dim: int) -> Gn:
    """A random ``dim``-D vector with float coefficients in ``[-5, 5)``.

    For the float-tolerant numeric conformance checks; ``random`` is fine here --
    these are test vectors, not cryptographic material.  Seed ``random`` in the
    caller for reproducibility.
    """
    basis: list[Gn] = [e_1, e_2, e_3][:dim]
    return sum(
        (random.uniform(-5.0, 5.0) * basis_vector for basis_vector in basis),  # noqa: S311
        start=Gn.zero(),
    )
