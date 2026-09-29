# Lean proof — projection correctness (2D and 3D; onto vectors and onto planes)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**Depends on:** `tasks/lean-proof-rotation-from-scratch.md` (the 2D geometric product + the G2 sandwich),
`tasks/lean-proof-dot-product.md`, `tasks/lean-proof-wedge-product.md`, **and a from-scratch `G3` in
Lean (to build — see Prerequisite below; shared with the 3D dot/wedge/pseudoscalar step-tasks)**.
**Feeds:** the **3D versor sandwich** in `tasks/lean-proof-rotation-from-scratch.md` — the projection
decomposition proved here is what makes the 3D sandwich a corollary of the (already proved) G2 sandwich.

**Status:** nearly complete (2026-09-29), `make lean` green. Landed: `G3` core; the uniform Hestenes
`proj`/`reject` (vector- and bivector-blades) via `(A·B)B⁻¹` / `(A∧B)B⁻¹`; `project_add_reject`
(project + reject = identity); `proj_plane = project_onto` (normal construction = Hestenes form); the
2D cases (`Projection2D.lean`); the graded inner product `⟨AB⟩₁`; and the general magnitude. Only the
optional G2 `dot`-bilinearity cleanup remains (below). **Refocused 2026-09-29 (maintainer steer):**
match gacalc's *uniform Hestenes* `project`/`reject` — see "Hestenes project/reject" below. The 3D versor
sandwich this task once "fed" **landed independently** (even-versor/quaternion route in `Sandwich.lean`).
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

## Hestenes project/reject — the uniform form (maintainer steer, 2026-09-29)

gacalc's `project`/`reject` (base.py:1279/1338, Hestenes & Sobczyk p.18 eqs 2.9) are two formulas,
**uniform for `B` a vector OR a bivector**:

- `project(onto=B)(A) = (A · B) · B⁻¹`  — the component of `A` in the subspace `B`.
- `reject(away_from=B)(A) = (A ∧ B) · B⁻¹`  — the component of `A` orthogonal to `B`.

**Status of each piece in Lean (2026-09-29):**

- **`project` onto a vector** — HAVE it: `Projection.proj a b = (b·a/a·a)·a` *is* `(A·B)B⁻¹` for a
  vector `B` (since `a⁻¹ = a/(a·a)`), just written divided-out.
- **Blade inverse `B⁻¹`** — HAVE it (resolves old open Q1): `Sandwich.inverse B = B̃/normSq B` works for a
  **bivector** too — `normSq B = |B|² > 0` and `B · (inverse B) = 1` (a bivector in 𝒢₃ is simple, so
  `B B̃` is a scalar). No new blade-inverse code needed.
- **`reject` onto a vector** — DEFINABLE NOW (wedge + inverse): `(b∧a)·a⁻¹`, and it **equals** the
  current `b − proj_a b` (because `(b∧a)a⁻¹ + (b·a)a⁻¹ = (ba)a⁻¹ = b`). Worth proving as the bridge.
- **`reject` onto a bivector** — DEFINABLE NOW (wedge + inverse): `(A∧B)·B⁻¹`; `A∧B` is a trivector
  (`wedge` handles it) times the bivector `inverse` → a vector.
