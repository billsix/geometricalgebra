# Investigate: graded-typed module basis constants (so `from gacalc.g2 import e_1` is a Vector2)

**Status:** DONE (2026-08-04) — Option A implemented (Bill approved). See "What landed" below.
**Priority:** 4
**Difficulty:** 4

## What landed (2026-08-04)

Option A (reverse the "module constants are the full class" decision), Bill-approved:

- **Generator** (`tools/gen_specialized.py` `generate_constants`): each `g1`/`g2`/`g3` module
  constant is now emitted at its **`resolve`d graded type** — `zero`/`one` → `Scalar_n`, a lone
  vector blade → `Vector_n`, `e_12`/`e_13`/`e_23` → `Bivector_n`, `e_123` → `Trivector3` — instead of
  the full class `G_n`. `gn.py` is generated separately and untouched (its constants stay `Gn`). The
  tracked diff is `tools/` only; the regenerated `g*.py` are gitignored.
- **Confirmed at REPL** (after `python tools/gen_specialized.py`): `from gacalc.g2 import e_1, e_2`
  → `Vector2`; `3*e_1+4*e_2` → `Vector2`; `e_1*e_2` → `Rotor2`; `e_1^e_2` → `Bivector2`;
  `g2.one` → `Scalar2`; `g3.e_123` → `Trivector3`. Runtime values byte-identical to the class
  constants (`e_1 == Vector2.e_1`, etc.). Full `G2` still reachable via `G2.e_1` / `G2(...)` / `Gn`.
- **Notebooks migrated:** `displayg2.py` / `displayg3.py` (teach the full class) switched bare
  `e_1…` → `G2.e_1` / `G3.e_1` (and `one`/`zero` → `G_n.from_scalar(1/0)`), keeping every `: G2` /
  `: G3` annotation exact. `displaygraded.py` (the payoff) now `from gacalc.g2 import e_1, e_2` and
  writes the 2D basis **unqualified** (`3*e_1 + 4*e_2`, matching `3e₁ + 4e₂`) while staying a
  `Vector2`; the 𝒢₃ section stays `Vector3.e_*` (the bare `e_1`/`e_2` names are already bound to 𝒢₂
  in that file — a real one-name-per-algebra constraint, noted in the notebook).
- **Docs:** CLAUDE.md "Two ways to name a basis blade" updated (module constants = graded type; full
  class via `G_n.e_1`).
- **One test updated:** `tests/test_conformance.py::test_basis_constants` encoded the *old* contract
  by attribute access (`type(mod.zero) is G2`) — the investigation's import-only scan missed it (it's
  `getattr(mod, …)`, not an import). Flipped to assert each constant's **graded** type; the
  "arithmetic on the constants widens to the full class" sub-check still holds (scalar + vectors has
  no covering graded type). This was the *only* `src`/`tests` code depending on the old behavior.
- **Verification:** `pytest` 347 passed; `ty check src tests tools` clean; the three notebooks
  execute headless. Notebooks are outside the gate (`testpaths = src tests`).
- **Consumer unblocked:** mvp can now `from gacalc.g2 import e_1` and keep `Vector2`
  (`github.com/billsix/modelviewprojection` `tasks/unqualify-graded-basis-imports.md`), gated on the
  next gacalc release.

## Goal

Let teaching/notebook code write basis vectors **unqualified and concise** — `3*e_1 + 4*e_2`,
matching the printed math `3e₁ + 4e₂` — **without losing the graded `Vector2` type** (or the fast
closed-form paths / precise product types). Today that isn't possible; see the finding.

Bill (2026-08-04): "it works as is, but the math printed in the notebooks looks so concise relative
to the python code — it'd be sweet if it matched a little closer, without losing anything."
**He is explicitly open to reversing the earlier decision** that module-level constants are the
module's full class type.

## Current state (verified 2026-08-04)

