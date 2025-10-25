import dataclasses
import numbers
import typing


@dataclasses.dataclass
class MultiVector:
    components: dict[tuple[tuple[int], numbers.Number], ...]

    def __add__(self, other: typing.Self) -> typing.Self:
        combined_dict: dict[tuple[tuple[int], numbers.Number], ...] = {}
        for key, value in self.components.items():
            combined_dict[key] = value
        for key, value in other.components.items():
            if key in combined_dict:
                combined_dict[key] += value
            else:
                combined_dict[key] = value
        return MultiVector(components=combined_dict)

    def __mul__(self, other: typing.Self) -> typing.Self:
        if isinstance(other, numbers.Number):
            combined_dict: dict[tuple[tuple[int], numbers.Number], ...] = {}
            for key, value in self.components.items():
                combined_dict[key] = other * value
            return MultiVector(components=combined_dict)

    def __rmul__(self, other: typing.Self) -> typing.Self:
        if isinstance(other, numbers.Number):
            return self * other


x: MultiVector = MultiVector({(1,): 1})
y: MultiVector = MultiVector({(2,): 1})
z: MultiVector = MultiVector({(3,): 1})
