# Refresh CLAUDE.md to match the current code (stale "Known issues" + nits)

**Status:** complete
**Completed:** 2026-06-06
**Started:** 2026-06-06

## Goal

`CLAUDE.md`'s "Assessment / known issues" section (and a couple of other spots) describes bugs that
have since been **fixed in the code**, so the contributor doc overstates the open-issue count and
contradicts itself in places. Bring CLAUDE.md back in sync with `base.py` / `gn.py` / `transforms.py`
/ `pytest.ini` as they actually are on 2026-06-06, and fix the one genuine residual typo the audit
turned up. This is a documentation-accuracy pass — **no behavior change** except the single typo fix.

## Why

A stale known-issues list is actively misleading: a newcomer (or a future session) will go hunting
for bugs that are already gone, or trust a "latent bug" warning that no longer applies. Two of the
stale entries (#3 reject/reflect, #4 `__rmul__`) are flagged as *correctness* concerns, so leaving
them listed implies the library is buggier than it is.

## Findings (verified 2026-06-06 against the working tree)

Each known-issue number below is from CLAUDE.md's current "Open issues" list.

- **#2 — `InvertibleFunction` doctests "broken/misleading … would fail under `--doctest-modules`
  (not enabled)". → STALE, remove.**
  - `pytest.ini` now sets `addopts = --doctest-modules --ignore=…/nbplotutils.py` and
    `testpaths = src tests`, so doctest-modules **is** enabled.
  - The doctests in `transforms.py` (`InvertibleFunction.__call__`, `__matmul__`, `inverse`,
    `compose`, `compose_intermediate_fns*`) now import from `geometricalgebra.transforms` with plain
    lambdas — no `modelviewprojection.mathutils` import, no nonexistent `Vector2D`/`Vector1D`.
  - `python -m pytest -q` → **141 passed**, doctests included.
  - The "(not enabled)" parenthetical also **contradicts** CLAUDE.md's own Module-layout line
    ("~141 tests (incl. doctests via `--doctest-modules`)").

- **#3 — latent bug in `reject`/`reflect` sequence handling (`cls.outer_product(*sequence)`). →
  FIXED, remove.** `base.py` now matches `case [*sequence]: return cls.reject(
  cls.outer_product_of_vectors(*sequence))` (and likewise for `reflect`) — the static, any-arity
  reduce, not the 2-arg instance method. (`base.py` ~lines 502–514 / 533–545.)

- **#4 — suspicious `__rmul__` negation (`-self._geometric_product(lhs)`). → FIXED, remove.**
  `__rmul__` now returns `NotImplemented` in the fall-through, with a comment explaining the old code
  was dead and wrongly negated (`base.py` ~lines 146–157).

- **#8 (minor) — typo/fragility cluster. → MOSTLY FIXED; trim to the one survivor.**
  - `excuted` / `sortedBladeDictionyEntriy` in `gn.py`'s `decrease_grade`: **gone** (clean
    `sorted_blade_dictionary_entry` names).
  - malformed `\\frac` in `scale_non_uniform_2d` LaTeX: **gone** — `scale_non_uniform` emits correct
    `rf"\frac{{1}}{{{m}}}"` (`transforms.py` ~line 305).
  - `_repr_latex_` `sympify(str(x))` round-trip: **gone** — now renders straight from the sympy/number
    object (`base.py` ~lines 625–644).
  - test copy-paste bug `i15` using `unit_pseudoscalar(14)`: **gone** — `test_multivector.py:345`
    uses `unit_pseudoscalar(15)`.
  - **Survivor:** `base.py:410` docstring of `inverse` reads "**Note** sure if I'm doing it
    correctly" (should be "Not sure"). This is the one real residual; fold it into the code edit
    below (it also relates to #6's self-flagged-uncertainty list).

- **Still genuinely open (leave as-is, they're accurate):** #5 fixed Euclidean signature; #6
  self-flagged uncertainty in `inverse` / `is_parallel_to` / `component` (the "not sure" /
  "Note sure" comments at `base.py:360` and `:410` are still present); the still-open half of #7
  (`format.sh` walks the whole repo).

### Other CLAUDE.md inaccuracies found in the same audit

- **Internal inconsistency — "`InvertibleFunction` (in `gn.py`)".** The Architecture → Transforms
  subsection (and a Future-directions mention) say the transform layer is in `gn.py`. It actually
  lives in **`transforms.py`** and is *re-exported* from `gn.py`; the Module-layout section already
  says this correctly. Make the two agree (point at `transforms.py`, note the re-export).

- **Dev-workflow understates the test config.** CLAUDE.md says only "`pytest.ini` sets
  `pythonpath = src`." It now also sets `testpaths = src tests` and `addopts = --doctest-modules
  --ignore=…/nbplotutils.py`. Worth a sentence, since doctests are now part of the fast suite (so
  e.g. a broken example in `transforms.py` fails CI).

- **Stale date stamp.** The section header is "Assessment / known issues (updated 2026-06-04)";
  bump it when this edit lands.

## Plan

- [ ] **CLAUDE.md "Open issues" list:** delete #2, #3, #4; rewrite #8 down to the single remaining
      `base.py:410` typo (or drop #8 entirely once the typo is fixed and just mention it in the commit).
      Renumber or leave gaps — author's call (gaps preserve the "issue #5/#6" references elsewhere).
- [ ] **CLAUDE.md consistency:** fix the "`InvertibleFunction` (in `gn.py`)" spots to say
      `transforms.py` (re-exported from `gn.py`).
- [ ] **CLAUDE.md Dev workflow:** note `testpaths` + `--doctest-modules` (and the `nbplotutils`
      ignore + why: it imports a GUI backend that fails headless).
- [ ] **CLAUDE.md header:** update "(updated 2026-06-04)" → today.
- [ ] **One code edit:** `base.py:410` "Note sure" → "Not sure" (keep the self-flag; just fix the
      typo). This is the only non-doc change in this task.
- [ ] Re-run `python -m pytest -q` (expect 141) and `entrypoint/format.sh` (ruff + ty clean) — the
      doc edits won't affect it, but the `base.py` docstring touch should be linted.

## Notes / decisions

- Coordinate with `tasks/document-rotor-methods.md`: that task *adds* new CLAUDE.md content
  (the `rotate` / `rotor_from_vectors` methods); this one *removes* stale content. They edit the same
  file in nearby sections — do them in one sitting (or back-to-back) to avoid a churn conflict.
- The `base.py:410` typo also appears in `tasks/clarify-2d-only-transforms.md`'s orbit only loosely;
  it's cleanest to fix it here as part of #8 cleanup.
- Keep CLAUDE.md's voice and structure; this is surgical, not a rewrite.

## Open questions

- Renumber the "Open issues" list after deletions, or leave numbered gaps so existing cross-references
  ("issue #5", "#6") in code comments / other task files don't break?
- Drop #8's heading entirely once empty, or keep a one-line "minor typos: none outstanding" marker?
