# Add docstrings everywhere, rendered well by the book's autodoc

**Status:** in progress (branch `sphinxDocstringUpdates`). Coverage + the Sphinx rendering/config
fixes are DONE and committed (`07fedcd`). The full napoleon-Google rewrite of `base.py`/`gn.py`
is DONE (2026-09-26, staged not committed), AND the grade-specialized generated docstrings
(`CUSTOM_METHOD_DOCS` in `tools/gen_specialized.py`) are now Google-style too (2026-09-26, staged).
The in-container `make docs` render gate has now been RUN (2026-09-26) and is clean: exit 0,
102-page `geometry2.pdf`, **0** substitution warnings, **0** missing-glyph, **0** undefined
hyperrefs, **0** ambiguous cross-refs. (Building the `BUILD_DOCS` image nested + running `make docs`
was done here.) Remaining before archive: harvest the durable book-pipeline facts to
`book-and-docs-pipeline.md`. See the (now-fixed) `book/docs/conf.py` E501 note below.

**Ambiguous-cross-ref fix (2026-09-26).** The first `make docs` after the base.py rewrite emitted 8
`WARNING: more than one target found for cross-reference 'ComposableFunction'/'InvertibleFunction'`
— those two names are re-exported by BOTH `gacalc.functions` and `gacalc.transforms`, so the bare
type tokens in my new `Returns:` fields (project/reject → ComposableFunction, reflect/identity →
InvertibleFunction) resolved ambiguously. Fixed by qualifying those 4 `Returns:` type tokens to the
canonical `gacalc.functions.ComposableFunction` / `gacalc.functions.InvertibleFunction` (truthful —
that's where they're defined; transforms only re-exports). Rebuild → 0 ambiguous refs, everything
else still 0. The generated `vector|project/reject/reflect` entries keep the bare name (g1/g2/g3 are
not autodoc-rendered, so they emit no cross-ref warning).
**Priority:** 5 **Difficulty:** 6 **Created:** 2026-06-13 **Updated:** 2026-09-26
(William Emerison Six <billsix@gmail.com>)

## BLUF

Every symbol the book's autodoc renders should have a good, Google-style, cleanly-rendering
docstring. This session did the coverage sweep of the hand-written modules and the Sphinx/LaTeX
rendering + config fixes (all committed, all gates green). The one remaining piece is the
**full napoleon-Google rewrite of `base.py` + `gn.py`** — the maintainer chose "full Google"
(`Args:`/`Returns:`/`Raises:`/`Example:` on *every* method). That is fully specified below so it
can be executed cold.

## Current state (2026-09-26)

### Done and committed (`07fedcd`)
- **Coverage sweep.** `functions.py` (`ComposableFunction.__rmatmul__`, `_repr_latex_`;
  the other "missing" ones were `@overload` stubs, left bare); `nbplotutils.py` (module docstring
  + the public plotting helpers `generategridlines`/`create_graphs`/`create_basis`/
  `create_unit_circle`/`create_x_and_y`/`sine`/`draw_ndc`/`draw_screen`/`show_mult` + `_coef_as_float`).
  `transforms.py` was already 100% covered; `base.py`/`gn.py` coverage came from the merged sibling.
