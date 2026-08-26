# Thin pass-through instance methods for project / reject (apply-to-this-value sugar)

**Status:** DONE 2026-08-26 (William Emerison Six <billsix@gmail.com>) — this spec's
implementation shipped in [[precise-typing-remaining-methods]] (Tier 3); see its Outcome. The
methods landed as `projected_onto` / **`rejected_away_from`** / **`reflected_across`** — the latter
two renamed from this doc's original `rejected_from` / `reflected_in` (they dropped the factory's
`away_from` / `across` keyword and "rejected from" misread as "excluded from"). This doc remains the
design record (rationale, boundary, call-site sweep).
**Priority:** 4
**Difficulty:** 2

## Decisions (Bill, 2026-08-25)

- **Names: `projected_onto` / `rejected_away_from` / `reflected_across`** (past-participle, value-returning).
  Include `reflected_across` for symmetry with the factory trio.
- **Do the work during [[precise-typing-remaining-methods]], not as a standalone ship.** Add the
  base pass-throughs **and** their precise graded return typing together there (same overload
  machinery that task already built for the `project`/`reject` factories) — so `Vector.rejected_away_from(b)`
  is a `Vector` statically from day one, no interim `-> MultiVectorBase` version to revise.
- **`content_by_rejection`** unrelated (that's the doctest task); ignore here.

## Question Bill asked → answer: **yes, this is useful and idiomatic here.**

`project` / `reject` / `reflect` are classmethod **factories** returning a `ComposableFunction`
(`base.py:756/807/854`), so *applying* one to a value reads verbosely — worst case in
`make_orthogonal_frame` (`frame.py:116-122`):

```python
orthogonal: list[MultiVectorBase] = []
for v in vectors:
    w: MultiVectorBase = v
    for prior in orthogonal:
        w = type(w).reject(away_from=prior)(w)   # <- the noise
    orthogonal.append(w)
return orthogonal
```

A pass-through instance method makes the inner line `w = w.rejected_away_from(prior)`. Three reasons
it's the right call, not just nicer:

1. **Established precedent in this very codebase.** CLAUDE.md (Architecture › measures): the
   fixed-arity measures "also exist as thin pass-through **methods** on `MultiVectorBase`
   (`v.area(w)`) **for discoverability**." A `v.rejected_away_from(b)` pass-through is the same move for
   projection/rejection.
2. **Many call sites are immediate applications**, not factory reuse. `grep` shows the
   `Cls.project(onto=b)(a)` / `Cls.reject(away_from=b)(a)` shape throughout `tests/` and
   `notebooks/` (e.g. `notebooks/displayg2.py:637` `a_par = Vector.project(onto=b)(a)`), plus
   `frame.py:120`. All of these read better as `a.projected_onto(b)` / `a.rejected_away_from(b)`.
3. **Zero cost to the existing design** — see the boundary below.

## The change

Add thin, value-returning pass-throughs on **`MultiVectorBase`** (`base.py`) — one definition,
inherited by `Gn` and every generated type, **no generator changes**:

```python
def projected_onto(self, onto: MultiVectorBase | Sequence[MultiVectorBase]) -> MultiVectorBase:
    """Apply the projection P_onto to this value (sugar for project(onto)(self))."""
    return type(self).project(onto)(self)

def rejected_away_from(self, away_from: MultiVectorBase | Sequence[MultiVectorBase]) -> MultiVectorBase:
    """Apply the rejection away from `away_from` to this value."""
    return type(self).reject(away_from)(self)

# optional, for symmetry:
def reflected_across(self, across: MultiVectorBase | Sequence[MultiVectorBase]) -> MultiVectorBase:
    return type(self).reflect(across)(self)
```

`type(self).…` (not `MultiVectorBase.…`) so the generated types' own overrides run and the runtime
result keeps the concrete type (the graded types already narrow — `tests/test_dot_wedge_projection_split.py:137-145`
asserts `Vector.project(onto=…)(…)` is a `Vector`).

## The boundary — what stays the factory (keep the originals; Bill asked for this)

The pass-through is **only** for "apply once to this value." The factory `project(onto)` /
`reject(away_from)` **must stay** and is still required wherever the function itself is the object:
- composed into a pipeline / wrapped in `ComposableFunction` (label) — e.g. `transforms.py:213-214`,
  `base.reflect`'s own `project`+`reject` split (`base.py:865-866`), the notebooks' labelled
  `ComposableFunction(Gn.project(...), "P_{…}")`;
- used as a Cayley-graph edge in *modelviewprojection* (needs the `InvertibleFunction`);
- assigned to a variable and reused.

So this is purely **additive**: no signature of `project`/`reject`/`reflect` changes.

## Where to define it (Bill's "generated types, or base, or gn?")

**`base.py` (`MultiVectorBase`).** It's representation-agnostic and delegates to
`type(self).project/reject`, so one definition covers `Gn` and all generated `g*` types with no
generator work — strictly better than emitting it per generated type or putting it on `gn` only.

## Call-site sweep (part of the task, use discretion)

Update the **immediate-application** sites to the pass-through, and leave every **factory-reuse**
site alone:
- **Convert:** `frame.py:120`; the `Cls.project(onto=b)(a)` / `Cls.reject(away_from=b)(a)` one-shots
  in `notebooks/displayg2.py`, and any test asserting on an applied value where readability improves.
- **Do NOT convert:** `transforms.py:213-214`, `base.py:865-866`, `test_transforms.py` /
  `displaymv.py` / `displayrotations.py` sites that keep the function object, and the
  `assert_type`/typing tests that deliberately exercise the factory form.

Open questions all resolved — see **Decisions** above.

## Verify

- `make test` green (add a couple of pass-through tests: `v.rejected_away_from(b) == reject(b)(v)`, and a
  graded-type identity so the concrete return type is exercised).
- `make format` clean (`ruff` + `ty check src`).

## Cross-links

- `src/gacalc/base.py:756/807/854` — the `project`/`reject`/`reflect` factories.
- `src/gacalc/frame.py:116-122` — the motivating call site (`make_orthogonal_frame`).
- `tasks/precise-typing-remaining-methods.md` (in-progress) — precise typing of project/reject; the
  natural home for typing these pass-throughs precisely (see open question 3).
- CLAUDE.md › Architecture (the `v.area(w)` pass-through precedent) and › "What earns an extraction".
