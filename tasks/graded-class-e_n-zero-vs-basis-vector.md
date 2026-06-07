# Why `Vector2.e_1` is `0` (not the basis vector) — and should it be?

**Status:** Phase 1 **done** (awaiting author commit) · Phases 2 & 3 pending go-ahead · started 2026-06-07

## Phase 1 — DONE 2026-06-07 (coeff_* field rename)

Fields renamed `scalar/e_1/e_2/e_12/e_123` → `coeff_scalar/coeff_e_1/…` across **all** generated
classes (`G1/G2/G3`, graded subtypes, `Scalar`). All in `tools/gen_specialized.py`; no hand-edits to
generated files. **161 tests pass, `ty` + `ruff` clean, `make check-generated` deterministic.**

What changed in the generator:
- **Split the overloaded `field_name`** into two functions so a name predicts its role:
  - `blade_label(blade)` → `e_1`/`e_12`/`scalar` — the *human/blade label*. Used for docstrings and
    the internal cse symbol names (`a_e_1`/`b_e_1`).
  - `field_name(blade)` → `coeff_e_1`/`coeff_e_12`/`coeff_scalar` — the *dataclass field*.
  - `blade_of_field` → renamed `blade_of_label` (it inverts `blade_label`; used by `term_grade_key`).
- **rename_map** now maps symbol `a_e_1` (label) → attribute `self.coeff_e_1` (field) — i.e. LHS uses
  `blade_label`, RHS uses `field_name`. This keeps the symbolic layer readable while fields are
  `coeff_*`. `term_grade_key`/`blade_of_label` unchanged in logic.
- **Hardcoded `"scalar"` field literals** (the `Scalar` class + every `construct("Scalar", …)`,
  `dot(self/rhs/other, "scalar")`, the scalar field decl, `Scalar.from_blade_dict`) → `field_name(())`
  = `coeff_scalar`. The non-field `"scalar"` uses (TypeSpec `kind`, `grade_words`, the label itself)
  were left alone.
- **Module-level public constants** (`g2.e_1`, … and `__all__`) deliberately kept as **`blade_label`**
  (`e_1`, not `coeff_e_1`) — they are the public basis constants and must not change name.
- **Docstrings** reworded "stored as named fields: e_1, e_2" → "basis blades: e_1, e_2" (the fields
  are now `coeff_*`; the listing describes blades, via `blade_label`).

Cross-code sweep confirmed nothing else needed changing: `tests/`, `notebooks/`, `README.md`,
`tools/bench.py` use only module constants (`gn.e_1`), `basis_vector(n)`, and the blade-dict protocol
— none reference the dataclass field names or scrape the dataclass `repr`. `base.py`/`gn.py` are
field-name-agnostic (blade-dict interchange; `Gn` stores `coefficient_of_blade`) — untouched.

Observable change for users: dataclass `repr` and constructor kwargs are now `coeff_*`
(`Vector2(coeff_e_1=1, coeff_e_2=0)`). `Vector2.coeff_e_1` (class attr) is still the field default
`0` — Phase 2 introduces `e_1` as the basis-vector constant.



## Observation (author's shell session)

On a generated `G2` build, the graded subtype `Vector2` has a class attribute `e_1` that resolves to
`0`, not to the e₁ basis vector. The basis vector only comes from the `basis_vector(n)` classmethod:

```python
>>> gacalc.g2.Vector2.e_1
0
>>> 5 * gacalc.g2.Vector2.e_1
0
>>> 5 * gacalc.g2.Vector2.e_1 + 3 * gacalc.g2.Vector2.e_2
0
>>> gacalc.g2.Vector2.basis_vector(1)
Vector2(e_1=1, e_2=0)
>>> 5 * gacalc.g2.Vector2.basis_vector(1)
Vector2(e_1=5, e_2=0)
>>> 5 * gacalc.g2.Vector2.basis_vector(1) + 2 * gacalc.g2.Vector2.basis_vector(2)
Vector2(e_1=5, e_2=2)
```