- `from gacalc.g2 import e_1` → **`G2`** (the full dimension class).
- `Vector2.e_1` → **`Vector2`** (graded; carries the fast sandwich + precise product overloads).
- `gn.py` module `e_1` → **`Gn`** (`MultiVector`, dimension-agnostic).
- **No `Vector2`-typed module-level constant exists.** So concise unqualified code (`3*e_1+4*e_2`)
  today silently yields a `G2`, not a `Vector2`.

## The decision to reconsider

Module-level constants are currently emitted as the **module's headline class** (`G2`/`G3`), not the
grade-1 type. **Q: why was that chosen, and does the rationale still hold?** (Check the generator
`tools/gen_specialized.py`, `tasks/reference/*`, git history, and any test that depends on
`gacalc.g2.e_1` being a `G2`.) The class-constant note + "no local aliases" convention in `CLAUDE.md`
are the surrounding context.

## Questions to answer

1. **Why G2-typed today?** What actually relies on `from gacalc.g2 import e_1` being a full `G2`
   (tests, notebooks, mvp, gacalc internals)? Enumerate.
2. **Option A — reverse it:** make `gacalc.g2`'s module `e_1`/`e_2`/`e_12`/… the **graded** types
   (`Vector2`, `Bivector2`, …). Then `3*e_1+4*e_2` → `Vector2` for free. What breaks?
   - `e_1 * e_2` would become `Rotor2` (graded) instead of `G2` — does any real call site depend on
     the `G2` result type? (Runtime *values* are identical; only static types tighten.)
   - Run the full suite + `ty` across gacalc, and check the notebooks + mvp as consumers.
3. **Option B — additive:** a *new* export that gives graded constants, leaving the `G2` ones
   (e.g. a `gacalc.g2` submodule, `from gacalc.g2.basis import e_1`, or distinct names). Zero
   breakage, but a longer import path. Weigh vs A.
4. **What do the notebooks/tests import now, and what type do they get?** If they already use the
   `G2`-typed module constants for conciseness (sacrificing the grade), then Option A is a strict
   *improvement* to them — confirm.
5. **"Without losing anything" — verify explicitly:** you can still build a general `G2`/`Gn` when
   you need one (via `Gn`, explicit construction, or the full class still exported); no runtime
   value change; graded is *more* precise, not less. Flag anything that would actually be lost.
6. Cover **all grades** (`e_12`, `e_123`, pseudoscalars) and **all algebras** (`gn`/`g1`/`g2`/`g3`),
   and how the **generator** would emit graded module constants.

## Deliverable

Findings (the "why G2" rationale, the breakage assessment for A, the trade-off vs B, what the
notebooks currently do) + a clear recommendation (A / B / status quo) with a migration sketch. Do
NOT change code until Bill signs off. If A is recommended, note the notebook simplifications it
unlocks (the point of the exercise).

## Notes

- Origin: Bill (2026-08-04). Consumer side tracked in mvp's
  `tasks/unqualify-graded-basis-imports.md` (`github.com/billsix/modelviewprojection`).
- Related: [[generated-product-typing]] (the graded types + precise products), and the
  class-constant / "no local aliases" conventions in `CLAUDE.md`.

## Findings & recommendation (2026-08-04)

All claims below verified against freshly-generated `g1/g2/g3.py` (on disk), a REPL, the
full `pytest` suite (**347 passed**), and `ty check src tests tools` (**clean**, ty 0.0.58
at `/usr/bin/ty` — no `/usr` vs `/usr-local` split in this sandbox, so the result is
trustworthy).

**Recommendation: Option A (reverse it) — make the g1/g2/g3 module constants the graded
types.** It breaks nothing in the gate, is exactly what the mvp consumer asked for, is a
strict improvement for the graded notebook, and loses nothing (the full class stays
reachable as `G_n.e_1` / `G_n(...)`). The only follow-on edit is migrating the two
full-class teaching notebooks (`displayg2.py`, `displayg3.py`) from bare `e_1` to `G2.e_1`
/ `G3.e_1` — a mechanical rename, and arguably more self-documenting for notebooks whose
whole point is the full class.

### 1. Why the module constants are the full class today

