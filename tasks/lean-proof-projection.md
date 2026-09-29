# Lean proof — projection correctness (2D and 3D; onto vectors and onto planes)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**Depends on:** `tasks/lean-proof-rotation-from-scratch.md` (the 2D geometric product + the G2 sandwich),
`tasks/lean-proof-dot-product.md`, `tasks/lean-proof-wedge-product.md`, **and a from-scratch `G3` in
Lean (to build — see Prerequisite below; shared with the 3D dot/wedge/pseudoscalar step-tasks)**.
**Feeds:** the **3D versor sandwich** in `tasks/lean-proof-rotation-from-scratch.md` — the projection
decomposition proved here is what makes the 3D sandwich a corollary of the (already proved) G2 sandwich.

**Status:** in-progress (2026-09-29) — `G3` core + the projection-op extension landed, and chain steps
1–3 proved (`reject_perp`, `wedge_reject`, `dual_wedge_perp_left`/`_right`), `make lean` green. Remaining:
the plane-projection `= (c·B)B⁻¹` (needs vector·bivector inner + blade inverse), the 2D cases, then the
3D versor sandwich as the corollary.
**Priority:** 6
**Difficulty:** 7

## BLUF

The author's own Lean proof that **projection works via the general geometric-algebra formula** gacalc
implements — `project(onto=B)(A) = (A · B) B⁻¹` (base.py) — in **2D and 3D**, for **vector-onto-vector**
and **vector-onto-plane (bivector)**. The 3D chain is built geometrically (vector projections + the
dual/normal) and then **proved equal to the general Hestenes formula**, which is the second-oracle check
of gacalc's `project`/`reject`/`projection_rotation`. Landing this also **reduces the 3D versor sandwich
to the 2D one**: the sandwich fixes the perpendicular (rejection) part and rotates the in-plane part,
and the in-plane rotation is exactly the proved G2 `sandwich_versor`. "Done" = the 2D/3D ×
onto-vector/onto-plane cases proved, each with its equivalence-to-`(A·B)B⁻¹` lemma, `make lean` green.

## Context — read first

- Read `tasks/reference/lean-for-gacalc.md`, `tasks/reference/dot-wedge-projection-rejection.md` (the
  projection/rejection math gacalc uses), `tasks/reference/unit-bivector-and-rotors.md` §6 (why the
  sandwich is scale-invariant), and the umbrella.
- **gacalc's definitions (the targets to match):** `project(onto=B)(A) = (A · B) B⁻¹` (base.py:1279);
  `reject = A − project`; `projection_rotation(from,to)` (transforms.py) rotates the *in-plane* part
  (`project` onto `from ∧ to`) and leaves the *rejection* (perpendicular part) fixed; gacalc **asserts
  by test** that the versor sandwich `R v R⁻¹` (`versor_rotation`) **equals** `projection_rotation`.
  `cross(a,b) = (a∧b) I₃⁻¹` (vectorcalc.py) is the dual of the wedge = the plane's normal.

## Design (decided with the maintainer, 2026-09-29)

Build the 3D projection geometrically from vector projections + the dual, then prove it equals the
general `(A·B)B⁻¹`. Two facts to keep straight (the maintainer confirmed the rejection reading):

- **The wedge sees only the rejection.** `proj_a b = (b·a) a⁻¹` is *parallel* to `a`, so
  `a ∧ (proj_a b) = 0`. The perpendicular part is the **rejection** `r = b − proj_a b`, and
  `a ∧ b = a ∧ r`. `{a, r}` is an *orthogonal* frame of the plane (Gram–Schmidt = gacalc's
  `make_orthogonal_frame`, frame.py).
- **The sandwich payoff.** Decompose `v = v_in + v_⊥` (in-plane + along the normal). The versor
  sandwich fixes `v_⊥` and rotates `v_in` within the plane — and that in-plane rotation *is* the G2
  `sandwich_versor` already proved. So 3D sandwich = (2D result) + (this projection decomposition).
