# Fix label placement / overlap in the ePiX book figures

**Status:** done — 2026-10-08 (per-figure pixel tuning; gates green; normalized pre-squash)
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

Several of the book's ePiX-generated figures had labels that overlapped or sat in the wrong place —
not beside the item they named. The worst cases: `proj3` drew the identity `a = proj_b a + rej_b a`
along the blue **projection** segment (so it read as the projection's label, not a statement about
`a`); the 3D `proj3d-e31` had its `proj` and `rej` labels overlapping outright (their segments are
near-collinear in the projection); `proj3d-e12`/`-e23` crowded the proj/rej/axis labels; and
`proj2`/`sp5` collided `b` with the `proj_b a` label near `b`'s head. All were fixed by **label
placement only** (adjusting each `epix.label` / `vector(...)` call's `at`/`offset`/`align`) — no
geometry, scene, or color changed — verified figure-by-figure with the render→view loop, and `make
format` + `make docs` green.

## What was done

Per-figure pixel tuning (the maintainer's choice — no shared helper), each change verified by rendering
the single figure (`tools/render_epix_figures.py <name>` → view `book/docs/_static/epix/<name>.png`,
run via the image's own `podman run`, not a rebuilding `make` target) and viewing the PNG. The 18
untouched figures are byte-identical (no regression). Every call stayed keyword-only and every binding
typed, so the `check_epix_keywords` gate passed unchanged.

- **`proj3`** — the `a = proj + rej` identity is now the **label of the `a` vector itself** (moved into
  the `vector(head=A, …)` call, offset up-left above the `a` head) instead of a separate `epix.label`
  at the projection midpoint; it no longer reads as the projection's label.
- **`proj2`, `sp5`** — `\vec b` pushed up-right (`align=l`) and `proj_{\vec b}\,\vec a` pushed down-left
  (`align=r`), so they no longer collide near `b`'s head.
- **`sp4`** — `a'_x` nudged left, `\vec b'` nudged right, apart below the x-axis.
- **`proj3d-e12`** — `rej_{e12}` moved out beside its green segment (`offset=(18,-6)`); the `e_{12}`
  subscript now renders fully (it had only looked clipped because of the overlap, not a text bug).
- **`proj3d-e23`** — `\vec a`/`proj`/`rej` spread into a readable stack (proj up-left, rej down-right,
  `a` at the head).
- **`proj3d-e31`** (worst) — `rej` pushed above-right, `proj` pushed below the blue line
  (`offset=(-10,-20)`) clear of the black `a` vector, `\vec a` up-right; all three now read separately.
  (Took two extra render→view nudges: an earlier `proj` offset crossed the black vector first.)

The clean figures left untouched: `add1`–`3`, `sub1`–`2`, `rotate1`–`8`, `rotate-goal`, `proj1`,
`sp1`–`3`.

## Decisions

1. **Per-figure pixel tuning, not a shared helper** (maintainer, 2026-10-08) — resolved the task's one
   open question; the count was small enough that per-figure `(at, offset, align)` offsets were simpler
   than a `segment_label` abstraction.
2. **Placement only** — no geometry/scene/color/background change (the dark-mode `BACKGROUND` flatten
   stays intact).

## History (commit chronology, `origin/master..HEAD` — for the maintainer's squash)

1. `03443f8` *added task to fix epix labels* — filed this task (then proposed) with the visual audit
   and defect checklist.
2. `8e955f5` *updated figures* — the seven label-placement fixes above; `make format` + `make docs`
   green.
3. `d596b09` *archived* — moved the task doc to `tasks/archive/2026/10/08/`.

## Related

- `tasks/reference/book-and-docs-pipeline.md` — the ePiX figure pipeline (render tool, label API,
  keyword/type gate). The durable "how it works" lives here, not in this record.
- `tasks/reference/book-outline.md` — figure/notation conventions (θ default, from→to naming).
- `tasks/archive/2026/10/07/book-epix-figures*.md` — the umbrella/steps that created these figures.
