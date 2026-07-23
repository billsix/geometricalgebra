# galgebra vs gacalc — feature gap analysis (research, for prioritization)

**Reference document** — a standing map of what the mature `galgebra` library does that
gacalc does not, kept for prioritizing gacalc's roadmap. Not a task: nothing here is "to
do." **Update it in place** as either library moves or as items get promoted into real
`tasks/`. Last researched 2026-07-20 against galgebra 0.6.0. Method: read all ~8,850 lines of
galgebra 0.6.0 source, cross-checked against the wider GA field, and diffed against gacalc's
real current surface (read from source, not memory).

---

## TL;DR — the prioritized picture (read this, skip the rest unless triaging)

**One decision dominates everything: do you want gacalc to support non-Euclidean/degenerate
metric signatures?** gacalc hardcodes `eᵢ²=+1` (in the geometric-product canonicalization
`decrease_grade`, which annihilates repeats to +1). That single assumption locks out the
*entire applied-GA world* — spacetime algebra (needs −1), conformal GA (needs mixed
signature/null vectors), projective GA (needs a `0` square), meet/join, motors, rigid-body
motion. It's already your Open Issue #1, and this research confirms it is *the* root gap.

**But most of the value is NOT gated on that decision.** Ranked by value-for-effort, taking
gacalc's pedagogical mission and its sympy strength into account (this ranking is my
synthesis, not from any doc):

| # | Gap | Size | Needs signatures first? | Why it's worth it |
|---|---|---|---|---|
| 1 | **exp / log of rotors & multivectors** | small, self-contained | no | "rotor = exp(bivector)" is a core teaching moment; enables interpolation. Best near-term win. (Finding 2B) |
| 2 | **~~Left/right contractions~~ (DONE 2026-07-22) + commutator/anticommutator + grade-involution + Clifford conjugation** | small, several one-liners | no | Table-stakes operations every GA text uses; gacalc collapses all inner products into one. Cheap. (Finding 2A) |
| 3 | **Reciprocal frames** | small–medium | no | Independently useful *and* the prerequisite for geometric calculus. Build regardless. (Finding 1, 5) |
| 4 | **Outermorphisms / general linear transforms** (`Lt`: det/adjoint/trace as pseudoscalar/blade operations) | medium, self-contained | **no** — works on Euclidean G3 | Beautiful teaching topic ("det = how a map scales the pseudoscalar"); generalizes gacalc's versor-only transforms. The best "big" step that *doesn't* need signatures. (Finding 3b) |
| 5 | **General-multivector inverse** (Hitzer closed-form n<6 / Shirokov) | small–medium | no | Correctness/coverage: gacalc's `inverse()` only handles blade/versor cases; a general multivector can silently fail. (Finding 2B) |
| 6 | **Symbolic ergonomics**: `Mv.subs`, `trigsimp`, public `func`, `Fmt(1|2|3)` display | small | no | On-brand for a symbolic pedagogical lib; `Fmt` (per-grade/per-blade LaTeX layout) is the single most transferable presentation idea. (Findings 2C, 4) |
| 7 | **Arbitrary metric signature (p,q,r)** | **large, architectural** | — (this IS it) | The root gap. Turns "Clifford arithmetic in ℝⁿ" into "a GA library." Decide scope: a signature *flag* (diagonal ±1, unlocks STA — moderate) vs a full *metric tensor* (unlocks CGA/curvilinear/manifolds — large). (Findings 1, 5) |
| 8 | **Geometric calculus (∇, directional/multivector derivatives, fundamental theorem)** | large, new layer | reciprocal frames + coords (not strictly signatures) | The *namesake* gap — the book is "…to Geometric **Calculus**" and gacalc stops at the algebra. Uniquely tractable here thanks to the sympy backend. (Finding 3a) |
| 9 | **meet/join/incidence + non-pseudoscalar-division duality** | large | **yes — gated on #7** | Very visible for "doing geometry," but the useful version can't exist without a projective/conformal model. Do after signatures. (Finding 5) |

