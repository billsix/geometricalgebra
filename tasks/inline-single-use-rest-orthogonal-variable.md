# Inline the single-use `rest_orthogonal_to_v` in `make_orthogonal_frame`

**Status:** done — 2026-10-29. William Emerison Six <billsix@gmail.com> asked for the inline directly.
Work commit subject: "frame: inline the single-use rest_orthogonal_to_v in make_orthogonal_frame".
**Priority:** 5  (readability)
**Difficulty:** 2  (one local variable, one function)
**Created:** 2026-10-29 (William Emerison Six <billsix@gmail.com>)

## BLUF

In `make_orthogonal_frame`'s inner `orthogonalize` recursion (`src/gacalc/frame.py`), the `[v, *rest]`
case bound a local `rest_orthogonal_to_v` and used it **once**, immediately, as the argument to the
recursive call. A single-use variable defined and consumed on the very next line should be inlined
and used as a value, so it was inlined. Behaviour unchanged (Modified Gram-Schmidt by rejection);
the suite stays green.

## What was done

The `[v, *rest]` case now passes the rejected-rest comprehension straight to the recursive call:

```python
return [v, *orthogonalize([w.rejected_away_from(v) for w in rest])]
```

(ruff wraps the list literal across lines.) The per-case operation-first comment — already reworked
in `tasks/archive/2026/10/27/orthogonal-frame-recursion-structure-and-comment.md` — was kept as is;
only the intermediate binding went away.

**Discretion note:** the name `rest_orthogonal_to_v` had documented what the comprehension produces,
the one sanctioned reason to keep such a binding. The maintainer asked to inline it, so the default
(inline) was taken; the recursive call reads clearly without the name.

## Verification

- `python -m pytest` — **690 passed** (`test_frame.py` among them).
- `ruff` + `ty` clean (via `entrypoint/format.sh`).

## Follow-on — convention-doc update (pending the maintainer's satisfaction check)

Record in the **Python coding standard** reference doc in **both** `runClaudeInContainer` and
`runCrushInContainer` (canonical `tasks/reference/python-coding-standard.md` + byte-identical mirror):
a **single-use local variable, defined and then used immediately**, should by default be **inlined
and used as a value**; exceptions are allowed when the name genuinely serves a purpose (documents a
non-obvious intermediate, or is reused) — discretion, defaulting to inline. Deferred to the single
cross-repo pass after the four Gn/frame tasks land, per the maintainer's "update docs once I'm
satisfied" framing (shared with the sibling tasks).
