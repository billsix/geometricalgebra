# Fast paths in the generated dispatch (measure with Code the Classics)

**Status:** proposed — needs go-ahead
**Created:** 2026-07-09 (Bill: "log the fast path stuff as a task")

## Motivation

The CTC games now use `gacalc.g2.Vector2` directly. The synthetic
busy-actor benchmark (2026-07-09, mvp container): **5.56 µs/actor-frame
direct gacalc vs 2.20 µs for the old two-float shim** — ~2.5× per-op
overhead, none of it math. Acceptable today (~6.7% of a 60 fps frame at
an unrealistic 200 busy actors), but if a game ever drags, the fix is
HERE — generator-level fast paths that every consumer inherits — never a
hand-written shim revival.

Where the time goes (per `a + b` on a graded type):

- the generated `__add__`/`__mul__`/product methods walk a `match rhs:`
  ladder (Scalar, Vector2, Bivector2, Rotor2, G2, numbers) — one
  isinstance-style class-pattern test per arm until the hit; the
  overwhelmingly common same-type case is not first.
- the number case of `__add__` wraps the scalar in an intermediate
  `Scalar(...)` object and re-dispatches instead of doing direct field
  arithmetic (scalar `__mul__` already does it right via `scaled_stmt`).
- `magnitude`/`magnitude_squared`/`normalize` are inherited
  `MultiVectorBase` methods that round-trip through
  `to_blade_dict()`/`from_blade_dict()` dict building instead of touching
  the named fields (compare: `sandwich` gets a generated closed form).
- `typing.cast(...)` / `cast_coef` are runtime identity *calls* on hot
  paths (cast is a real function call, ~50 ns each).

## Candidate fast paths (all in tools/gen_specialized.py — never hand-edit g*.py)

1. Emit an exact-type early-out before the match ladder:
   `if type(rhs) is Vector2: return type(self)(...)` — the same-type case
   skips the pattern machinery entirely.
2. Order the remaining match arms by measured frequency (see Metrics).
3. Number case of `__add__`/`__sub__`: direct field arithmetic (only the
   scalar field changes), no intermediate `Scalar` + re-dispatch.
4. Generated closed-form `magnitude` / `magnitude_squared` / `normalize`
   on the graded types (`sqrt(x*x + y*y)` on the named fields), keeping
   base.py's numeric-preservation rule (float in → float out; int routes
   through sympy for exactness; symbolic stays symbolic).
5. Audit `cast_coef`/`cast_self` emission on hot paths — where the
   checker allows, emit plain expressions instead of runtime `cast()`
   calls.

## Metrics — REQUIRED: derive them from Code the Classics, in 2D (Bill)

Do NOT tune against guesses or a synthetic-only mix. The CTC games are
the real 2D consumer; use them to generate the numbers:

- **Op-mix profile**: instrument or statically count the games' vector
  operations (which dunders, which operand types — same-type add/sub,
  scalar mul, scalar_product, magnitude/normalize, rotor sandwich) across
  the 10 games' per-frame paths (soccer ball physics + AI, kinetix ball
  loop, avenger enemy swarm are the hot ones). The frequency table drives
  arm ordering (candidate 2) and says which fast paths matter at all.
- **Before/after benchmark**: the busy-actor mix from
  mvp `tasks/archive/2026/07/08/ctc-vector2-deferral.md` (2.20 µs shim /
  2.82 µs subclass / 5.56 µs direct baselines), rerun identically in the
  mvp container, PLUS a headless-loop measurement of at least one real
  game's update path if practical.
- Acceptance: meaningful reduction on the CTC 2D mix (target: within ~1.5×
  of the old float shim), `make test` (277+) green, `make check-generated`
  deterministic, format.sh clean, and mvp's ctc gates green against the
  result.

## Related (separate, pre-tag candidate — not this task)

`plane_rotation` numeric preservation: with a numeric theta the rotor
inherits sympy-exact coefficients from the int-coeff basis constants
(wedge -> normalize -> Rational), so every rotated vector comes back with
sympy Floats and downstream arithmetic goes ~6x slower (measured
2026-07-09: 3.71 vs 0.60 us per add). That's a correctness-of-contract
fix (base.py's numeric-preservation rule), wanted BEFORE the 0.0.8 tag;
kinetix's `_turn` and every mvp demo frame hit it.
