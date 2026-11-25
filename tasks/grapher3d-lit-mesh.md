# 3D grapher: lit triangle-mesh surface (Blinn-Phong, the half-vector model) (done)

**Started:** 2026-11-03 in github.com/billsix/modelviewprojection, as `tasks/graphing-calculator-3d-lit-mesh.md`; moved to gacalc on 2026-11-13. **Done:** 2026-11-25.

The 3D height-field grapher drew a wireframe and a height-coloured, unlit solid. The maintainer asked for a lit solid with the Blinn-Phong half-vector model (not Phong's reflection vector), with a specular highlight that follows the light and the view.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-25)

1. Normals are analytic, from `∂f/∂x` and `∂f/∂y` of the authored function. The maintainer asked why the example surfaces carried hard-coded gradients and suggested sympy at runtime; that replaced the first design (an optional `gradient` field on `Surface`): sympy differentiates `fn` once on symbols.
2. One directional light.
3. Light direction and shininess are menubar sliders.

## Result

- **`src/gacalc/gl/grapher3d.py`:** `surface_gradient` (sympy derivatives of `fn`; central differences when `fn` cannot take symbols or the derivative is undefined, as at a cone's tip), `surface_normal` (the cross product of the two tangents, with `gacalc.g3`), `build_normals` (one normal per vertex of `build_solid`, same order, via the shared `_triangle_corners`), `light_vector`; `View3D` gains `lit`, `light_azimuth`, `light_elevation`, `shininess` (default 64); the Light menu has three sliders, `T` and Controls ▸ Lighting toggle lighting, and the wireframe toggle was already there. `Surface.fn` is typed `Callable[[Real, Real], Real]`.
- **Shaders** `src/gacalc/gl/lit_surface.vert` / `lit_surface.frag`: per-fragment Blinn-Phong in view space (`H = normalize(L + V)`, `pow(max(0, dot(N, H)), shininess)`, ambient 0.18), two-sided (the normal is flipped toward the eye). Ported the SuperBible v4 `chapt17/lighting` per-fragment math, with explicit `uniform` and `in` instead of the legacy built-ins.
- **`examples/grapher3d.py`:** the three surfaces no longer cast to `float`, so sympy can differentiate them.
- **Verification:** `make test` (1411 passed; the one failure, the `gacalc.gl` doctest listing the shared `.vert` files, was fixed by adding `lit_surface.vert`); doctests (8 in `grapher3d.py`) pass; `ty` is clean on the changed files; rendered headless (Xvfb, `glReadPixels`) the cone, saddle and plane: highlights follow the light and the lit and unlit solids differ. The plane (index 1) is exactly edge-on at the default camera and draws nothing in either mode, as before. Not done: an interactive run on a real display (the Light sliders, `T`).
- **Reusable harness:** `tools/grapher3d_render_probe.py` (promoted from the task's ad-hoc script), noted in `tasks/reference/gl-toolkit.md`, which also describes the lit solid.
- **Found, not caused:** `make format` fails on ten E501s and a `T201` in `tools/check_lean_arch_doc_names.py` (already on `master`); ruff also reformats that file when it runs. I reverted the reformat and did not touch the file.
