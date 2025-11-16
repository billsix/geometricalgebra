import dataclasses
import numbers
import typing

import sympy


@dataclasses.dataclass
class MultiVector:
    components: dict[tuple[int, ...], typing.Any]

    def __add__(self, other):
        combined_dict = {}
        for key, value in self.components.items():
            combined_dict[key] = value
        for key, value in other.components.items():
            if key in combined_dict:
                combined_dict[key] += value
            else:
                combined_dict[key] = value
            combined_dict[key] = sympy.simplify(combined_dict[key])
        return MultiVector(components=combined_dict)

    def __mul__(self, other):
        if self.components.keys() == tuple():
            combined_dict = {}
            for key, value in self.components.items():
                combined_dict[key] = sympy.simplify(
                    other * self.components[tuple()]
                )
            return MultiVector(components=combined_dict)
        elif isinstance(other, numbers.Number) or isinstance(other, sympy.Expr):
            combined_dict = {}
            for key, value in self.components.items():
                combined_dict[key] = sympy.simplify(other * value)
            return MultiVector(components=combined_dict)
        else:
            combined_dict = {}
            for key_left, value_left in self.components.items():
                for key_right, value_right in other.components.items():
                    my_type, sign = sort_types(key_left + key_right, 1)
                    existing_value_for_type = combined_dict.get(my_type, 0)
                    combined_dict[my_type] = sympy.simplify(
                        existing_value_for_type
                        + sign * value_left * value_right
                    )
            return MultiVector(components=combined_dict)

    def __rmul__(self, other):
        return self * other


x: MultiVector = MultiVector({(1,): 1})
y: MultiVector = MultiVector({(2,): 1})
z: MultiVector = MultiVector({(3,): 1})


def sort_types(foo: tuple[int, ...], val):
    def s(foo: list[int, ...], val):
        current_val: int = foo[0]
        for i in range(1, len(foo)):
            if foo[i] < current_val:
                return s(
                    foo[: i - 1] + [foo[i]] + [foo[i - 1]] + foo[i + 1 :], -val
                )
            else:
                current_val = foo[i]
        return foo, val

    foo_sorted, val = s(list(foo), val)
    return remove_same_components(tuple(foo_sorted), val)


def remove_same_components(foo: tuple[int, ...], val):
    def s(foo: list[int, ...], val):
        if foo == list():
            return foo, val
        current_val: int = foo[0]
        for i in range(1, len(foo)):
            if foo[i] == current_val:
                return s(foo[: i - 1] + foo[i + 1 :], val)
            else:
                current_val = foo[i]
        return foo, val

    foo_sorted, val = s(list(foo), val)
    return tuple(foo_sorted), val
