# Why don't the generated graded subtypes (and `Scalar`) have `slots=True`?

**Created:** 2026-06-27 · **Completed:** 2026-06-27

## Question

`Gn` and the full specialized classes `G1`/`G2`/`G3` were `@dataclass(slots=True)`, but the generated
graded subtypes (`Vector_n`/`Bivector_n`/`Trivector3`/`Rotor_n`) and the shared `Scalar` were only
`@dataclass(eq=False)`, so their instances carried a per-instance `__dict__` (checked at runtime after
generating). Why, and should they be slotted too?

## Findings (2026-06-27)

**A historical oversight, not a technical blocker.** `slots=True` came in with commit `4d6380a`
("upated using match"), when the generator still emitted source as strings and only the full classes
existed. The graded subtypes and `Scalar` were added later
(`tasks/archive/2026/06/06/graded-blade-subtypes.md`) with just `eq=False`, and the flag was never carried
over.

**No inheritance conflict.** Every generated class inherits from `MultiVectorBase`, which has
`__slots__ = ()` so slotted subclasses get no `__dict__`; the graded subtypes do not inherit from the full
classes, so there is no duplicate-slot problem for `coeff_e_1`. The full classes already combined, with
`slots=True` and passing tests, everything the graded subtypes have: the empty-slots base, `coeff_*`
fields with numeric defaults, basis blades as `ClassVar` in the body plus post-class
`Cls.e_1 = Cls.from_blade_dict(...)` assignments (class-attribute writes are unaffected by slots), and
zero-arg `super()` calls (the CPython bug with slots was fixed in 3.11; the project ran 3.14). A probe
slotted subclass with the graded layout confirmed it.

## What was done

`generate_graded_type` and `generate_scalar` in `tools/gen_specialized.py` emit
`dataclass_decorator(eq=False, slots=True)`, matching `generate_class`, so every generated value type is
slotted. That removes the per-instance `__dict__` (less memory, faster attribute access) from the types
most often created in bulk (numeric pipelines, plotting, mvp rotations), at no API cost: slots forbid
setting undeclared instance attributes, which is desirable for value types. No CLAUDE.md change was
needed, since it did not claim otherwise.

## Verification

After regenerating, `Vector2` / `Bivector2` / `Rotor2` / `Scalar` had `__slots__` and no `__dict__`; the
basis class constants still resolved; arithmetic and `coefficient()` still worked. `ruff` and
`ty check src tools` were clean, regeneration was deterministic (twice, identical), and the full suite
passed (246). This was a behavioural generator change, so the output differed from the old baseline (the
decorator line) by design; the determinism and test gates covered it.
