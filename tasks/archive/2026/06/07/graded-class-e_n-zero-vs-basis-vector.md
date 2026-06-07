# Why `Vector2.e_1` is `0` (not the basis vector) — and should it be?

**Status:** complete
**Completed:** 2026-06-07
(Phase 1 committed `6c88fae`; Phases 2 & 3 done — awaiting author commit. Started 2026-06-07.)

## Phase 3 — DONE 2026-06-07 (component is the blessed grade-general getter)

`AbstractMultiVector.component(x)` was `self.dot(x).scalar_part()` with a "TODO - is this really how
I should define it?" comment — correct for vectors but **sign-wrong for grade ≥ 2** (`e_12 · e_12 ==
−1`). Fixed to the grade-general extraction `⟨A x̃⟩₀`:

```python
return (self * x.reverse()).scalar_part()
```

- One change in the **ABC** (`base.py`) — `component` is not overridden anywhere (verified), so it
  covers `Gn`, `G1/G2/G3`, and every graded subtype. Added a real docstring (Hestenes-style: the
  orthonormal-basis coefficient α_J = ⟨A ẽ_J⟩, reverse = inverse for unit Euclidean blades) and noted
  `x` is expected to be a **unit** basis blade (the class constants / `gn.e_1` are exactly these);
  pointed to `project` for the blade-valued part.
- **Tests added** (component was previously untested — that's why the bug hid): `test_component` in
  `test_conformance.py` (parametrized over `[Gn, G1, G2, G3]`, n=1..3) checks every blade's
  coefficient incl. the grade-≥2 sign case and the reconstruction identity
  `Σ_b component(b)·b == x`; `test_component_reads_coefficients` in `test_graded.py` covers the graded
  subtypes (vector/bivector/trivector + a 3D bivector component). **170 tests pass** (+7), `ty` +
  `ruff` clean.
- Docs: CLAUDE.md known-issue #2 now lists only `inverse`/`is_parallel_to` (component resolved);
  README quick-start shows `a.component(e_1)`; the Architecture/Phase-2 text already points users at
  `component`/`project` as the way to read components.

## Phase 2 — DONE 2026-06-07 (e_n basis-vector class constants)

`e_1`/`e_2`/`e_12`/`e_123`/… are now **class constants of each class's own type** on every generated
class (`G1/G2/G3` and the graded subtypes). The original puzzle is resolved:
`Vector2.e_1 == Vector2.basis_vector(1)`, and instance access `inst.e_1` falls through to the same
constant (not shadowed, since the field is `coeff_e_1`). **163 tests pass (+2 new), `ty` + `ruff`
clean, `make check-generated` deterministic.**

Implementation (all in `tools/gen_specialized.py`):
- Two new generator helpers: `basis_classvar_decls(name, blades)` emits `e_1: typing.ClassVar[Name]`
  (annotation only) into the class body for each **nonempty** blade — ClassVar so it's excluded from
  the dataclass fields/`__slots__` and so `ty` knows the attribute; `basis_constant_assignments(name,
  blades)` emits `Name.e_1 = Name.from_blade_dict({(1,): 1})` **after** the class (a class can't
  reference itself mid-definition).
- Wired into both `generate_class` (full `G_n`, `slots=True`) and `generate_graded_type` (graded,
  non-slots): ClassVar decls appended right after `class_header_stmts`; the post-class assignments
  appended to each generator's returned node list. Verified the slots=True case works (probe + tests).
- Scalar gets none (no nonempty blades). The scalar unit stays `from_scalar` / module-level `one`.

Decisions:
- **Per-type constants:** `Vector2.e_1` is a `Vector2`, `G2.e_1` is a `G2`, `Bivector2.e_12` a
  `Bivector2`, etc. Each class gets a constant for each of *its* nonempty blades.
- **Coexist with module-level constants:** the existing `gn.e_1`/`g2.e_1` module globals (G-typed)
  are untouched; the new class constants are an additional, type-precise access path. No clash
  (class namespace vs module namespace).
- **`Gn` asymmetry (intentional):** `Gn` is dimension-agnostic, so it gets **no** class constants —
  users use module-level `gn.e_1 …` or `Gn.basis_vector(n)`. Confirmed nothing assumed `Gn.e_1`.

Docs updated: README "Graded subtypes" (uses `Vector2.e_1`, explains the class-constant /
instance-fallthrough / `component` read-back model), CLAUDE.md "Architecture" (`coeff_*` fields +
the class-constant mechanism + the `Gn` asymmetry), and `notebooks/displaygraded.py` (new idiom).
New tests: `test_basis_blade_class_constants`, `test_basis_constant_instance_fallthrough`.


## Phase 1 — COMPLETE 2026-06-07 (coeff_* field rename) — committed `6c88fae`

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

- [x] Generator: emit, per generated class, class-level constants `e_1 = basis_vector(1)`, … and the
      pseudoscalar (`e_12`/`e_123`) — each of that class's type. **ClassVar decl in body + post-class
      `Cls.e_1 = Cls.from_blade_dict(...)`**; both `Cls.e_1` and `inst.e_1` resolve to it.
- [x] Reconcile with the **existing module-level constants** — class constants are per-type
      (`Vector2.e_1` is a `Vector2`); module globals untouched; no clash.
- [x] **`Gn` consistency:** no class constants on `Gn` (dimension-agnostic); documented; confirmed
      nothing assumes `Gn.e_1`.
- [x] Update README/notebooks to show the new idiom (`Vector2.e_1`, `G3.e_123`). Suite + guards green.
      **Stop — author commits.**

### Phase 3 — make `component` the correct, blessed getter (resolves known-issue #2)

`base.py:207` `component(x) = self.dot(x).scalar_part()` is correct for vectors but **sign-wrong for
grade ≥ 2** (`e_12 · e_12 = −1`). Fix to the grade-general extraction `⟨A x̃⟩₀`.

- [x] `base.py`: `component(self, x) -> Real: return (self * x.reverse()).scalar_part()`, with a real
      docstring; documented as expecting a **unit** basis blade. Dropped the TODO comment. **One ABC
      change covers `Gn` and all specialized/graded classes** (verified: no override anywhere).
- [x] Added tests: `test_component` (parametrized `[Gn, G1, G2, G3]`, n=1..3) — every blade's
      coefficient incl. the grade-≥2 sign case and the `Σ component(b)·b == x` reconstruction;
      `test_component_reads_coefficients` (graded subtypes) in `test_graded.py`.
- [x] CLAUDE.md known-issue #2 updated (component resolved); README quick-start shows
      `a.component(e_1)`; Architecture text points at `component`/`project`.
- [x] Suite (170) + `ruff` + `ty` green. **Stop — author commits.**

## Open questions for the author

- **`coeff_scalar` or leave `scalar`?** `scalar` doesn't collide with any basis-vector name, but
  mixing `scalar` (bare) with `coeff_e_1` (prefixed) is inconsistent. Plan assumes `coeff_scalar` for
  uniformity — confirm.
- **Phase 3 in this task or its own?** It touches `base.py`/`Gn` and is verifiable independently of
  the rename. Folded in here because the rename is what makes `component` the *primary* user path;
  say if you'd rather split it.
