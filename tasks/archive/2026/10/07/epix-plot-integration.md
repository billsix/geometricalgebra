# Import epix-mirror at container build time for plot generation

**Created:** 2026-06-13 · **Completed:** 2026-10-07 (archived on the maintainer's say-so: "looks great both in HTML and PDF" … "6) yes")

At container build time the gacalc image pulls the maintainer's **epix-mirror**
(`https://github.com/billsix/epix-mirror`, a mirror of ePiX, a C++ library producing LaTeX-quality
mathematical figures) and builds/installs it, so it is available as the book's figure tool. The image
integration landed 2026-10-06; the Python front-end and all nine rotation figures landed 2026-10-07.
The follow-on figure work is `tasks/archive/2026/10/07/book-epix-figures.md`. The task moved here
from modelviewprojection (this is gacalc's epix import; mvp's plotting is a separate concern and got no
epix task).

## Decisions

- **URL** (2026-10-04): `https://github.com/billsix/epix-mirror`.
- **Pin** (William Emerison Six <billsix@gmail.com>, 2026-10-06): epix-mirror commit
  `ebf3ca607ae6c1d4fa307e8b0359960d875d219c` (epix-mirror's GitHub `master` as of 2026-10-06, the merge
  of its `containerFileRework` branch), held in the Dockerfile's `EPIX_COMMIT` ARG.
- **Fetch with git**, the maintainer's choice over a tarball.
- **Coexist, not replace** (William Emerison Six <billsix@gmail.com>, 2026-10-06): `nbplotutils.py`
  (matplotlib) stays for the interactive notebooks; ePiX is the book's LaTeX-native figure source (PDF
  for LuaLaTeX, PNG for HTML).
- **Figures in Python, not `.xp`** (the maintainer, 2026-10-07), with the `epix` package.
- **Two figure-file rules** (the maintainer, 2026-10-07), carried into the follow-on umbrella: every
  argument by keyword (`tools/check_epix_keywords.py`, a `make format` gate step) and every binding typed
  (`fig: PendingFigure`).
- This was a permanent build-file change (a real plot dependency), made with the maintainer's go-ahead.
- The original ask to keep the integration usable from both the Sphinx build and a possible future LaTeX
  port stayed a design constraint only; no LaTeX port was built.

## What was done

- **The build, learned from the pushed epix-mirror tree** (`ebf3ca6`): Meson, `meson setup build
  --prefix=/usr/local && meson install -C build`, installing `epix`/`elaps`/`flix`/`laps` + `libepix.a` +
  headers + man pages + samples. Runtime needs: `g++` (the `epix` driver compiles each `.xp`), `bash`,
  `latex`, `ps2epsi`; `gs` for eps→png, ImageMagick for animations. That push also made the epix-side dnf
  lists host-runnable (`entrypoint/01-install-base.sh`/`02-install-render.sh`), added `MINIMAL_IMAGE`
  flags, a lazily-rasterizing Python `Figure` (building a figure needs only `libepix`; PNG needs TeX +
  `gs`), and a warning-free `-Wall -Wextra -Wpedantic` build with a `Complex::operator!=` recursion fix.
- **Dockerfile** (2026-10-06): behind `USE_EPIX` (`?= $(if $(filter 1,$(MINIMAL_IMAGE)),0,1)` in the
  Makefile, `ARG USE_EPIX=0` + `ARG EPIX_COMMIT` in the Dockerfile). `entrypoint/install-epix.sh` does a
  shallow `git fetch --depth 1 origin $EPIX_COMMIT` + detached checkout, `meson setup`/`meson install`
  into `/usr/local`, removes the build dir and `.git`, keeps the source at `/opt/epix-src`.
  `entrypoint/06-install-epix.sh` installs git, meson/ninja/g++/binutils, ghostscript, ImageMagick and
  the TeX set epix's own `02-install-render.sh` names (the overlap with `03-install-notebook-tex.sh` is a
  dnf no-op, listed in full so an epix-only image has `latex`). The layer sits before `COPY src` for
  cache ordering; everything lands in committed layers and runs offline. `install-lean.sh`'s no-git note
  was widened.
- **Python front-end** (2026-10-07): `install-epix.sh` also builds the nanobind extension via
  epix-mirror's `build_py.sh` (so the tree is fetched to `/epix`) and installs `epix` editable into
  `/venv` (`python3-devel` added for `Python.h`). The maintainer's host build then failed on `import
  epix` from the Dockerfile's cwd `/`, where the bare `/epix` directory shadowed the package as a
  namespace package; fixed by moving the tree to `/opt/epix-src` before the editable install.
- **First figure**: `book/figures/epix/rotate_goal.py` (jupytext percent) rebuilt `rotate-goal`;
  `tools/render_epix_figures.py` (one fresh process per figure) writes `_static/epix/rotate-goal.{pdf,png}`
  from `docs.sh`; `rotate.rst` + `proof-rotate.rst` reference `_static/epix/rotate-goal.*`.
- **The remaining eight** (maintainer: "do that for the remaining svgs"): `rotate1.py`–`rotate8.py` share
  `_rotation_scene.py` (β, θ, r, disc + axes, `vector`/`wedge`/`right_angle_marker`/`leg`) so the
  sequence agrees with the goal figure and ends on `r(a;θ)`. Dark mode (maintainer's report): the
  `pngalpha` PNGs were transparent, so each figure defines `BACKGROUND = "#f2f2f2"` (the disc fill) and
  the renderer flattens the HTML PNGs onto it with ImageMagick. Gotcha: `epix.label_angle` takes radians.
  The nine CC0 SVGs under `_static/cc0/williamesix/` were `git rm`'d (the maintainer's choice); the
  Stephan Kulla unit-circle SVG stayed (not ours to redraw).
- The two figure-file rules were applied to all ten figure files; the eepic oracle was byte-identical.
- **Docs:** `CLAUDE.md` ("ePiX in the image" + the lean-image flag list); the README's container-build
  section with the flag table; `tasks/reference/book-and-docs-pipeline.md` ("ePiX figures": `make docs`
  renders them, `python tools/render_epix_figures.py [NAME]` renders one by hand).

## Verification (2026-10-06, nested in the runClaudeInContainer sandbox)

| Check | Result |
| --- | --- |
| `make image USE_LEAN=0 USE_EMACS=0` (ePiX on; Lean/Emacs trimmed — the diff touches neither) | built; the ePiX layer logged `epix-mirror at ebf3ca607ae6c1d4fa307e8b0359960d875d219c` (epix-mirror commit) and Meson installed 194 files under `/usr/local` |
| tools present | `epix`/`elaps`/`flix`/`laps` on PATH, `libepix.a` + `epix.h` installed, source at `/opt/epix-src` with `.git` removed |
| render `samples/hello.xp` in the image | `epix` → eepic; `elaps --pdf` → `hello.pdf` (4.6 KB) through latex → dvips → ps2epsi → epstopdf |
| gacalc gate (`make test`'s run line) | **696 passed** |
| `make image MINIMAL_IMAGE=1` (flag-off permutation) | built, 2.47 GB; `epix`, `git` and `meson` all absent — the `USE_EPIX` gate holds. The ePiX-enabled image (Lean/Emacs still off) is 3.96 GB |

The 2026-10-07 HTML and PDF were approved by the maintainer at archive.