- **`project` onto a bivector** — THE ONLY GAP: needs Hestenes' **graded inner product** `A·B =
  ⟨AB⟩_{|r−s|}` for the vector·bivector case (`r=1, s=2`), which is the **grade-1** (vector) part of the
  geometric product. Our `dot a b = (mul a b).s` only takes the **grade-0 (scalar)** part — which *is*
  Hestenes' inner product for two vectors, but for a vector·bivector the scalar part is **identically
  zero**, so `dot` returns 0 instead of the intended vector. So the gap is a *graded* version of the
  dot, not any new operation. (Terminology note, maintainer 2026-09-29: this is **Hestenes' inner
  product** — `A·B = ⟨AB⟩_{|r−s|}`, defined for all grades in *Clifford Algebra to Geometric Calculus*,
  1984 — **not** the "left/right contraction," which is a later, slightly different notion from
  Lounesto and Dorst–Fontijne–Mann. For vector·bivector the two coincide, which is why they're easy to
  conflate; the library and the book use Hestenes' inner product.)

**Why this graded inner product is barely relevant (maintainer asked):** it is needed ONLY for
`project` onto a bivector via the literal `(A·B)B⁻¹`. It is NOT needed for any `reject` (those use `∧`),
NOT for `project` onto a vector (scalar dot suffices), and NOT for the rotation proofs — there the
in-plane component is just `c − reject_B(c)` (projection = identity − rejection for a blade), so the
perpendicular/in-plane split needs only `reject`. So Hestenes' graded dot is the lowest-priority piece;
add it only to reproduce Python's `project`-onto-a-plane formula exactly (and to prove
`proj_plane = (c·B)B⁻¹`).

**Payoff for the rotation proofs:** "components perpendicular to the plane are unchanged" is exactly
`reject` onto the plane bivector `B = a∧b` (= `(c∧B)B⁻¹`), definable now. So `rotation_fixes_normal`
(which only fixes the one normal direction) generalizes to **`sandwich R (reject_B c) = reject_B c` for
ANY vector `c`** — the whole perpendicular component fixed. And reduce-to-2D becomes the clean,
Python-faithful statement: *the sandwich rotates `project_B(c)` and fixes `reject_B(c)`*.

**Proposed next steps (this task):**
- [x] Define `reject` the Hestenes way `(A∧B)·B⁻¹` (`Projection.reject`, using `wedge` +
      `Sandwich.inverse`); prove the vector case equals `b − proj_a b` (`reject_vec_eq`). DONE 2026-09-29.
- [x] Generalize goal 3: `rotation_fixes_perp` — the rotation fixes any multiple of the plane normal
      `b×a` (= the whole orthogonal complement in 3D), superseding the single-direction
      `rotation_fixes_normal`. DONE 2026-09-29 (`RotateComponents.lean`).
- [x] Add Hestenes' **graded inner product** `⟨AB⟩₁` (`inner_vb`, the vector·bivector → grade-1 case)
      and `project` onto a bivector `= (A·B)B⁻¹` (`project_onto`). DONE 2026-09-29 (`Projection.lean`).
      Validated by **`project_add_reject`**: `(A·B)B⁻¹ + (A∧B)B⁻¹ = A` (in-plane part + perpendicular
      part reconstruct the vector), since `(A·B)+(A∧B) = AB` and `B B⁻¹ = 1`.
- [x] **`proj_plane a b c = project_onto (a∧b) c`** (the normal-based construction equals the Hestenes
      form) — DONE 2026-09-29 (`Projection.lean` `proj_plane_eq_project_onto`), assembled from the
      literal-bivector lemmas `reject_eq_proj_normal` (rejection from a plane = projection onto its
      normal) + `project_eq_sub_reject`, instantiated at `a∧b`.
- [x] **2D cases** — DONE 2026-09-29 (`Projection2D.lean`): G2 `wedge`/`proj`/`reject`, `reject_perp`
      (rejection ⊥ the vector), and the onto-the-pseudoscalar-plane case (`vec_wedge_I_eq_zero`,
      `reject_from_I_eq_zero` — a 2D vector has no perpendicular component to the whole plane).
- [x] **Magnitude** (maintainer ask 2026-09-29): the squared magnitude `normSq = ⟨AÃ⟩` (H&S p.13
      eq 1.49) was already defined and is the workhorse of the versor layer; added the general
      `magnitude = √(normSq)` (all grades) with `magnitude_vec` bridging to the vector-only `mag`.

- [x] **G2 `dot` bilinearity** (`dot_sub_left`/`dot_smul_left` in `Versor2D.lean`) — DONE 2026-09-29;
      the G2 `reject_perp` is now structural (coordinate-free) and general in `a, b`, the exact shape of
      the 3D proof.

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

1. ~~`B⁻¹` (blade inverse) in `G3`~~ — **RESOLVED 2026-09-29.** `Sandwich.inverse B = B̃/normSq B` is
   exactly `B̃/(B B̃)` and works for a vector and a (simple) bivector in 𝒢₃ (`B · inverse B = 1`,
   verified). No non-simple bivectors until 𝒢₄. See "Hestenes project/reject" above.