Author's expectation: `Vector2.e_1` *should* be the same basis vector that `Vector2.basis_vector(1)`
returns.

## Questions to answer

1. **Why does `Vector2.e_1` resolve to `0`?** (Mechanism: it's almost certainly the dataclass *field*
   `e_1` whose default is `0`, read off the class object rather than an instance.)
2. **Does `Vector2.e_1` resolving to something-other-than-the-basis-vector have any actual value or
   use anywhere in the code?** Grep for class-level field access, default usage, codegen reliance.
3. **If it has no value:** make `<GradedClass>.e_n` equal to `basis_vector(n)` across *all* generated
   classes (graded subtypes and full `G1`/`G2`/`G3`), consistently. Decide the mechanism (the `g*`
   modules already export module-level `e_1`/`e_2` constants of the right type — the issue is the
   *class attribute* shadowing for graded subtypes).

## Plan

- [ ] `make generate` (or `python tools/gen_specialized.py`) to materialize `g2.py` etc.
- [ ] Reproduce the shell session; confirm `e_1` is the dataclass field default.
- [ ] Study mechanism + search for any reliance on the current behavior (codegen, tests, base ops).
- [ ] Write up: is the current behavior load-bearing? Recommendation.
- [ ] **Stop for go-ahead** before changing any source/generator.

## Findings

### 1. Mechanism — why `Vector2.e_1` is `0`

`Vector2` is a plain (non-slots) `@dataclass` whose **fields are named after the basis blades**:
`e_1`, `e_2` (and `G2` adds `scalar`, `e_12`). Each field has default `0`. In generated `g2.py`:

```python
class Vector2(AbstractMultiVector):
    e_1: numbers.Real = typing.cast(numbers.Real, 0)
    e_2: numbers.Real = typing.cast(numbers.Real, 0)
```

So `e_1` is the **per-component coefficient field**, and on an *instance* it holds that component's
value. Class access reads the field default:

```
instance  Vector2(e_1=5, e_2=2).e_1  →  5      # the COEFFICIENT (correct, load-bearing)
class     Vector2.e_1                 →  0      # the field default leaking through the class object
```

`Vector2.e_1 == 0` is therefore not a designed value — it's just standard dataclass behavior (the
default becomes a class attribute; instances shadow it with their own).

### 2. Does the current `Vector2.e_1 → 0` behavior have any value/use? **No.**

Searched `src`, `tests`, `tools`, `notebooks`. Every `e_1`/`e_2` reference is one of:
- **instance field access** in generated methods (`self.e_1`, `rhs.e_1`, `lhs.e_2`) — uses the
  coefficient; unaffected by class access.
- **module-level constants** `gn.e_1`, `g2.e_1` — but note `g2.e_1` is typed **`G2`**, not `Vector2`
  (`g2.py:1161  e_1: G2 = G2.from_blade_dict({(1,): 1})`).
- **`Vector2.basis_vector(1)`** — the only way to get a `Vector2`-typed basis vector. The graded
  tests build `E1, E2 = Vector2.basis_vector(1), Vector2.basis_vector(2)` (`test_graded.py:43`).

Nothing reads `Vector2.e_1` as a class attribute or relies on it being `0`.

### 3. The catch — you can't just "make them the same"

The name `e_1` is **already taken by the coefficient field**, and that instance meaning is essential
(`Vector2(e_1=5).e_1` must be `5`). So:

- **Can't** set the field *default* to `basis_vector(1)` — then `Vector2()` and every
  partially-constructed value would get a `Vector2` object as a coefficient. Broken.
- The only way to have **class access** `Vector2.e_1` return the basis vector while **instance
  access** `inst.e_1` returns the coefficient is a **descriptor / metaclass** that distinguishes the
  two accesses (e.g. a data descriptor whose `__get__` returns `basis_vector` when `obj is None`).
  That is real machinery, has to be code-generated for every class, and risks surprising anyone who
  reasonably expects `Vector2.e_1` and `inst.e_1` to mean the same kind of thing.

So "they should be the same" runs into a genuine semantic collision: one name, two desired meanings.