- **docutils rendering fixes** — the real 6 unbalanced `|`/`` ` `` in `base.py`
  (`magnitude`/`magnitude_squared`/`inverse`/`cosine`/`exp`/`normalize` + one `rotor_from_vectors`
  prose line + a stray `` ``Rational``s ``) and 2 in `measure.py` (a display equation made an RST
  literal block). Wrapped magnitude tokens in the `` `` `` code-role. `make docs` → **0** substitution warnings.
- **Config fixes** (see next section): ₙ glyph fixed, undefined hyperrefs 169 → ~7.
- **Gates green:** `make test` **649 passed**, `make docs` **exit 0**, `ruff check .` clean.

### Remaining
- **The full napoleon-Google rewrite of `base.py` + `gn.py`.** DONE 2026-09-26 (see below —
  every `MultiVectorBase` method + gn.py methods + the public module-level functions now carry
  Google `Args:`/`Returns:`/`Raises:`/`Example:`; 649 tests + 170 doctests green, deterministic,
  ruff clean on base/gn).
- **The grade-specialized generated docstrings (`CUSTOM_METHOD_DOCS` in `tools/gen_specialized.py`).**
  DONE 2026-09-26 at the maintainer's request ("did the google/napoleon work also cover the
  generated docstrings? … do it"). The base docstrings above are *copied* into generated methods
  that lack a specialized entry, so those are Google automatically; the ~185 hand-written
  `CUSTOM_METHOD_DOCS` entries (keyed `role|method`, roles scalar/vector/bivector/trivector/rotor/odd)
  + the 7 `_*_doc` callables were grade-specialized summary+doctest strings NOT in Google form —
  now all converted to Google style (`Args:`/`Returns:`/`Raises:`/`Yields:` + the doctest moved
  under `Example:`), mirroring the base.py treatment. Verified: regenerate + 163 g1/g2/g3 doctests
  pass, full `pytest` 649 pass, g2 & g3 byte-identical across two generations (determinism), ruff
  clean.  Param names in `Args:` match the generated signatures (rhs / other / lhs / r / n /
  blade_coef / onto / away_from / across / a,b / from_vector,to_vector / x); return-type tokens
  used only for grade-preserving ops, prose elsewhere (per the type wrinkle below).
  - **Note (not autodoc-rendered):** `book/docs/api.rst` automodules base/gn/functions/transforms/
    measure/vectorcalc/frame — NOT g1/g2/g3 — so these generated docstrings are read as *source*
    and run as *doctests*, not rendered by the book's autodoc. The value here is source-readability
    consistency + the executable per-grade examples, not autodoc type rendering.
  - **Type wrinkle:** for grade-*changing* ops (products, `dual`, `exp`, `outer_product`) the
    resolved return type varies by dimension/grade, so a single `Returns:` type token can be wrong.
    Follow the project convention (`tasks/reference/generated-docstrings.md`): put the type token in
    `Returns:` only where grade-preserving and certain (add/sub/neg/reverse of a closed-grade role);
    otherwise describe in prose and let the annotated-local in the `Example:` show the type.
  - **Verify:** `tools/gen_specialized.py` is E501-exempt, so no column pressure; regenerate +
    `pytest --doctest-modules src/gacalc/g1.py g2.py g3.py`, then `make test` / `make check-generated`.

## Config fixes — how and why (in case they need changing later)

Folded in 2026-09-26 (maintainer: "fold them in and figure out how to fix them"). All in
`book/docs/conf.py` and `book/docs/api.rst`:
- **ₙ (U+2099) glyph drop — FIXED, no new package.** FreeSerif (Sphinx's lualatex default main
  font) HAS the script-G 𝒢 but LACKS ₙ (lualatex logged `Missing character: ... ₙ`; it dropped
  from the PDF). Fix in `conf.py` `latex_elements['preamble']`: a **luaotfload fallback** to
  **DejaVu Sans** (already installed), referenced **by file** (`file:DejaVuSans.ttf:mode=harf;`)
  so it needs no luaotfload name database, with FreeSerif kept as the main face. `Missing character`
  count → 0. Dead ends learned: `newunicodechar` is NOT installed in the image; naming DejaVu
  **Serif/Mono** crashes the build (only DejaVu **Sans** is installed).
- **Undefined hyperrefs — 169 → ~7.** (1) `autodoc_typehints = "none"` — autodoc no longer turns
  every type annotation (the `V` TypeVar, the re-exported `ComposableFunction`/`InvertibleFunction`)
  into an unresolvable cross-ref; the types now live in the Google `Args:`/`Returns:` prose.
  (2) expanded `api.rst` to `automodule` ALL package modules (base/gn/functions/transforms/measure/
  vectorcalc/frame) so the explicit `:func:` refs resolve. The ~7 residual are a latexmk multi-pass
  convergence tail (labels ARE in `geometry2.aux`) — a clean rebuild resolves them; not a defect.
- **`scit` (small-caps-italic) shape warning — 42, cosmetic, left as-is.** FreeSerif lacks that
  shape so LaTeX auto-substitutes italic; no content lost. Silencing needs a fragile hardcoded
  `\DeclareFontShape` against fontspec's internal `FreeSerif(0)` name — not worth it.
- **Pre-existing gate failure — `book/docs/conf.py:120` E501 (89 > 88) — FIXED 2026-09-26.**
  The `\directlua{luaotfload.add_fallback(...)}` line (added by the ₙ-glyph fix, committed
  `07fedcd`) is 89 cols and `ruff check .` flagged it (only `entrypoint`/`tasks/adhoc` are
  excluded, not `book/`); the task's earlier "ruff clean" claim was inaccurate for this one line.
  **Decision:** added a `per-file-ignores` entry `"book/docs/conf.py" = ["E501"]` in
  `pyproject.toml`, with a reason comment. **Why this over the alternatives:** (a) an inline
  `# noqa: E501` is *impossible* — the line lives inside the `r"""..."""` LaTeX preamble string,
  so a `# noqa` would inject literal text into the preamble and break lualatex; (b) restructuring
  the `\directlua{...}` across two physical lines was rejected — it can't be verified without the
  heavy `BUILD_DOCS` lualatex build and risks the render for no real benefit. The `per-file-ignores`
  approach is zero render-risk and matches the existing `tools/gen_specialized.py` precedent (E501
  is not meaningful for un-reflowable string-literal content). `ruff check .` now passes
  repo-wide. base.py/gn.py stay E501-clean on their own.

