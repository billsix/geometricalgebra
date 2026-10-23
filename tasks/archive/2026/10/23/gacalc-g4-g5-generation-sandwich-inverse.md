# g4/g5 generation fails: the Versor sandwich arm inverts a generic even element

**Status:** done 2026-10-23 (fix committed; archived). **Priority:** 3 **Difficulty:** 5
**Created:** 2026-10-22; **Done:** 2026-10-23 (William Emerison Six <billsix@gmail.com>). Surfaced
while verifying the 𝒢₄/𝒢₅ half of `tasks/generalize-sandwich-other-grades.md`.

## What it was

`GACALC_DIMS=1,2,3,4,5 python tools/gen_specialized.py` (i.e. `make generate-all` / `make dist` /
`make test-all-dims`) raised, at `g4`:

```
RuntimeError: inverse() supports a blade or versor (where Ã * A is a scalar); the general
mixed-grade multivector inverse is not implemented
```

The generated `Versor.sandwich` closed form `R * x * R.inverse()` is derived symbolically over a
**generic** even element `R`. Through 𝒢₃ a generic even element is versor-invertible (`R̃ * R` is a
scalar: `(s − B)(s + B) = s² − B²`), so `inverse()` succeeds; in **𝒢₄+** a generic even element has a
grade-4 part and `R̃ * R` is not a scalar, so `inverse()` correctly raised. Genuine math, not a
host/sympy artifact. It blocked `make dist` (which bakes g4/g5) and therefore the 0.2.0 release.

## Fix — option 1 (maintainer-approved 2026-10-23: "go with your recommendation")

`tools/gen_specialized.py`, two edits:

- **`versor_extras()`** — the specialized `Versor.sandwich` `dispatch_method` append is wrapped in
  `if n <= 3:`. 𝒢₄/𝒢₅ emit no closed-form sandwich and the graded `Versor` inherits
  `MultiVectorBase.sandwich` (runtime `type(x)` projection, no closed-form `inverse()`) — still
  correct, just not a specialized closed form.
- **`header()`** — the `_OperandT` import narrowed from `n >= 2` to `2 <= n <= 3` (it is used only by
  the specialized sandwich, so it would be an unused F401 in g4/g5 otherwise).

Work commit: `git log` subject "restrict specialized Versor.sandwich to dims <=3 so g4/g5 generate".
Durable rationale harvested to `tasks/reference/generated-algebra-generation-cost.md` (point 3, the
n≥4-only generator-bug class).

## Verification (2026-10-23)

- `GACALC_DIMS=1,2,3,4,5 python tools/gen_specialized.py` → all of g1–g5 written + ruff-formatted,
  exit 0 (the former failure point, g4, now generates).
- g1–g3 suite: **707 passed** — no regression on the n≤3 path (the fix is a pure no-op there).
- Runtime intent: `g2.Versor` keeps its specialized `sandwich`; `g4.Versor` has no own `sandwich` and
  the inherited base `sandwich` returns its operand for the identity versor.
- **NOT run this session:** the full container `make test-all-dims` (~1.5 h, g5 ~87 min) — a
  pre-release gate for the maintainer to run before `make dist`/release.

## See also

- `tasks/generalize-sandwich-other-grades.md` — its 𝒢₄/𝒢₅ half is now **unblocked**: g4/g5 generate,
  and the sandwich there is the inherited base fallback (already covered by the base tests).
- `tasks/reference/generated-algebra-generation-cost.md` — release-only design + the full-dim gate.
- `tasks/lean-general-multivector-inverse.md` — option 3 (implement the general inverse), not pursued.