**My single recommendation if you want one thing to do next:** #1 (`exp`/`log`) — smallest,
most pedagogical, unblocks nothing-else-required. **If you want the biggest self-contained
leap that stays Euclidean:** #4 (outermorphisms). **If you're ready for the architectural
project:** #7 (signatures), scoped first as a diagonal ±1 flag to reach STA before attempting
a full metric tensor.

**gacalc strengths this research says to protect** (don't regress chasing features):
symbolic+numeric unification (kingdon's *headline* selling point — gacalc already has it),
the code-generated fast paths, the from→to rotation API, and equation-cited fidelity.

---

## What this is

Bill is reading ~5 books on geometric algebra and has limited time; this note front-loads
the "what does a mature GA library actually contain" research. We read the **full source of
`galgebra` 0.6.0** (the well-known symbolic GA library for SymPy — `pygae/galgebra`, orig.
Alan Bromborsky) and cross-referenced it against gacalc's current capabilities and against
the wider GA literature, then wrote up the differences organized for triage.

## Scope & assumptions

1. **"galgebra" = `pygae/galgebra` 0.6.0** — the symbolic-GA-for-SymPy package on PyPI /
   GitHub. Pulled its sdist and read every module. (There is no other well-known Python
   library by that name.)
2. **This is a prioritization reference** (lives in `tasks/reference/`), not an
   implementation plan and not any code change. Nothing here is "do it"; it is "here is the
   map." Concrete follow-up work gets spun out into real `tasks/` docs later per
   `/findings-to-tasks`, and this note is updated in place as that happens.
3. **Scope of "different" = capability & design gaps that matter for a GA library**, focused
   on *what galgebra can do that gacalc can't* (since galgebra is far more mature). Where
   gacalc is deliberately different-by-design (pedagogical, provably-correct reference +
   generated fast paths, Euclidean-only on purpose), that is noted rather than treated as a
   deficiency.
4. **Not evaluating galgebra's code quality** — Bill wants the *functionality* map. Design
   contrasts are noted only where they bear on what gacalc would have to change to close a
   gap.
5. **gacalc's own stated non-goals still hold** (fixed Euclidean signature is a documented
   limit, paravectors deferred until Bill studies APS). Gaps that collide with those are
   flagged as "collides with a current gacalc decision" so Bill can decide consciously.

## galgebra module map (0.6.0, ~8,850 LOC)

| module | LOC | what it is |
|---|---|---|
| `ga.py` | 2349 | the `Ga` algebra factory: basis, metric, products, reciprocal frames, grades |
| `mv.py` | 2295 | `Mv` multivector + `Dop`-adjacent ops; the operation surface |
| `printer.py` | 1246 | LaTeX / text / console printing machinery |
| `lt.py` | 1023 | linear transformations & **outermorphisms**, `Mlt` multilinear functions |
| `metric.py` | 843 | metric tensor, signatures, normalization, **reciprocal basis** |
| `dop.py` | 387 | differential operators (**geometric calculus** ∇) |
| `gprinter.py` | 300 | "graphical" LaTeX printer (standalone pdf) |
| `atoms.py` | 169 | the symbolic atoms (basis blades as SymPy objects) |
| `primer.py` | 60 | convenience constructors |
| `deprecated.py` | 97 | back-compat shims |

---

## Finding 1 — Metrics, signatures & frames (the biggest structural gap)

**galgebra treats "the algebra" as `Ga(basis_string, g=metric, coords=...)` — an object
parameterized by an arbitrary metric.** gacalc has no such object: an algebra is just a
dimension `n` with a hardcoded Euclidean orthonormal basis (`eᵢ·eᵢ=+1`, `eᵢ·eⱼ=0`).
Everything below flows from that one difference.

**Ways galgebra lets you specify the metric/signature** (gacalc supports only the first row):
| galgebra input | example | gacalc |
|---|---|---|
| Euclidean signature hint | `sig='e'`, or `g=[1,1,1]` | **has** (the only case) |
| Minkowski / mixed signature | `g=[1,-1,-1,-1]`, `sig='m+'`, `sig=p` (→ (p,n−p)) | **lacks** — blocks STA |
| full symmetric metric matrix | `g=sympy.Matrix([[...]])` | **lacks** — blocks CGA |
| symbolic constant metric | `g="a b,b c"` | **lacks** |
| position-dependent Riemannian metric | `g='g'` → `g_ij(x,y,z)` | **lacks** |
| coordinate/embedding-derived metric | `g=None, X=field, coords=...` | **lacks** |
| degenerate metric (a `0` on the diagonal) | `g=[0,1,1,1]` | **lacks** — blocks PGA |
| curvilinear presets | `Ga.preset('sph3d'/'cyl3d'/'para3d')` | **lacks** |

Consequences galgebra gets "for free" from the general metric, all **absent in gacalc**:
- **Non-orthonormal / curvilinear bases.** galgebra keeps a dual *base* vs *blade*
  representation and a general product `eᵢeⱼ = 2(eᵢ·eⱼ) − eⱼeᵢ` (`reduce_basis`) — the
  direct generalization of gacalc's bubble-sort, which hardcodes `eᵢ·eⱼ=δᵢⱼ`.
- **Reciprocal frames.** `Ga.mvr()` (reciprocal of the algebra's basis) and
  `ReciprocalFrame(vectors)` (reciprocal of *arbitrary* vectors). Trivial/degenerate in an
  orthonormal Euclidean algebra, so gacalc exposes nothing — but it's the machinery the
  vector-derivative operator is built on. **gacalc lacks.**
- **Coordinates, manifolds, submanifolds.** `class Sm(Ga)` builds a submanifold algebra
  (e.g. the unit sphere) with an induced metric; Christoffel symbols, connections, basis-
  vector derivatives all hang off `coords`. This is the substrate for geometric calculus.
  **gacalc lacks entirely** (it has no calculus layer at all — see Finding 3).
- **Named applied algebras are just metric choices:**
  - **STA** = `Ga('e', g=[1,-1,-1,-1], coords=...)` — literally galgebra's README example.
  - **CGA** = a non-orthogonal/indefinite metric with null directions (arbitrary-`Matrix`
    path handles it).
  - **PGA** = a degenerate metric (`g=[0,1,1,1]`); galgebra even flags a null pseudoscalar
    (`sing_flg`) instead of erroring.
  gacalc's hardcoded `+1` blocks **all three** — this is gacalc's own Open Issue #1, and
  it is the single change that would unlock the most.
- **Dual with metric + convention:** `Ga.dual_mode()` offers 8 sign conventions and
  computes `I² = (−1)^{n(n−1)/2}·det(g)`. gacalc has a fixed Euclidean `dual()` only.

**Collides with a current gacalc decision:** fixed Euclidean signature is documented as an
intentional limit. Everything in this finding is downstream of lifting it. Prioritization
question for Bill is really "do I want non-Euclidean signatures at all, and if so, is it a
signature *flag* (cheap: STA-like diagonal ±1) or a full metric tensor (expensive:
CGA/curvilinear/manifolds)?" — those are very different sizes of project.

## Finding 2 — Multivector operation surface (many small, self-contained additions)

Unlike Finding 1 (one big structural change), most of these are **independent, small, and
Euclidean-safe** — each could be added to gacalc on its own without touching the signature.
This is the "cheap wins" bucket. galgebra's `Mv` delegates product *definitions* to its
`Ga` (metric-aware), but the operation *names* below are what a user sees.

**Present in galgebra, absent in gacalc — grouped by how cheap/relevant they are:**

**A. Cheap & Euclidean-safe (no signature dependency, high pedagogical value):**
- ~~**Left / right contraction** (`A < B`, `A > B`) as distinct named ops~~ — **DONE 2026-07-22.**
  `left_contraction`/`right_contraction` + the `<` / `>` operators (base + generated fast paths with
  precise overloads), per Taylor 2021 p.103; see `tasks/reference/contraction-and-dot-definitions.md`.
  The **Hestenes inner (`|`) vs contraction** distinction is now real: `inner_product` stays the
  Hestenes dot (grade-0-excluded), the contractions include grade 0 (the grade-0 wrinkle was
  settled 2026-07-22 — Hestenes for `inner_product`, no second dot:
  `tasks/archive/2026/07/22/investigate-dot-product-grade-0.md`).
- **Commutator** `½(AB−BA)` and **anticommutator** `½(AB+BA)` — one-liners; the commutator
  is how bivectors generate rotations, so it's genuinely pedagogical.
- **Grade involution / main involution** (`g_invol`, negate odd grades) and **Clifford
  conjugation** (`ccon` = reverse ∘ grade-involution). gacalc has `reverse` but not these
  two of the three standard involutions.
- **`cross(v1,v2)`** — 3-D vector cross product as `−I(v1∧v2)` (nice teaching bridge from
  vector calculus).
- **`undual()`** (explicit inverse of `dual`) and **configurable dual sign/side** (galgebra
  offers 8 dual-mode conventions; gacalc's `dual` is one fixed convention).
- Operator sugar: **`~A`** for reverse, **`A/B`** division, **`A**n`** integer power.
- Predicates: **`is_versor`**, **`is_blade`**, **`is_base`**, **`compare(A,B)`** (is B a
  scalar multiple of A).

**B. Medium, high-value, some are real algorithms:**
- **Multivector `exp()`** (only when `A²` is scalar: trig if `A²<0`, hyperbolic if `A²>0`).
  This is galgebra's *primary rotor/versor constructor* — `(B/2).exp()` for a bivector `B`
  gives a rotor. gacalc builds rotors only from from/to vectors or plane+angle and has **no
  `exp` at all**. Adding `exp` would let gacalc express rotors the exp-map way the books do.
- **General-multivector inverses**: `shirokov_inverse` (works for *any* multivector,
  iterative — arXiv 2005.04015) and `hitzer_inverse` (closed form for n<6). gacalc's
  `inverse()` only handles blade/versor-like cases; a general multivector can fail. This is
  a correctness/coverage gap, not just a convenience.
- **Signature-aware norm family** — `qform` (⟨Ã A⟩), `norm2`, and `mag`/`mag2` that differ
  from `norm`/`norm2` only when the metric is non-Euclidean, plus `hint` sign control.
  *No analog needed while gacalc is Euclidean*, but the concepts appear the moment signature
  work starts (ties to Finding 1).

**C. Symbolic-ergonomics helpers (gacalc is sympy-based, so these are natural):**
- **`Mv.subs(...)`** — symbolic substitution per coefficient (gacalc has none; you'd rebuild
  by hand). Genuinely missing given gacalc's symbolic focus.
- **`trigsimp()`** and **`func(fct)`** (apply an arbitrary fn to each coefficient — gacalc
  has a *private* `_map_coefficients` but exposes no public `func`). gacalc already has
  `simplified()`/`expanded()`.
- **`Fmt(1|2|3)`** display modes (one multivector / one grade / one blade per line).

**Differentiation preview (full treatment in Finding 3):** galgebra's `Mv` can be
differentiated at the value level — **`A.diff(coord)`**, **`pdiff`**, and even a sympy
`diff` hook so `sympy.diff(mv, x)` works. gacalc has **no multivector differentiation**.

**Neither library has:** multivector **logarithm**, or general **trig/sqrt of a
multivector** (galgebra uses trig only *inside* `exp`).

**Things gacalc has that galgebra lacks a named analog for** (don't lose these — they're
gacalc's pedagogical identity): `outer_product_of_vectors`, and the from→to rotation
factories `rotor_from_vectors`/`plane_rotation`/`projection_rotation` (galgebra only builds
rotors via bivector `exp` or products of vectors), plus the composable-function/transform
layer.

## Finding 3 — The two biggest gaps: geometric calculus, and linear transforms/outermorphisms

Both are **new architectural layers, not functions** — each needs a coordinate+metric-
bearing algebra object that gacalc structurally does not have (gacalc multivectors are
constant dict-of-blades, no coordinates, no `Ga`-like context). These are the largest
capability jumps available, and both are gated on the same prerequisite as Finding 1.

### 3a. Geometric calculus (`dop.py` + `mv.Dop` + `ga.grad`) — *gacalc's namesake, entirely absent*

gacalc is styled after Hestenes & Sobczyk **"Clifford Algebra to Geometric _Calculus_"**
and cites its equations — but implements only the *algebra* half. It has **zero**
differentiation: no coordinates, no ∂, no ∇, no multivector fields.

galgebra's stack (three layers): `Pdop` (a partial derivative) → `Sdop` (scalar sum of
`coefᵢ·Pdopᵢ`) → `mv.Dop` (attaches a *multivector* coefficient to each `Pdop`, so it acts
by any GA product). **∇ = `ga.grad` = Σ eⁱ ∂ᵢ**, built from the **reciprocal frame** (Finding
1!) over the coordinates. The headline GA-calculus result — one operator whose *geometric
product* yields divergence and curl at once — is spelled by choice of product:
- gradient of scalar φ: `ga.grad * phi`
- **geometric derivative** ∇F (div + curl in one object): `ga.grad * F`
- divergence: `ga.grad | F`   · curl: `ga.grad ^ F`   · Laplacian: `ga.grad * ga.grad`
- directional derivative a·∇: `(a | ga.grad) * F`; derivative w.r.t. a multivector variable:
  `ga.make_grad(a)`
- left- vs right-acting operators (`ga.grad` / `ga.rgrad`, the `cmpflg`) — a genuinely
  GA-specific concern (∇ on the left vs right of a product differs) with no scalar-calculus
  counterpart.
Fields are multivectors whose coefficients are **sympy functions of the coords**, so
differentiation is exact/symbolic (`ga.mv('v','vector', f=True)` → `v__x(x,y,z)`). This is
the "collapse Maxwell to ∇F = J" machinery. **gacalc analog: none of it.**

### 3b. Linear transformations & outermorphisms (`lt.py`) — *no gacalc abstraction exists*

`Lt` is a linear operator on the algebra, stored as `{eᵢ: image multivector}`, constructible
from a **matrix, dict, list, Python function (linearity-checked), symbolic letter, or a
versor**. The key idea gacalc has no analog for is the **outermorphism**: a map defined only
on vectors is extended to *all* blades/multivectors by
`L(a∧b∧…) = L(a)∧L(b)∧…` (cached `mv_dict`, applied by one `xreplace`). That single idea is
what makes these **coordinate-free and blade-aware**:
- **`Lt.det()`** = `L(E)·E⁻¹` — the determinant as "how L scales the pseudoscalar" (needs the
  outermorphism to even state).
- **`Lt.adj()`** — adjoint L̄ via `a·L(b)=b·L̄(a)` (metric-correct `g⁻¹·Mᵀ·g`).
- **`Lt.tr()`** = `∇_a·L(a)` — trace, *defined using the calculus layer* (ties 3a and 3b).
- **`Lt.inv()`**, **`Lt.is_singular()`**, **`Lt.matrix()`**, and an algebra of Lts
  (`+`,`-`,`*`=composition).
- **Versor-based `Lt`**: from a versor V the map is the grade-involute sandwich
  `x ↦ V̂ x V⁻¹` (covers rotations *and* reflections), immediately compiled to the same
  `lt_dict` outermorphism — one interface unifying rotors/reflections with general matrix
  maps. This is the general superset of gacalc's bespoke `Rotor.sandwich`/`plane_rotation`.
- **`Mlt`** — multilinear functions / **tensors** `F(v₁,…,vᵣ)`, with `.pdiff`/`.contract`/
  `.cderiv` (covariant derivative) built on `ga.grad`. gacalc has no tensor abstraction.

**Contrast with what gacalc has:** a *fixed, closed menu* of transform factories
(`translate`/`uniform_scale`/`scale_non_uniform`/rotations) returning callables, plus
`to_matrix`. No object representing "an arbitrary linear operator," so gacalc cannot express
`det(f)`, the adjoint, eigenblades, or the action of a general linear map on a bivector.

**Sequencing note for Bill:** 3b (outermorphism/`Lt`) is buildable on a *Euclidean* algebra
and does **not** strictly require lifting the signature — an outermorphism over `G3` with
det/adjoint/trace is a self-contained, high-value addition and arguably the best "big" next
step. 3a (∇) genuinely needs coordinates + reciprocal frame first, so it's downstream of
Finding 1's machinery even if you stay Euclidean.

## Finding 4 — Presentation, packaging & maturity (mostly not algebra — read for what's worth copying)

gacalc is a *cleaner, younger, better-typed* engineering surface (Python 3.13, ruff+ty
clean, ~246 tests, numpy+sympy so it's numeric-capable). galgebra is *far broader in
capability but carries maturity debt* (Beta status, Python-version metadata that disagrees
with itself, a `utils.py` still importing `collections.Iterable` so its `flatten` is
**broken** on modern Python, Py2 remnants, and it **monkeypatches builtin `print` and
`sympy.Basic.__repr__` globally on import**). So this finding is *not* "gacalc is behind" —
it's "here are the few presentation ideas worth stealing, and the ecosystem signals a mature
library has."

**Worth copying (ranked by value-for-effort):**
1. **User-controlled multivector display layout** — galgebra's `Mv.Fmt(1|2|3)`: whole
   multivector on one line / **one grade per line** / **one blade per line**, with an
   optional LaTeX `title = <mv>`. This is the single most transferable presentation idea;
   gacalc's `_repr_latex_` emits one fixed form. Cheap, high pedagogical payoff (a graded
   multivector reads far better one-grade-per-line).
2. **Configurable LaTeX notation** — `Format()`/`GaLatexPrinter` toggles: suppress function
   args, condense ∂-fractions, inv-trig style, custom macro preamble. gacalc has no display
   settings at all. Medium effort; matters more once fields/derivatives exist (Finding 3).
3. **A text/console printer** (optionally ANSI-colored) as a non-Jupyter display path.
   gacalc has no console-display story beyond `repr`. Low priority unless you use the REPL a
   lot.
4. **Worked-example corpus that doubles as tests** — galgebra's `examples/{ipython,primer,
   Macdonald}` are notebook-validated (nbval) in CI. gacalc has notebooks (`displaymv.py`
   etc.) but they aren't gap-analysis-driven pedagogical walk-throughs. Cheap, and on-brand
   for a pedagogical library.

**Ecosystem/maturity signals gacalc lacks (mostly out of scope for a solo pedagogical lib,
listed for awareness, not as targets):** hosted versioned docs (Read the Docs) with
tutorials + API autosummary + changelog; formal citability (Zenodo DOI + `CITATION.md`);
interop bridge to the other major Python GA lib (`clifford`, via `interop.Cl`) and a Julia
binding; a documented `used_by` downstream list.

**Explicitly do NOT copy** (they run counter to gacalc's house style): galgebra's
`primer.py` `import *` convenience shim, and its `utils.py`/`deprecated.py` back-compat
cruft. These are maturity *debt*, not features.

**One heavyweight galgebra feature to note but probably skip:** a standalone
script→`.tex`→`pdflatex`→PDF(+crop/PNG) pipeline (`gprinter.gxpdf`) with per-OS viewer
launch and fixture-diffed PDF regression tests — used for Macdonald's textbook materials.
gacalc's PDFs come from the external Sphinx book (mvp) in a different repo, which is the
better separation of concerns; don't pull document generation into the library.

## Finding 5 — The wider GA landscape (is this gap real, or just galgebra's taste?)

Cross-checked against the field (clifford, kingdon, ganja.js, gafro, versor, Gaalop; the
STA/CGA/PGA literature; Hestenes & Sobczyk) so we're not just chasing one library's choices.
The verdict: **galgebra's big gaps are the field's gaps too** — they're what separates a
*geometry/physics* GA library from a *Clifford-arithmetic* one.

**The one root fact:** almost every applied GA beyond textbook G2/G3 lives in a **non-
Euclidean or degenerate metric**, so `eᵢ²=+1` hardcoded locks gacalc out of the entire
applied world:
- **STA** (relativity, Maxwell as `∇F=J`, Dirac) = Cl(1,3), needs **negative** squares.
- **CGA** (points/lines/planes/circles/spheres as blades; rotations+translations+dilations
  as versors) = Gₙ₊₁,₁, needs a **mixed** signature → genuine **null** vectors.
- **PGA** (rigid-body motion / motors / robotics — the currently-fashionable one) =
  degenerate metric with **e₀²=0**, and needs a **non-metric dual** because the pseudoscalar
  isn't invertible — which is exactly the operation gacalc's `dual()` (divide by
  pseudoscalar) cannot generalize to.
- **Euclidean GA's structural ceiling:** translations are *not* versor operations, so
  rigid-body motion is impossible — which is *why* PGA/CGA exist. Worth stating plainly in
  gacalc's docs as the honest boundary of what it teaches.

**Table-stakes vs advanced, for a general-purpose GA library** (● = gacalc has, ◐ partial,
○ lacks):
| capability | tier | gacalc |
|---|---|---|
| geometric/outer/inner products, reverse, dual, grades | table stakes | ● |
| symbolic **and** numeric in one library | differentiator | ● (real strength — kingdon's headline feature) |
| code-generated fast paths | scaling | ● (pedagogical miniature of versor/gafro/Gaalop) |
| arbitrary signature (p,q,r) incl. degenerate | **table stakes** | ○ |
| left/right contractions as distinct operators | table stakes | ● (done 2026-07-22, `< `/`>`) |
| exp/log of rotors & multivectors | table stakes (for motion) | ○ |
| outermorphisms / general linear transforms | table stakes (for a "linear algebra" GA lib) | ○ |
| reciprocal frames | table stakes | ○ |
| meet/join/incidence | table stakes (for geometry) | ○ |
| versor/blade factorization | advanced | ○ |
| geometric calculus (∇, fundamental theorem) | advanced (galgebra's differentiator) | ○ |
| visualization | table stakes (graphics/edu) | ◐ (matplotlib helpers) |

**gacalc's genuine strengths to protect** (don't regress these chasing features): the
symbolic+numeric unification, the generated fast paths, and equation-cited pedagogical
fidelity. The gaps are what make it *arithmetic in ℝⁿ* rather than *a geometry library* — and
a GA expert would name **arbitrary signature** and **geometric calculus** first.

---

## Appendix — how to reproduce / extend this research

- galgebra 0.6.0 source was pulled from its PyPI sdist and read in full. To re-fetch:
  `pip download galgebra==0.6.0 --no-binary :all:` (or the sdist URL from
  `pypi.org/pypi/galgebra/0.6.0/json`).
- Module map and the per-file findings above cite exact galgebra symbol names / line
  numbers (as of 0.6.0), so each claim is checkable against the source.
- Web sources for the landscape context are listed inline in Finding 5's reasoning; key ones:
  the PGA hub (projectivegeometricalgebra.org), Lengyel's dual-PGA blog, Dorst *GA for
  Computer Science*, Hestenes & Sobczyk *Clifford Algebra to Geometric Calculus*, the
  kingdon paper (arXiv:2503.10451), and the clifford/galgebra docs.
- **Next step if Bill wants to act on any row of the TL;DR table:** run `/findings-to-tasks`
  to spin the chosen row(s) into their own `tasks/` docs (each `proposed — needs go-ahead`).
  This doc stays as the reference map.
