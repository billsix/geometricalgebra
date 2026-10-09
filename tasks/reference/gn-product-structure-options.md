# Structuring the Gn geometric product: named record vs. passing tuples

**Reference document** — a design-rationale comparison of how `Gn._geometric_product` carries a
`(blade, coefficient)` term through its `decrease_grade` canonicalization: the current
`BladeDictionaryEntry(NamedTuple)` vs. the earlier plain-tuple form the maintainer recalls as
"cleaner", vs. other options. All options keep behaviour identical. Durable; update in place. Written
2026-10-09 (William Emerison Six <billsix@gmail.com>) for
`tasks/archive/2026/10/09/analyze-gn-product-tuple-vs-named-type.md`. The product mechanism itself (the
four moves) is `tasks/reference/gn-multiplication-by-hand.md`.

## What the code does today

`Gn._geometric_product` (`src/gacalc/gn.py`) multiplies by concatenating each left blade with each
right blade, canonicalizing the concatenation with the recursive `decrease_grade`, promoting each
result to a one-term `Gn`, and summing. The unit carried through the recursion is a **named record**:

```text
class BladeDictionaryEntry(NamedTuple):
    blade: Blade          # Blade = tuple[int, ...]
    coefficient: Real
    def as_multivector(self) -> Gn: ...

def decrease_grade(basis_blade: BladeDictionaryEntry) -> BladeDictionaryEntry:
    match basis_blade.blade:
        case () | (_,):            return basis_blade
        case (a, c, *rest) if a == c:  return decrease_grade(BladeDictionaryEntry(blade=(*rest,),         coefficient=basis_blade.coefficient))
        case (a, c, *rest) if a > c:   return decrease_grade(BladeDictionaryEntry(blade=(c, a, *rest),    coefficient=-basis_blade.coefficient))
        case (a, c, *rest) if a < c:   ...   # canonicalize the tail, then insert `a`
```

## What it used to do (the "cleaner" tuple form)

Commit `ca31ce5` ("use tuple instead, directly", then `src/geometricalgebra/multivector.py`) passed the
blade and coefficient as **two positional values**, returning a **bare 2-tuple**:

```text
def decrease_grade(basis_blades: tuple[int, ...], magnitude: Numeric
                   ) -> tuple[tuple[int, ...], Numeric]:
    match basis_blades:
        case ():                       return (), magnitude
        case (a,):                     return (a,), magnitude
        case (a, c, *rest) if a == c:  return decrease_grade(tuple(rest), magnitude)
        case (a, c, *rest) if a > c:   return decrease_grade((c, a, *rest), -magnitude)
        case (a, c, *rest) if a < c:
            sorted_rest, new_mag = decrease_grade((c, *rest), magnitude)
            ...
```

The maintainer's read is right about where it felt cleaner: the **recursive calls and the
return-destructure are terser** — `return (c, a, *rest), -magnitude` and
`sorted_rest, new_mag = decrease_grade(...)` carry no constructor name, and the function matches
directly on `basis_blades` instead of `basis_blade.blade`. Later `18e1536` ("extracted type")
introduced the named record. So the history is exactly the oscillation the maintainer remembers.

## The options (behaviour identical in every one)

| option | the term is… | `match` | construction | annotation | notes |
|---|---|---|---|---|---|
| **A. two positional values** (old) | `blade`, `coef` as separate params; return `(blade, coef)` | `match basis_blades:` directly | terse: `return (c, a, *rest), -mag` | opaque `tuple[tuple[int,…], Real]` | destructures cleanly; meaning of the pair is positional/implicit |
| **B. `NamedTuple`** (current) | one `BladeDictionaryEntry(blade, coefficient)` | `match entry.blade:` | verbose: `BladeDictionaryEntry(blade=…, coefficient=…)` ×4 | self-documenting | field names read well in the arms; carries `as_multivector()`; still a tuple (iterable/positional) |
| **C. type-aliased tuple** | `BladeTerm = tuple[Blade, Real]`; still positional | `match term[0]:` or unpack first | terse like A | named alias (not opaque) | A's terseness with a readable return type; no field names, no method home |
| **D. frozen dataclass** | `@dataclass(frozen=True, slots=True)` record | `match term.blade:` (or class pattern via `__match_args__`) | verbose like B | self-documenting | heavier than NamedTuple; not tuple-ish; only worth it if it must be non-iterable or grow behaviour |

A note on `match`: every option pattern-matches fine. The arms here match on the **blade tuple**
(`()` / `(a,)` / `(a, c, *rest)`), which is `basis_blades` directly in A/C and `entry.blade` in B/D —
a field access, not a structural difference.

## Trade-offs that actually matter here

- **Readability of the arms.** B/D's `basis_blade.coefficient` / `.blade` name the parts; A/C rely on
  the reader knowing the pair's order. In a 4-arm sign-tracking recursion, names help a little.
- **Construction noise.** A/C are markedly terser at the recursive calls (the bulk of the function);
  B/D repeat the constructor name and keyword fields four times.
- **Where `as_multivector()` lives.** B gives the term a natural method home, used by the outer
  comprehension (`decrease_grade(...).as_multivector()`). A/C would make that a free function
  `term_to_multivector(blade, coef)` or inline — slightly less tidy at the call site.
- **Hot loop.** The product maps `decrease_grade` over **every pair of blades** from the two factors.
  `NamedTuple` and a plain tuple allocate the same (a tuple); a frozen dataclass with `slots=True` is
  comparable. None of the options changes the asymptotics; this is not a performance decision.
- **Type precision.** A's `tuple[tuple[int,…], Real]` return is the one genuinely poor spelling; C or
  B both fix that without changing anything else.

## Recommendation

**The current `NamedTuple` (B) is defensible and the honest "cleanest" win over the old form is small
and local** — it is the recursive-call verbosity, not the whole design. Two reasonable directions, both
behaviour-identical, for the maintainer to pick:

1. **Keep B.** The field names earn their keep in the four arms and `as_multivector()` has a home; the
   construction verbosity is the price. No work. *(Recommended if the arms' readability is the priority.)*
2. **Move to C (`BladeTerm = tuple[Blade, Real]`).** Recover the old terseness (positional return,
   direct `match`) while naming the return type, and relocate `as_multivector` to a small free
   function. *(Recommended if the maintainer wants the old "cleaner" feel back without the opaque
   annotation that made the first tuple era worse than it needed to be.)*

A/D are not recommended: A reintroduces the opaque annotation; D is heavier than B for no gain (the
term is never mutated and does not need to be non-iterable).

The pick is a taste call on "field names vs. terseness", not a correctness one.

**Decision (William Emerison Six <billsix@gmail.com>, 2026-10-09): keep the current `NamedTuple`
(option B).** Option C (the type-aliased tuple) was considered and declined; the field names in the
four `match` arms and the `as_multivector()` method home were judged worth the small construction
verbosity. No change to the code.