## Agreed direction (author-decided 2026-06-07)

Three coordinated phases, each independently testable and committable **in this order**. The author
commits between phases (per repo convention; Claude does not commit).

**Why this shape (the rationale that ties the phases together):**
- The current `e_n` names are *coefficient storage* fields; their instance values are load-bearing,
  but the *class* attribute `Cls.e_1 == 0` is an accidental dataclass-default leak with **no use**
  (Finding 2). Freeing the `e_n` names lets them become the basis vectors the author expects.
- Once `e_n` is no longer a dataclass field, a **plain class-level constant** `e_1 = basis_vector(1)`
  serves *both* `Cls.e_1` and `inst.e_1` (no instance entry shadows it) — so no descriptor/metaclass
  magic is needed (this is the simple form of the old option "B").
- Users should read components through the **algebra**, not raw fields: `component(blade)` (scalar)
  and `project(blade)` (blade-valued). That works identically on `Gn` (which has **no** named fields)
  and the specialized classes, so the renamed `coeff_*` fields become pure private storage.

**Cross-cutting invariant that contains the blast radius:** every cross-representation interaction
goes through the **blade-dict interchange** (`to_blade_dict`/`from_blade_dict`, keyed by blade tuples
like `(1,)`, *not* field names) and through module-level constants (`gn.e_1`, `g2.e_1`). So renaming
the dataclass fields is internal to each generated class — the dict keys, equality, products, and all
existing tests that use `gn.e_1` / `basis_vector(n)` / `E1,E2` are unaffected. The observable change
is **`repr`** (auto-dataclass repr uses field names) and the **constructor kwargs** (`Cls(e_1=...)`).

### Generator mechanics (where the levers are — `tools/gen_specialized.py`)

- `field_name(blade)` (line ~113) currently maps `()->'scalar'`, `(1,)->'e_1'`, `(1,2)->'e_12'`. It
  is the **single source** of the field identifier — used for field decls (`field_decls`, ~514),
  `to_blade_dict` (`dot("self", field_name(b))`, ~548), `from_blade_dict` (kwargs, ~526), every
  product/`__add__`/unary body (`construct(..., (field_name(b), ...))`), **and also** for internal
  CSE symbol names (`"a_"+field_name(b)`, ~363/381/442) **and docstring blade tables** (~172, 204-237).
- **Must split two concerns** that currently share `field_name`:
  - `field_name(blade)` → the **dataclass field** → becomes `coeff_e_1`/`coeff_e_12`/`coeff_scalar`.
  - a new `blade_label(blade)` → the human/blade label `e_1`/`e_12`/`scalar` → used for the
    **docstring tables** (which should keep saying `e_1, e_2  grade 1`) and may keep the internal
    symbol prefixes readable. `blade_of_field` (the inverse, ~121) must invert whichever name the
    symbol-rename path (`expr_to_ast`, ~144-148) actually consumes — keep that path self-consistent.
- After editing the generator: `make generate`, then `make check-generated` (byte-determinism), then
  full suite + `ruff` + `ty check src tests`.

---

### Phase 1 — rename coefficient fields to `coeff_*` (pure refactor, no behavior change)

Fields become `coeff_scalar`, `coeff_e_1`, `coeff_e_2`, `coeff_e_12`, `coeff_e_123`, …

- [x] Generator: introduce `coeff_`-prefixed `field_name`; add `blade_label` for docstrings/symbols
      (see mechanics above). Regenerate; confirm output **AST-stable & deterministic**.
