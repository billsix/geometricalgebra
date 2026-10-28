"""Runtime feasibility spike for Gn graded-typing subclasses.

Task: tasks/gn-graded-typing-subclasses.md. Throwaway investigation harness (git
rm'd at archive). Validates, at RUNTIME:

  1. Gn (a slots=True dataclass) can be subclassed cheaply with no new fields
     (`__slots__ = ()`), and such an instance constructs and operates normally.
  2. The shared `type(self).from_blade_dict(...)` construction pattern makes a
     naive subclass MIS-TYPE operation results: `vector * vector` lands on the
     `Vector` class even though the product is scalar + bivector -- the crux the
     design must widen around.
  3. The widening fix (build results via `Gn.from_blade_dict`) restores `Gn`.
"""

from __future__ import annotations

from gacalc.gn import Gn, e_1, e_2


class Vector(Gn):
    """A no-behaviour, no-new-field narrowing subclass of Gn."""

    __slots__ = ()


def as_vector(v: Gn) -> Vector:
    """Validate grade 1 and re-type the same blade-dict as a Vector."""
    if not v.is_vector():
        raise TypeError("not a grade-1 vector")
    return Vector(coefficient_of_blade=v.to_blade_dict())


def main() -> None:
    """Print the three findings."""
    a: Vector = as_vector(3 * e_1 + 4 * e_2)
    print("1. cheap subclass -> type(a) =", type(a).__name__, "| is_vector =", a.is_vector())
    product: Gn = a * a
    print("2. type(a*a) =", type(product).__name__, "(MIS-TYPED: product is scalar+bivector)")
    print("   (a*a).is_vector() =", product.is_vector(), "| value =", product)
    widened: Gn = Gn.from_blade_dict((a * a).to_blade_dict())
    print("3. widened via Gn.from_blade_dict -> type =", type(widened).__name__)


if __name__ == "__main__":
    main()
