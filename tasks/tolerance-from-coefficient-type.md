# Decide float tolerance from the coefficients, not a threaded flag

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; scaffolded from the research in
`tasks/archive/2026/11/18/research-numeric-symbolic-mode-threading.md`)

## BLUF

`float_close_to_zero: bool = False` is threaded through 62 sites: `base.py`, `frame.py`,
`transforms.py`, the generator and tests. Most layers accept it only to pass it on. Change it to
`float_close_to_zero: bool | None = None`, where `None` means tolerant when any coefficient involved
is a Python `float` and exact otherwise. Then drop the pass-through plumbing where the bottom-level
comparison already sees the same values. Done means:
- the default decides from the values;
- an explicit `True` / `False` still overrides;
- `frame.py`'s `_has_float` is the one shared helper, moved to `base.py`;
- the generator emits the new signature;
- there is a `CHANGELOG.md` entry, since a float caller relying on the exact default changes;
- the gates pass.

## Context (read first)

- `tasks/reference/numeric-symbolic-mode.md`: the inventory, the options with sources, and why this
  option (d), not a global or a `ContextVar`. It also gives the closure example that rules out a
  setting read when a returned function is called.
- `src/gacalc/frame.py` `_has_float`: the existing helper, already used instead of the flag in two
  places.
- `src/gacalc/transforms.py` `_is_zero`, `require_on_line`, `coordinate_along`, and the four
  line-to-line and line-to-plane factories: the threaded sites.
- `tools/gen_specialized.py`: emits `float_close_to_zero: bool = False` on the generated `Vector`
  methods (7 sites). Regenerate; never edit `g*.py`.

## Plan

1. Move `_has_float` to `base.py` (public or private: decide while implementing). Resolve `None`
   in `is_orthogonal_to` / `is_parallel_to` and `_is_zero` from the values being compared.
2. Change every signature's default to `None`. Where a layer only passed the flag on, stop passing
   it, and keep the parameter as the override.
3. Update the generator, then run `make generate`, `make check-generated` and `make check-regions`.
4. Tests:
   - float inputs with no flag are tolerant;
   - integer and symbolic inputs are exact;
   - `True` / `False` still force the choice;
   - a factory built from exact inputs and called on float input is tolerant at call time.
5. `CHANGELOG.md` `[Unreleased]` › Changed; update the reference doc's "Today" section.

## Open questions

None yet.
