# Refactor `Frame.to_invertible_function`: inline single-use locals, narrow scopes, name the implied dimension

**Completed:** 2026-11-06. Requested by William Emerison Six <billsix@gmail.com>; implemented on
branch `refactor-frame-to-invertible-function`.

## What was done

`Frame.to_invertible_function` (`src/gacalc/frame.py`) was reshaped with no change in behaviour, and the
naming and scoping rules that came out of the review were written into the shared cross-project
standards. The before/after code and what each change illustrates are in
`tasks/reference/python-coding-standard-gacalc.md` ("Inline once, declare at use, nest and shadow").

- **New public method `MultiVectorBase.implied_minimal_number_of_dimensions()`** (`base.py`): the
  highest basis index a vector uses (0 for the zero vector), raising `ValueError` on a non-vector. It
  replaced the opaque `max(max(blade) …)` in the frame code, the private `measure._max_basis_index`
  (deleted), and that helper's cross-module import in `vectorcalc.cross`. `CHANGELOG.md`
  `[Unreleased]` "Added" entry.
- **The method body:** `n` comes from `getattr(type(self.vectors[0]), "DIMENSION", <implied
  dimension>)`, which replaced the `cls` and `dimension` locals and the ternary. `measure.signed_content`
  was given the same form. `k` and the `frame_vectors` alias were inlined. `pairs` was inlined into the
  `peel(...)` call with a comment naming it. `peel` was nested inside `backward`, its only caller. The
  class locals in `forward`/`backward` were renamed `basis` → `cls` (gacalc's naming rule). In
  `vectorcalc.cross` the implied dimension is computed once, inside the `Gn`-only branch that uses it.
- **Gates:** containerized `make test` (718 passed) and `make format` (ruff + ty, no changes) on a lean
  `MINIMAL_IMAGE=1` image; `tools/check_annotations.py` unchanged by this work (43 findings before and
  after). The nested `make image` needed `podman build --network=host` passed by hand for that one build
  (the nested build's RUN steps fell back to pasta and could not open the network namespace); the
  Makefile was not changed.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-06)

1. A local bound once and used once is inlined, even when the name was there for readability. A comment
   above the inlined subexpression describes it and gives it its name.
2. A declaration goes where it is used, not earlier.
3. A helper used by only one function is nested inside that function. Nesting costs one function object
   per call of the caller; there was no performance or correctness reason to keep `peel` outside.
4. The opaque dimension expression became a named method, `implied_minimal_number_of_dimensions`
   (the maintainer's name), an instance method on `MultiVectorBase` that checks its input is a vector.
5. No shared "`DIMENSION` else implied" helper (left to the agent's discretion): `vectorcalc.cross` uses
   the two halves differently, so each caller keeps its own short check.
6. "Used twice" does not by itself earn a name. `dimension` (used only as "value or fallback") was
   absorbed by `getattr`'s default; `k` was inlined because `len(self.vectors)` is cheap to repeat. `n`
   was reviewed and kept: its second use is the error message, and the alternatives were dropping it from
   the message (losing information) or writing its three-line expression twice.
7. A nested helper's parameter deliberately shadows the caller's same-meaning variable, and the
   shadowing must be verified. `peel`'s `y` shadows `backward`'s `y`; `peel` reads only its own `y`,
   and its other names bind nothing in the enclosing scopes.
8. The rules are portable, so they went into the shared layer, not the personal overlay.

## Knowledge extracted to the shared layer (in both sandbox repos)

- github.com/billsix/runClaudeInContainer:
  - github.com/billsix/runClaudeInContainer `tasks/reference/python-coding-standard.md`: the
    inline-once section rewritten around decisions 1, 2 and 6; two bullets for decisions 3 and 7.
  - github.com/billsix/runClaudeInContainer `tasks/reference/code-style-conventions.md`: a new
    language-agnostic section "Names: inline what is used once, declare at the point of use, nest and
    shadow".
  - the shared `CLAUDE.md` (`entrypoint/dotfiles/.claude/CLAUDE.md`): a "Names" paragraph and the
    doc's read trigger.
- github.com/billsix/runCrushInContainer: both copies of `python-coding-standard.md` re-copied
  byte-identical from the canonical (the baked crush-client copy had also been missing the
  pin-dependencies section), and a "Names" bullet in the crush `CLAUDE.md` "Code conventions" section.

## Follow-ons

- `tasks/archive/2026/11/06/reuse-existing-vector-check.md` — one shared vector check; it replaced the
  nested `require_vector` this task kept and the check inside the new method.
- `tasks/frame-inverse-head-first-recursion.md` — whether `peel` can run first-element-first; it waited
  on `tasks/archive/2026/11/07/reciprocal-frame-hestenes.md`, which was done 2026-11-07.