- **The plane is `a (b − proj_a b)` (maintainer, 2026-09-29).** Since `r = b − proj_a b ⊥ a`
  (`reject_perp`), the geometric product has no scalar part, so `a (b − proj_a b) = a ∧ r = a ∧ b`
  (`wedge_reject`) — the plane bivector, built on the orthogonal frame `{a, r}`. Normalizing `{â, r̂}`
  reproduces G2's `{e₁, e₂, e₁₂}` table (`â²=r̂²=1`, `âr̂=−r̂â`, `(âr̂)²=−1`), which is the concrete
  mechanism of the reduce-to-2D finish. The one new unlocking lemma: **`a r = a ∧ r` for `a ⊥ r`**.
  The angle-free versor itself and the identity `R a = |a|·h` are already landed in `Rotation3D.lean`
  (see `tasks/lean-proof-rotation-from-scratch.md`).

## Prerequisite: a from-scratch `G3` in Lean (shared)

We have only `G2` (4-dim) in `proofs/GacalcProofs/G2.lean`. This needs **`G3`** — the 8-dim algebra
`{1, e₁,e₂,e₃, e₁₂,e₁₃,e₂₃, e₁₂₃}` as a coordinate struct (8 real coefficient fields), the same
build style as `G2`: the geometric product `mul`, `add`/`sub`/`smul`/`neg`/`reverse`, the basis
*elements* (`one`/`e_1`/`e_2`/`e_3`/`e_12`/…/`e_123`), the multiplication table, plus `inner_product`
(dot), the wedge `∧`, the pseudoscalar `I₃ = e_123` with `I₃² = −1` and `I₃⁻¹`, and `project`/`reject`.
**Build it once — it also unblocks `lean-proof-dot-product.md`, `-wedge-product.md`, and
`-pseudoscalar-square-sign.md` (all need 3D).** Follow the standalone policy (coordinate struct; basis
blades as genuine `G3` elements, per the rotor→versor representation lesson).

## Plan

- [x] **Build `G3` core** (the shared prerequisite): `proofs/GacalcProofs/G3.lean` — struct, geometric
      product + wedge + reverse (transcribed from gacalc's `Gn` via
      `tasks/adhoc/build-g3-lean/derive_g3_product.py`), the 8 basis elements, `vec`, `I₃`, the
      multiplication table, `I₃² = −1`. `make lean` green (2026-09-29).
- [x] **Extend `G3`** (2026-09-29, in `G3.lean`): `dot` (= ⟨AB⟩₀; the Euclidean dot for vectors) with
      `dot_sub_left`/`dot_smul_left` bilinearity, wedge bilinearity (`wedge_sub_right`/`wedge_smul_right`),
      `wedge_self_vec`, `zero`, `I₃⁻¹` (`I_inv`, with `I_mul_I_inv`), and `dual := A·I₃⁻¹`. Still to add:
      the full `project`/`reject` (`(A·B)B⁻¹`, incl. vector·bivector inner) for the plane-projection step.
- [x] **Vector-onto-vector projection** (2026-09-29, in `Projection.lean`): `proj a b := (b·a/a·a) • a`,
      and **`reject_perp`** — `(b − proj_a b) · a = 0` for `a·a ≠ 0`.
- [x] **Wedge via rejection** (`wedge_reject`): for a vector `a`, `a ∧ (b − proj_a b) = a ∧ b`.
- [x] **Dual/normal orthogonality** (`dual_wedge_perp_left`/`_right`): `dual(a∧b) · a = 0` and `· b = 0`
      for vectors — the plane normal is ⊥ the plane.
- [ ] **Projection onto the plane:** for `c`, `c_⊥ := proj n c`, `c_in := c − c_⊥`; prove `c_in ⊥ n`
      (lies in the plane) **and `c_in = (c · (a∧b))(a∧b)⁻¹`** — the geometric construction equals the
      general Hestenes/`project` formula. (The prize: verifies gacalc's `project`/`reject`.) Needs the
      vector·bivector inner + blade inverse (open question 1).
- [ ] **2D cases** (onto-vector, onto the pseudoscalar plane) — deducible from the rotation-derived
      product; the simpler warm-up.
- [ ] Then the **3D versor sandwich** (in `lean-proof-rotation-from-scratch.md`) as the corollary.
- [x] `make lean` green (for what's landed); `proofs/README.md` updated.

## Open questions

1. `B⁻¹` (blade inverse) in `G3`: for a simple blade `B`, `B⁻¹ = B̃ / (B B̃)`; confirm the scalar-norm
   form is enough for the vector/bivector cases we need (it is in 𝒢₃; no non-simple bivectors until 𝒢₄).
