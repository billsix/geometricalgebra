# Guards report the caller from the Python frame instead of a `context` string

**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>) · **Done:** 2026-11-10

`MultiVectorBase.require_vector(value)`, `require_vectors(values)` and `frame.require_frame(vectors,
float_close_to_zero=False)` lost their `context` string. Each message now names the calling function
and its call site, e.g. `make_orthogonal_frame (frame.py:230) requires a frame …`, read from the
Python stack by `base.describe_caller()`.

- **Mechanism.** `describe_caller()` starts at `sys._getframe(1)` and walks up past every frame whose
  code object is registered by the `@validation_guard` decorator, so `require_frame` →
  `require_vectors` → `require_vector` still names the real caller. It runs only when a guard is about
  to raise, so a passing check costs nothing; `inspect.stack()` was rejected because it reads source
  files on every call.
- **Decision** (William Emerison Six <billsix@gmail.com>, 2026-11-10, "whatever you recommend"): drop
  the parameter entirely, with no optional override. Closures are named by their qualified name, e.g.
  `Frame.to_invertible_function.<locals>.forward` where the old message said "a frame's map".
- **Call sites:** 30, in `base.py`, `frame.py`, `measure.py`, `nbplotutils.py`, `standardposition.py`,
  `transforms.py`, `vectorcalc.py`. The generator emits none. The doctests show the guard inside a
  small function (`double`, `total`, `first_of_frame`), so the message visibly names it.
  `tests/test_frame.py` matches the `name (file:line)` form.
- **Docs:** project `CLAUDE.md` (the guard convention) and the `[Unreleased]` CHANGELOG entries, edited
  in place because the guards were never released.
- **Gate:** host `ruff check`, `ruff format --check`, `ty check src tests tools` clean; host
  `pytest -m "not slow"` 782 passed. The containerized `make format` + `make test` gate ran once for the
  whole 2026-11-10 batch, after its last task.
