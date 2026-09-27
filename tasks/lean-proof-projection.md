# Lean proof — projection correctness (2D and 3D; onto vectors and onto planes)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**Depends on:** `tasks/lean-proof-rotation-from-scratch.md` (the 2D geometric product + the G2 sandwich),
`tasks/lean-proof-dot-product.md`, `tasks/lean-proof-wedge-product.md`, **and a from-scratch `G3` in
Lean (to build — see Prerequisite below; shared with the 3D dot/wedge/pseudoscalar step-tasks)**.
**Feeds:** the **3D versor sandwich** in `tasks/lean-proof-rotation-from-scratch.md` — the projection
decomposition proved here is what makes the 3D sandwich a corollary of the (already proved) G2 sandwich.

**Status:** proposed — **planned as the next 3D work (decided with the maintainer 2026-09-29)**;
sequenced BEFORE the 3D versor sandwich. Gated on building `G3`.
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

- [ ] **Build `G3`** (the shared prerequisite above): struct + product + basis elements + table +
      dot/wedge/dual/inverse + `project`/`reject`; `make lean` green.
- [ ] **Vector-onto-vector projection:** `proj a b := ((b·a)/(a·a)) • a` (a·a ≠ 0). Prove `proj a b ∥ a`
      and `(b − proj a b) · a = 0` (rejection ⊥ a).
- [ ] **Wedge via rejection:** `a ∧ b = a ∧ (b − proj a b)`.
- [ ] **Dual/normal orthogonality:** `n := (a∧b) · I₃⁻¹` (= `cross a b`); prove `n·a = 0` and `n·b = 0`.
- [ ] **Projection onto the plane:** for `c`, `c_⊥ := proj n c`, `c_in := c − c_⊥`; prove `c_in ⊥ n`
      (lies in the plane) **and `c_in = (c · (a∧b))(a∧b)⁻¹`** — the geometric construction equals the
      general Hestenes/`project` formula. (The prize: verifies gacalc's `project`/`reject`.)
- [ ] **2D cases** (onto-vector, onto the pseudoscalar plane) — deducible from the rotation-derived
      product; the simpler warm-up.
- [ ] `make lean` green; update `proofs/README.md`.

## Open questions

1. `B⁻¹` (blade inverse) in `G3`: for a simple blade `B`, `B⁻¹ = B̃ / (B B̃)`; confirm the scalar-norm
   form is enough for the vector/bivector cases we need (it is in 𝒢₃; no non-simple bivectors until 𝒢₄).