- [x] **Sweep all code & notebooks for field-name dependence** (the observable surface):
  - `src/` — base.py is field-name-agnostic (uses the blade-dict protocol; only mentions
    "coefficient" in comments) — **verify** it needs no change. gn.py uses `coefficient_of_blade`
    (a different name) — **verify** untouched.
  - `tests/` — current suite uses `gn.e_1` / `basis_vector(n)` / `E1,E2`, **not** `Cls(e_1=...)`
    kwargs (good). Grep for any `(e_1=`, `(scalar=`, `.e_1`/`.e_2`/`.e_12` *instance/field* access,
    and any `repr()`/string assertion on a specialized value. Update kwargs → `coeff_*`.
  - `notebooks/` (`displayg2.py`, `displayg3.py`, `displaygraded.py`, `displaymv.py`,
    `nbplotutils.py`) — these pull components via `to_blade_dict()` (blade keys, unaffected) and
    display via `_repr_latex_`/`show()` (not dataclass repr). **Grep for any direct `.e_1`/`(e_1=`**
    and for code that scrapes the dataclass `repr` string; fix any found.
  - `tools/bench.py` — grep for field kwargs / `.e_1`.
  - `README.md` — the "Graded subtypes" section shows `Vector2(e_1=1, e_2=0)`-style **repr output**;
    update those example outputs to the new repr, and any prose naming the fields.
- [x] Suite green, `make check-generated`, `ruff`, `ty check src tests` clean. **Stop — author commits.**

### Phase 2 — `e_1`, `e_2`, `e_12`, … become basis-vector class constants

With the `e_n` names freed, define them as class-level constants of each class's own type.

- [ ] Generator: emit, per generated class, class-level constants `e_1 = basis_vector(1)`, … and the
      pseudoscalar (`e_12`/`e_123`) — each of that class's type. Decide placement (class body vs.
      assigned just after the class) and that **both** `Cls.e_1` and `inst.e_1` resolve to it.
- [ ] Reconcile with the **existing module-level constants** (`g2.e_1: G2 = …`, `gn.e_1`): decide
      whether class constants on graded subtypes should be the graded type (e.g. `Vector2.e_1` is a
      `Vector2`) — almost certainly yes — and ensure no name clash/confusion with the module-levels.
- [ ] **`Gn` consistency:** `Gn` is dimension-agnostic and cannot carry a fixed `e_1..e_n` set, so it
      keeps **only** the module-level `gn.e_1..e_10` constants. Document this asymmetry (specialized
      classes gain class constants; `Gn` relies on module constants + `basis_vector(n)`). Confirm
      nothing assumes `Gn.e_1` exists.
- [ ] Update README/notebooks to show the new idiom (`Vector2.e_1`, `G3.e_123`). Suite + guards green.
      **Stop — author commits.**

### Phase 3 — make `component` the correct, blessed getter (resolves known-issue #2)

`base.py:207` `component(x) = self.dot(x).scalar_part()` is correct for vectors but **sign-wrong for
grade ≥ 2** (`e_12 · e_12 = −1`). Fix to the grade-general extraction `⟨A x̃⟩₀`.

- [ ] `base.py`: `component(self, x) -> Real: return (self * x.reverse()).scalar_part()` (reverse =
      inverse for unit Euclidean blades; robust for non-unit `x` too). Drop the "TODO - is this
      really how I should define it?" comment. **One change in the ABC covers `Gn` and all
      specialized classes** (none override `component` — verify via grep of the generator).
- [ ] Add tests (currently `component` is **untested** — that's why the bug hid): scalar coefficient
      of a vector along `e_1`, of a bivector along `e_12` (the sign case), and a round-trip
      `sum(c.component(b)*b for b in basis) == c`. Parametrize over `[Gn, G1, G2, G3]` like
      `test_conformance.py`, and add the graded-subtype cases in `test_graded.py`.
- [ ] Update CLAUDE.md known-issue #2 (remove `component` from the "not sure" list once verified) and
      document `component`/`project` as the public way to read components. README usage example.
- [ ] Suite + guards + `ruff` + `ty` green. **Stop — author commits.**

## Open questions for the author

- **`coeff_scalar` or leave `scalar`?** `scalar` doesn't collide with any basis-vector name, but
  mixing `scalar` (bare) with `coeff_e_1` (prefixed) is inconsistent. Plan assumes `coeff_scalar` for
  uniformity — confirm.
- **Phase 3 in this task or its own?** It touches `base.py`/`Gn` and is verifiable independently of
  the rename. Folded in here because the rename is what makes `component` the *primary* user path;
  say if you'd rather split it.