## Session operational notes (cold-start context)

- **Git:** on branch `sphinxDocstringUpdates`; the above is committed at `07fedcd`. `base.py`/`gn.py`
  are clean — no Google edits yet. The sibling `generate-missing-docstrings.md` is COMPLETE and
  archived at `tasks/archive/2026/09/26/`.
- **`make docs`** builds HTML + PDF (lualatex), ~2–3 min, and needs an image built with
  `BUILD_DOCS=1` (the default). It's the authoritative render check. It re-executes notebooks; a
  *clean* build (`rm -rf book/docs/_build && make docs`) is slower but converges cross-refs.
- **Measuring warnings from the build log — gotchas:**
  - Undefined hyperrefs: `grep -c 'Hyper reference.*undefined'` **UNDERCOUNTS** (LaTeX wraps the
    warning across lines, so "undefined" often lands on the next line). Use
    `grep -oE "Hyper reference .api:[^' ]+"` to count real ones, or isolate the final latexmk pass
    (the log accumulates EVERY pass, so early-pass "undefined" is stale).
  - Substitution: `grep -ic 'start-string without end-string\|undefined substitution'`.
  - Missing glyph: `grep -c 'no ₙ'`.  Font shape: `grep -c 'scit.*undefined'`.
- **Cheap per-docstring RST check without a full build:**
  `docutils.core.publish_doctree(doc, settings_overrides={"warning_stream": ..., "report_level": 2})`.
  CAVEAT: `:func:`/`:meth:`/`:class:`/`:attr:` "unknown interpreted text role" errors there are
  **FALSE POSITIVES** — Sphinx defines those roles, bare docutils doesn't. Only "start-string
  without end-string" and "undefined substitution" are real syntax problems.
- **Fonts in the image:** FreeSerif (main; has 𝒢, lacks ₙ and the scit shape); DejaVu **Sans**
  installed (`/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf`); DejaVu Serif/Mono NOT installed;
  `newunicodechar` package NOT installed; no STIX.