Not a load-bearing decision — a **historical default that was never revisited.** The
module-level constants (`generate_constants(n, name)` in `tools/gen_specialized.py:2684`)
predate the graded subtypes: when they were written, the module's *only* type was the
headline `G_n`, so `e_1: G2 = G2.from_blade_dict(...)` was the only thing they could be.
The graded types (`Vector_n`/`Bivector_n`/… — "Future directions › Graded subtypes", now
built) arrived later, and `generate_constants` was never updated to use them. CLAUDE.md
codifies the status quo descriptively ("each `g*` module exports module-level constants of
its own type … `3*e_1 + 4*e_2` builds a `G2`"), but nothing structural *requires* the full
class. The generator already has everything needed to resolve a blade to its graded type —
`resolve([blade], n, name)` returns `Vector2` for `(1,)`, `Bivector2` for `(1,2)`,
`Scalar2` for `()`, `Trivector3` for `(1,2,3)` (verified).

**What actually relies on `from gacalc.g2 import e_1` being a `G2`** (enumerated, AST-checked
across `src`/`tests`, plus mvp):

- **`src/` and `tests/`: nothing.** No library module and no test imports the bare
  lowercase module constants (`e_1/e_2/e_3/e_12/e_13/e_23/e_123/zero/one`) from
  `gacalc.g1/g2/g3`. (They import the *classes* — `G2`, `Vector2`, … — and use the *class*
  constant `Vector2.e_1`.) No generated doctest uses a bare module constant either.
- **The only consumers are two notebooks:** `notebooks/displayg2.py` and
  `notebooks/displayg3.py` — the notebooks that teach the *full* `G2`/`G3` class. They
  `from gacalc.g2 import ... e_1, e_2, e_12, one, zero` (and the g3 analogue) and lean on
  the `G2` type: e.g. `i: G2 = e_1 * e_2`, `m: G2 = 3 * e_1 + 4 * e_2`, `unit_gram_fe: G2 =
  e_1`. **Notebooks are outside the gate** — `pytest.ini` sets `testpaths = src tests`
  (notebooks not collected) and `format.sh` runs `ty check` on `src`/`tests`/`tools` only —
  so even the type-annotation mismatch Option A would introduce there is not a gate failure.
- **mvp: unaffected.** mvp imports the *classes* `Vector2`/`Vector3` from `gacalc.g2`/`g3`
  and constructs `Vector2(x, y)` / uses `Vector2.e_1`; it never imports the bare module
  constants. (mvp's `tasks/unqualify-graded-basis-imports.md` explicitly *wants* Option A —
  it's the only way it can `from gacalc.g2 import e_1` and keep the `Vector2` type.)
- **`gn.py` is out of scope for the change.** Its module constants are `Gn`
  (dimension-agnostic, no graded subtypes exist for `Gn`), and `displaymv.py` /
  `displayrotations.py` import `from gacalc.gn import e_1, e_2, e_3` intending `Gn`. Option A
  touches only `g1/g2/g3`; gn stays as-is, correctly.

### 2. Option A — reverse it. What breaks: nothing gated.

Make `generate_constants` emit each constant at its **resolved graded type**. Verified
consequences:

- `3*e_1 + 4*e_2` → **`Vector2`** (today: `G2`). ← the goal, for free.
- `e_1 * e_2` → **`Rotor2`** (today: `G2`); `e_1 ^ e_2` → **`Bivector2`**; `zero`/`one` →
  **`Scalar2`**. All *tighter* static types; **runtime values are byte-identical** (checked:
  `3*e_1+4*e_2 == 3*Vector2.e_1+4*Vector2.e_2`, `e_1*e_2 == Vector2.e_1*Vector2.e_2`, both
  `True`).
- **Does any real call site depend on the `G2` result type of `e_1 * e_2`?** No — the only
  sites that annotate the result `G2` are in `displayg2.py`/`displayg3.py` (`i: G2 = e_1 *
  e_2`), which are notebooks, ungated. A `Rotor2` is **not** a subtype of `G2` (they're
  siblings under `MultiVectorBase` — see `generated-product-typing.md`), so under A those
  bare-`e_1` annotations would no longer type-check *if* the notebooks were ever ty-checked;
  they aren't, and the migration in §7 removes the mismatch anyway.
- **Suite + checker: green either way.** Nothing in `src`/`tests`/`tools` imports the bare
  constants, so `pytest` (347) and `ty` are unaffected by the type change. (This is a
  generator change; per CLAUDE.md its `git diff` is `tools/`-only — the regenerated
  `g*.py` are gitignored.)

### 3. Option B — additive (new export, leave the `G2` ones)

A second, distinct export of graded constants — e.g. a `gacalc.g2.basis` submodule
(`from gacalc.g2.basis import e_1`) or new module-scope names. **Zero breakage, but it does
not deliver Bill's ask.** The request is the *concise, unqualified* `from gacalc.g2 import
e_1`; B makes that path *longer* (`from gacalc.g2.basis import e_1`) and requires turning
`g2` from a module into a package (or adding a parallel `g2basis.py`) — more generator
machinery, two names for one value (a discoverability wart, and it invites exactly the kind
of ambiguity the "no local aliases" rule fights). B only wins if some real, *gated* consumer
needed the `G2`-typed bare constant — and none does. **Dominated by A here.**

### 4. What the notebooks import now, and the type they get

| notebook | imports | bare-const type today | Option A |
|---|---|---|---|
| `displaymv.py` | `from gacalc.gn import e_1, e_2` | `Gn` (`MultiVector`) | unchanged (gn not touched) |
| `displayrotations.py` | `gn` `e_1/e_2/e_3` **and** `Vector2.e_1`, `Bivector2.e_12` | `Gn` + graded | gn unchanged; already uses `Vector2.` for graded |
| `displaygraded.py` | **`Vector2.e_1`, `Vector3.e_1`, `Bivector3`** (class-qualified, verbose) | `Vector2`/`Vector3`/… | **could drop to bare `e_1` and stay graded — the win** |
| `displayg2.py` | `from gacalc.g2 import e_1, e_2, e_12, one, zero` | **`G2`** | migrate bare→`G2.e_1` (§7) |
| `displayg3.py` | `from gacalc.g3 import e_1..e_123, one, zero` | **`G3`** | migrate bare→`G3.e_1` (§7) |

So the "concise unqualified" form Bill likes in `displaymv` already works there **because
`gn`'s constant type (`Gn`) is the right type for that notebook.** The graded notebook
(`displaygraded.py`) is verbose (`Vector2.e_1`) precisely because no graded module constant
exists. Option A closes exactly that gap: it moves the concise bare name onto the graded
type, which is the type real teaching/consumer code reaches for.

### 5. "Without losing anything" — verified

- **Full `G_n` still reachable, concisely:** every full class keeps its own class constant
  `G2.e_1` / `G3.e_123` (full-class typed, `G2.e_1 = G2.from_blade_dict(...)` at
  `g2.py:1102`), plus `G2(...)`, `G2.from_blade_dict(...)`, and `Gn` for
  dimension-agnostic work. Nothing about building a general multivector is removed.
- **No runtime change:** values identical (checked across grades and both algebras).
- **Strictly more precise statically:** `Vector2`/`Bivector2`/`Rotor2`/`Scalar2` carry the
  fast closed-form paths and the precise product overloads; `G2` is the widen-to-container
  type. Narrowing the constants *adds* type information, removes none.
- **The one honest cost:** the concise bare name `e_1` is *reallocated* from "full class" to
  "graded". The two full-class notebooks trade `e_1` for `G2.e_1` (5-char prefix). That is a
  reallocation of conciseness toward the type used most often, not a loss of capability.

### 6. All grades / all algebras + how the generator emits it

`generate_constants(n, name)` (`tools/gen_specialized.py:2684`) currently annotates every
constant `name` (the full class) and builds via `name.from_blade_dict(...)` /
`name.from_scalar(...)`. Option A resolves per-blade instead (the generator already does this
for products):

```python
def generate_constants(n: int, name: str) -> list[ast.stmt]:
    nonempty = [b for b in blades_for_dim(n) if b != ()]
    scalar_name = scalar_spec(n).name          # Scalar_n
    nodes = [
        annotated_assign("zero", name_ref(scalar_name),
                         call(attribute(scalar_name, "from_scalar"), [constant(0)])),
        annotated_assign("one",  name_ref(scalar_name),
                         call(attribute(scalar_name, "from_scalar"), [constant(1)])),
    ]
    for b in nonempty:
        graded = resolve([b], n, name).name    # (1,)->Vector_n, (1,2)->Bivector_n, (1,2,3)->Trivector3
        nodes.append(annotated_assign(
            blade_label(b), name_ref(graded),
            call(attribute(graded, "from_blade_dict"),
                 [ast.Dict(keys=[constant(b)], values=[constant(1)])])))
    # __all__ unchanged (same names; graded type names already exported)
    ...
```

Coverage this produces, per algebra:

- **g1** (dim 1): `zero`/`one` → `Scalar1`; `e_1` → `Vector1`.
- **g2** (dim 2): `zero`/`one` → `Scalar2`; `e_1`,`e_2` → `Vector2`; `e_12` → `Bivector2`.
- **g3** (dim 3): `zero`/`one` → `Scalar3`; `e_1`,`e_2`,`e_3` → `Vector3`; `e_12`,`e_13`,`e_23`
  → `Bivector3`; `e_123` → `Trivector3`.
- **any future G4+**: falls out of `resolve` automatically (pseudoscalar → the top-grade
  graded type; mixed only if a blade needs a wider cover, which single blades never do).

Verified the constructors the emitted code would call all exist and behave:
`Vector2.from_blade_dict({(1,):1})`, `Bivector2.from_blade_dict({(1,2):1})`,
`Trivector3.from_blade_dict({(1,2,3):1})`, `Scalar2.from_scalar(1)` all round-trip. The
graded types are defined **before** `generate_constants` runs (emission order: scalar →
full class → graded → constants), so name references resolve. `gn.py` is not generated by
this path and is untouched.

### 7. Migration sketch (if A is approved)

1. **Generator:** the `generate_constants` change above; regenerate; `make check-regions`
   (basis-constant assignments are unmarked, so regions are unaffected) + `make test` +
   `ty check` (all expected green — nothing gated imports these).
2. **`notebooks/displaygraded.py` — the payoff:** it may drop the `Vector2.`/`Vector3.`
   prefix on basis constants once it imports them bare. Concretely, `a: Vector2 = 3 *
   Vector2.e_1 + 4 * Vector2.e_2` becomes `from gacalc.g2 import e_1, e_2` + `a: Vector2 = 3
   * e_1 + 4 * e_2` — matching the printed `3e₁ + 4e₂`, and *still* a `Vector2`. (Higher
   grades: `Vector3.e_1 ^ Vector3.e_2` → `e_1 ^ e_2`, a `Bivector3`.) This is the whole
   point of the exercise. Note: the "no local aliases" rule is satisfied — these are real
   imported names, not `e_1 = Vector2.e_1` rebindings.
3. **`notebooks/displayg2.py` / `displayg3.py` — keep teaching the full class:** replace the
   bare-constant import with the class constant, i.e. bare `e_1` → `G2.e_1` (`G3.e_1` for
   g3) at the ~18 g2 sites / analogous g3 sites, so every `i: G2 = ...`, `m: G2 = ...`
   annotation stays exact. (`translate(b=5 * e_1)`-style sites accept `MultiVectorBase`, so
   they'd work with either — but rename uniformly for clarity.)
4. **mvp:** unblocks `tasks/unqualify-graded-basis-imports.md` — it can then `from gacalc.g2
   import e_1` and keep `Vector2`. Gated on the gacalc release that ships this.
5. **CLAUDE.md:** update the "Two ways to name a basis blade" paragraph — module constants
   are now the *graded* type; the full class is reached via its class constant `G_n.e_1`.
