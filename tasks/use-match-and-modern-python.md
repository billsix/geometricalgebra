# Use match statements and modern Python features where appropriate

**Status:** in-progress
**Started:** 2026-06-05

## Goal

Study the codebase and find places where the code would read better or be more robust with modern
Python: (1) replace `if/elif/else` chains with structural-pattern-matching `match` statements where
it's a genuine improvement (not just churn) — the code already uses `match` in a few spots
(`Gn.decrease_grade`, `__mul__`/`__rmul__`, `reject`/`reflect`), so this extends that established
style; and (2) identify where other newer language features could help readability or correctness.
Produce a concrete, reviewable list of candidate sites first (per repo convention: investigate and
report before editing), each with a before/after sketch and a recommendation, so changes can be
approved individually rather than applied blanket.

## Plan

- [ ] Inventory `if/elif/else` chains across `src/` (base.py, gn.py, transforms.py, nbplotutils.py)
      and the generator (`tools/gen_specialized.py`); flag the ones that dispatch on type/shape/value
      (good `match` candidates) vs. simple boolean guards (leave alone).
- [ ] For each candidate, sketch the `match` rewrite and judge: clearer? same behavior? worth it?
- [ ] Survey for other modern-Python opportunities (see Notes for the menu) — list sites, don't apply.
- [ ] Present the findings as a per-item list for go-ahead. Apply only what's approved.
- [ ] After any edits: `ruff check`, `ty check src`, full suite (124) green; re-run the generator if
      `tools/gen_specialized.py` changes (it auto-formats its output).

## Notes / decisions

- Confirm the project's Python floor before recommending version-gated features. `requirements.txt`
  pins recent deps and the dev container runs Python 3.14, but `pyproject.toml` declares no
  `requires-python` — worth pinning as part of this.
- Candidate modern features to evaluate (only where they genuinely help):
  - structural `match` for type/shape dispatch (the core of this task)
  - `X | Y` union / `T | None` type syntax (already used in places — make consistent)
  - `@dataclass(slots=True)` / `kw_only` for the multivector dataclasses
  - `typing.Self` (already used), `assert_never` for exhaustive match `case _:` arms
  - `itertools`/`functools` niceties, `enum` where integer/string constants are used as tags
  - f-string `=` debugging, `tomllib`, structural improvements in comprehensions
- Keep the pedagogical, textbook-faithful style — don't sacrifice legibility for cleverness.
- `g1/g2/g3.py` are generated: any `match`/feature change there must be made in the generator, not
  the output.

## Open questions

- What minimum Python version may we target? (Decides which features are on the table — e.g.
  `match` needs 3.10, `assert_never` 3.11, etc.)
- Appetite: a focused sweep of the few clear wins, or a thorough modernization pass?