- **Instrumentation lesson:** build the docs FIRST and read the actual warnings — the task's
  original prediction of ~12 `|A|` "undefined substitution" warnings was mostly moot (most `|A|`
  are inside `` `` `` code-spans or `::` literal blocks that RST doesn't parse).

## Full napoleon-Google rewrite — execution spec (COLD-START READY, not started)

**Decision (maintainer, 2026-09-26): FULL Google — `Args:` / `Returns:` (and `Raises:` /
`Example:` where they apply) on EVERY documented method, including trivial ones** like `zero()` /
`reverse()`. Not the value-driven subset. Example shape:

```
def zero(cls) -> Self:
    """The additive identity 0.

    Returns:
        Self: the multivector with every coefficient zero.
    """
```

**Scope:** every method of `MultiVectorBase` in `src/gacalc/base.py` (~70 — constructors,
operators, products, grade ops, predicates, magnitude/inverse/dual/reverse, project/reject/reflect,
the measure pass-throughs, rotor/exp/sandwich/isclose/repr) AND every method of
`Gn`/`BladeDictionaryEntry` in `src/gacalc/gn.py`. (`functions.py`/`transforms.py`/`nbplotutils.py`
may be normalized too if time allows, but base/gn is the mandate.) Suggested batch order:
constructors → operators → products/grades → predicates → magnitude/inverse/dual/reverse →
project/reject/reflect → measure pass-throughs → rotor/exp/sandwich → `gn.py`. Verify after each.

**How to write each one:**
- Keep the existing Hestenes prose + `from Hestenes and Sobczyk ... page/equation` citations as the
  summary line + extended description; then add the Google sections.
- `self`/`cls` are NOT in `Args:` (Google convention). Document the remaining params with types.
- `Returns:` names the type + what it is. `Raises:` where the method raises (e.g. `i`/`inverse` on
  parallel/zero, `exp` on a positive-square vector). Move any EXISTING doctest under `Example:`.
- **napoleon is already enabled** (`conf.py` → `sphinx.ext.napoleon`) and `autodoc_typehints =
  "none"`, so the types you write in `Args:`/`Returns:` ARE the rendered type info — get them right.

**Conventions this pass MUST follow** (see `tasks/reference/generated-docstrings.md`):
- Explicit unit coefficients in any example (`1 * Vector.e_1`; bare only for *direction* args).
- Typed comparisons in doctests, never bare numbers (`== Scalar.from_scalar(-1)`; a multivector
  never `==` a bare int — see `tasks/reference/symbolic-equality.md`).
- `base.py`/`gn.py` are E501-gated (≤ 88 cols) — wrap the field-list lines.

**Verification (after each batch):**
- `PYTHONPATH=src python3 -m pytest --doctest-modules src/gacalc/base.py src/gacalc/gn.py -q`
  (fast host check of any `Example:` doctests).
- `make test` — **base.py/gn.py docstrings are COPIED into the generated `g*.py`** via the
  generator's `inspect.getdoc` copy path, so regeneration + the full doctest suite (649) must stay
  green; `make check-generated` (determinism) too.
- `make docs` — stays exit 0, **0** substitution warnings.
- `ruff check .` clean.

**At completion:** harvest the durable book-pipeline facts above (font list, warning-measurement
gotchas, the config knobs) into `tasks/reference/book-and-docs-pipeline.md`, then archive this task.

## Voice & invariants (apply while editing)

- Preserve the Unicode + LaTeX-ish math notation and the house rule that a rotation reads as an
  *explicit* rotation (`plane_rotation` / rotor vocabulary in `CLAUDE.md`).
- The generated `g1`/`g2`/`g3` are build artifacts — never hand-edit; improve docstrings at the
  `base.py`/`gn.py` source and regenerate.

## See also

- `tasks/reference/generated-docstrings.md` — the generated-docstring mechanism + the doctest
  conventions this pass must follow.
- `tasks/reference/symbolic-equality.md` — the "multivector never `==` a bare number" gotcha.
- `tasks/reference/book-and-docs-pipeline.md` — the Sphinx build mechanics (harvest target).
- `tasks/reference/code-generator-architecture.md` — the base→generated docstring copy path.
- `tasks/archive/2026/09/26/generate-missing-docstrings.md` — the completed sibling (coverage).
- `tasks/narrate-code-generator-in-docstrings.md` — the generator's own narrative (separate task).
