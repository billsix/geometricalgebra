# Add a g2 `rotate_90_degrees` — a 90° turn in the e₁e₂ plane (= × pseudoscalar)

**Status:** proposed — a standalone design question for gacalc; needs a decision (does the library want this named convenience?). Researched 2026-09-04.
**Priority:** 7
**Difficulty:** 3

## BLUF

Consider giving 𝒢₂ a named **`rotate_90_degrees`**: a 90° rotation in the e₁e₂ plane. In 2-D
geometric algebra that rotation is exactly **multiplication by the unit pseudoscalar `e_12`** —
`(x, y) → (-y, x)` — so it is **exact** (`e_12` has ±1 coefficients; no `cos`/`sin`),
unlike the general-angle `plane_rotation(θ)` rotor. It would exist as an `InvertibleFunction`, so it
**composes** (its k-fold composition is the `k·90°` rotation `I^k`) and **inverts** (the −90° turn,
right-multiply by `−e_12`). The pedagogical value: it names, and its one-line body reveals, a
foundational 2-D GA identity — *multiplying a vector by the pseudoscalar rotates it a quarter turn*.

**It must be 𝒢₂-only.** gacalc once had a general planar `rotate_90_degrees` and **removed** it
because it "acted only in the e₁e₂ plane and silently mis-transformed a vector with an e₃+
component" (`transforms.py:39-43`) — `× e_12` sends `e_3` to a trivector in 3-D. That footgun does
not exist in 2-D, so a dimension-scoped 𝒢₂ version is safe.

## Context

- **The removal history (transforms.py:39-43):** the old dimension-agnostic `rotate(angle)` /
  `rotate_90_degrees` / `rotate_around` factories were dropped for the e₃+ mis-transform; the
  plane-explicit `plane_rotation(a, b)` is the general replacement. A new `rotate_90_degrees` avoids
  reopening that only by being **𝒢₂-only** — the dimension where "the e₁e₂ plane" is the whole space.
- **Precedent — the generated `cross` in 𝒢₃.** gacalc already emits a **dimension-specific,
  closed-form, type-precise** method: 𝒢₃'s `Vector` carries a generated `cross` (`Vector → Vector`),
  3-D only (`vectorcalc.py`; `tasks/archive/2026/08/31/generated-vector-cross.md`).
  `rotate_90_degrees` is the exact 2-D analogue: 𝒢₂-only, closed form, `Vector → Vector`.
- **Why a dedicated function, not `plane_rotation(e_1, e_2)(π/2)`.** That is the *general-angle*
  rotor (`exp(−B·θ/2)` from `cos`/`sin`); routing a fixed 90° turn through it loses exactness (a
  float π/2 gives `cos`/`sin` round-off) and is over-engineered for what is a plain signed
  coordinate swap. A quarter turn is not "an angle that happens to be 90°" — it is the pseudoscalar
  product, exact and angle-free.
- **Direction.** `v * e_12 = (-y, x)` is **+90°** (e₁ toward e₂, matching `plane_rotation`'s
  positive sense). `Vector.dual()` is the same operation the other way (−90°, `v · e_12⁻¹`).

## Proposed design

- **Form:** an **`InvertibleFunction`** (so it composes into `I^k` and inverts to −90°). Optionally
  also a `Vector.rotate_90_degrees()` method for discoverability (the `cross` shape) — decide.
- **Direction:** **+90°** (e₁→e₂); state it in the name/docstring.
- **Name:** `rotate_90_degrees` (reviving the old name, now safe because 𝒢₂-scoped). If the +90°
  sense should be in the name, `rotate_90_degrees_ccw` is an option.
- **Scope:** **𝒢₂ only**, and **error on non-vector input** (a grade guard — a 90°-in-e₁e₂ turn is
  only meaningful for a grade-1 vector; reject a scalar/bivector/etc. with a clear `ValueError`).
- **Docstring must teach:** state plainly that it *is* `v * e_12` — "a quarter turn in the e₁e₂
  plane is multiplication by the unit pseudoscalar" — so the named function is a labelled doorway to
  the GA identity, not a black box (the same way `cross`'s docstring says "the dual of the wedge
  `(a∧b)I₃⁻¹`").

## Implementation sketch (gacalc is code-generated)

- In `tools/gen_specialized.py`, emit `rotate_90_degrees` for the **2-D algebra only** (guard on the
  algebra's dimension, exactly as `cross` is emitted for 3-D). The closed form is trivial and needs
  no product: `Vector(-self.coeff_e_2, self.coeff_e_1)` — exact. If the `InvertibleFunction`
  form is wanted, add a 𝒢₂-scoped factory whose inverse negates (right-multiply by `−e_12`).
- `make generate`; add tests (`rotate_90_degrees(1*e_1) == 1*e_2`; equals `v * e_12` in value; exact
  on integer coords; 4× round-trip to identity; non-vector input raises). Update **CHANGELOG**
  (additive → MINOR bump), **CLAUDE.md** (Operators / Rotations), **README**, and doc-region markers
  if a book will `literalinclude` it.

## Open questions

1. **Does the library want this at all?** It is a named convenience over the raw `v * e_12` (which
   already rotates 90° and is arguably the more didactic form). Add it only if a discoverable,
   composable, self-documenting named function is judged worth carrying — otherwise the raw
   pseudoscalar product stands on its own.
2. **Form** — `InvertibleFunction`, a `Vector` method, or both?
3. **Name / direction-in-name** — `rotate_90_degrees` vs `rotate_90_degrees_ccw`?
4. **Confirm 𝒢₂-only** (the removed general-dimension footgun; `plane_rotation(a, b)(π/2)` remains
   the sanctioned general-case form).
