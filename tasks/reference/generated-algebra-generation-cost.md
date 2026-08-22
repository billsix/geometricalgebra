# Generation cost of the specialized 𝒢ₙ modules — how it scales, and why g4/g5 aren't default

**What this is:** the standing record of how long `tools/gen_specialized.py` takes to build each
`gN.py`, how that cost scales with dimension, the grade/dimension assumptions that had to be fixed
to generate beyond 𝒢₃, and the decision about which algebras ship in the default build. Consulted
before adding a new algebra to `ALGEBRAS` or changing the generation step in `entrypoint/shell.sh`
/ `make dist` / `make check-generated`.

Measured 2026-08-22 (William Emerison Six <billsix@gmail.com>) on the dev container.

## Measured build times

Node-build time only — running `Gn`'s symbolic geometric/inner/outer products on sympy symbols and
`sympy.cse`/`simplify`-ing the closed forms. Excludes ruff-format (negligible: << 1 s even for the
big modules). This is the cost paid by `make generate`, and today by **every** `make shell`.

| algebra | blades (2ⁿ) | term-pairs (4ⁿ) | build time | ×prev |
|---------|-------------|-----------------|------------|-------|
| 𝒢₁ | 2  | 4    | < 1 s        | —     |
| 𝒢₂ | 4  | 16   | < 1 s        | —     |
| 𝒢₃ | 8  | 64   | **23.3 s**   | —     |
| 𝒢₄ | 16 | 256  | **292.5 s ≈ 4.9 min** | 12.6× |
| 𝒢₅ | 32 | 1024 | **5214.9 s ≈ 87 min (1 h 27 m)** | 17.8× |

### Why it's superlinear (and the factor accelerates)

The full `G_n` symbolic geometric product touches ~4ⁿ term pairs (every basis-blade pair), but the
per-pair cost *also* grows: `sympy.simplify` runs on expressions whose size scales with the number
of contributing terms, which itself grows with n. So each +1 in dimension multiplies both the number
of simplifications and the cost of each. That compounding shows in the measured **×prev** column: the
step is **12.6× for 𝒢₃→𝒢₄, then 17.8× for 𝒢₄→𝒢₅** — the growth factor is itself *rising*, not
constant, each for a 4× term-pair increase. Extrapolating, 𝒢₆ would be many hours. Generated source
size roughly doubles per step (g4 ≈ 259 KB, g5 ≈ 529 KB). The generated *code* stays fast; this is a
one-time *generation* cost.

## Grade/dimension assumptions that block n ≥ 4 (fix before adding an algebra)

Generation of 𝒢₄ originally crashed (`IndexError`) — the generator carried grade-≤3 assumptions.
Known and fixed / to-check:

- **FIXED — axis-letter coordinates cap at 3.** `coordinate_property_defs`
  (`tools/gen_specialized.py:769`) emits the `x`/`y`/`z` read-only properties on the grade-1
  `Vector` type by indexing `AXIS_NAMES = ("x","y","z")`. In 𝒢₄ a `Vector` has an `e_4` coordinate
  with no axis letter → `IndexError`. Fix (2026-08-22): skip the letter property for `e_4`+; those
  coordinates are reached via `coeff_e_4` / `.coefficient(...)`. Only grades 1–3 get `x`/`y`/`z`.
- **TO CHECK when actually adding g4/g5:** any *other* hard-coded grade-≤3 spot — the graded-type
  registry only defines up to `Trivector` + `Rotor` (`graded_specs`, `:626`), so grade-4/5 blades
  currently widen to the full `G`; dual/product result resolution, the `i`/`plane_of_rotation`
  extractors, and dispatch tables should be re-verified against real generated g4/g5 output.

## Why g4/g5 are NOT in the default build (and what would change that)

The generated `gN.py` are **gitignored and regenerated unconditionally on every `make shell`**
(`entrypoint/shell.sh`) and `make dist`, and **twice** for `make check-generated` (regenerate-twice
determinism guard). Today that's ~23 s (g1+g2+g3, g3-dominated). Consequences of naively adding
higher dims to `ALGEBRAS`:

- g4 default → **every `make shell` blocks ~5 min** before a prompt; `check-generated` ~10 min.
- g5 default → **~87 min per shell**; `check-generated` (regenerates twice) **~3 hr**. Untenable.

**Decision (2026-08-22): release-only generation of the high dims.**

1. **Parameterize the generated dim-set by build context** — a `GACALC_DIMS` env var (default
   `1,2,3`). `make shell` / normal dev generates g1–g3 only, so **dev never pays the g4/g5 cost at
   all**. `make dist` / `make release` set `GACALC_DIMS=1,2,3,4,5`, so g4/g5 are generated **once at
   publish** and baked into the sdist/wheel.
2. **`setup.py`'s if-missing `GENERATED` list stays `[g1,g2,g3]`** — a git-checkout build must not
   silently pay the ~1.5 hr; the shipped sdist already contains all dims.
3. **A CI / opt-in full-dim gate is REQUIRED** (`GACALC_DIMS=1,2,3,4,5 make test` + lint) — because
   dev never generates g4/g5, an n≥4 generator bug (like the `AXIS_NAMES` crash above) would
   otherwise first surface at release. This is the one real cost of release-only: g4/g5 aren't
   exercised in the normal dev loop, so a separate slow gate must exercise them.
4. **Scope `make check-generated`** to a cheap dimension (or make high-dim determinism opt-in), since
   it regenerates twice (g5 twice ≈ 3 hr).

Rejected alternative — **incremental / only-if-missing generation** (regenerate a dimension only when
its `gN.py` is absent): keeps g4/g5 locally testable, but still makes the first `make shell` on a
fresh tree pay the one-time cost (g5 ~87 min). Release-only keeps dev at *zero* g4/g5 cost, which the
maintainer preferred.

Value beyond the numbers: running this end-to-end **verified the generator works past 𝒢₃** (once the
`AXIS_NAMES` assumption is fixed) rather than assuming it did — the failure was a real bug, found by
trying.

## Related

- Task: `tasks/precise-blade-typing-and-g4-g5-default.md` (the work these findings scope).
- `tasks/reference/code-generator-architecture.md` — how the generator is structured.
- `README.md` "add a dimension" section + the generation-cost heads-up.
