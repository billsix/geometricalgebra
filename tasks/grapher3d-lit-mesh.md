# 3D grapher: lit triangle-mesh surface (Blinn-Phong, the half-vector model)

**Status:** proposed, needs go-ahead and the three open questions answered. The grapher move it
waited for is done (2026-11-13), so the 3D grapher is now `src/gacalc/gl/grapher3d.py`.
**Priority:** 7
**Difficulty:** 6
**Started:** 2026-11-03 in github.com/billsix/modelviewprojection (mvp), as
`tasks/graphing-calculator-3d-lit-mesh.md`. Moved to gacalc on 2026-11-13, so that the triangulation
and normals are written in gacalc from the start.
**Depends on:** `tasks/archive/2026/11/13/move-mvp-gl-toolkit-to-gacalc-step-4-graphers-as-library.md` (done 2026-11-13). That step puts
the 3D grapher in gacalc as `src/gacalc/gl/grapher3d.py`, with `run(surfaces)`.
**Background:** mvp's `tasks/archive/2026/11/03/graphing-calculator-2d-3d.md`, which built the base
graphers. Read it first.

## BLUF

Take the 3D `f(x,y)` height-field grapher and render its surface as a **solid triangle mesh with
Blinn-Phong lighting**. That is the half-vector specular model, not Phong's reflection-vector model.
The work is to triangulate the height field, compute **normals** from it, add a light, and shade in
a core-profile shader. Done means the 3D grapher can draw its surfaces as lit, solid triangle meshes,
alongside the wireframe or instead of it, with a specular highlight that follows the light and the
view.

## Why a separate task

The base graphers stopped at wireframe and an unlit height-shaded solid, so the first version stayed
small. Lighting adds normals, a light model, a lit shader and material parameters, so it gets its own
commit boundary.

## Plan (draft)

- [ ] **Triangulate** the height field: two triangles per grid cell, wound counter-clockwise (the
      repo-wide GL conventions, mvp `tasks/reference/gl-and-imgui-gotchas.md` section 7, copied into
      gacalc's `tasks/reference/gl-toolkit.md` by step 3), indexed by an element buffer.
- [ ] **Normals** from the height field: per-vertex normals that average the adjacent face normals,
      or analytic normals from the partial derivatives `∂f/∂x`, `∂f/∂y` (open question 1).
      - Use gacalc for the CPU-side vector math, written the way gacalc's `CLAUDE.md` asks: the named
        operations, and `cross` from `gacalc.vectorcalc`.
      - Doctest the normal builder.
- [ ] **Blinn-Phong lit shader** (core profile):
      - diffuse `max(0, N·L)`;
      - specular `pow(max(0, N·H), shininess)`, where **H is the halfway vector** `normalize(L + V)`.

      Per-fragment lighting is the target (a smooth highlight). Per-vertex is acceptable as a first
      cut.
- [ ] One directional or point light. Expose the light direction and shininess in the menubar,
      beside the existing dx/dy and view controls (open questions 2 and 3).
- [ ] Keep the wireframe available as a toggle, so the lit surface and the mesh can be compared.

## The Blinn-Phong math

The specular term uses the **cosine** of the angle between the surface normal `N` and the **halfway
vector** `H`. Both are unit vectors, so that cosine is their dot product, and no `cos()`, `sin()` or
`acos()` call is needed. For a fragment:

```
L = normalize(lightDir)          // unit direction TO the light
V = normalize(eyeDir)            // unit direction TO the viewer/eye
H = normalize(L + V)             // the halfway vector  (this is the "half")
N = normalize(surfaceNormal)

diffuse  = max(0, dot(N, L))
specular = pow(max(0, dot(N, H)), shininess)   // only when dot(N,L) > 0
color    = ambient + diffuse * materialDiffuse + specular * materialSpecular
```

`dot(N, H)` is `cos(θ)` for the angle `θ` between `N` and `H`, and `shininess` sharpens the
highlight. The original **Phong** model uses the reflection vector `R` and `dot(R, V)` instead.
Blinn's `dot(N, H)` is cheaper, and it is the "half-angle" model the maintainer asked for. `H` and
the dot products are computed in the GLSL fragment shader on the GPU, so gacalc is in the CPU path
only: the transforms and the normals.

> **Terminology caveat.** Blinn's half **vector** (the bisector `normalize(L + V)`) is unrelated to
> the geometric-algebra rotor's half **angle** (`cos(θ/2) + I * sin(θ/2)`). The two share the word
> "half". The shading needs only the former. A rotor aside would be teaching material, not part of
> the lighting.

## Inspiration: the OpenGL SuperBible v4 port (read before writing the shader)

These files are in mvp (github.com/billsix/modelviewprojection), under `ports/openglsuperbiblev4/`:
- `chapt16/vertexshaders/shaders/specular.vs`: the **per-vertex** half-vector,
  `vec3 H = normalize(L + normalize(-V.xyz)); float NdotH = max(0.0, dot(N, H));
  specular = pow(NdotH, specularExp)` with `specularExp = 128.0`.
- `chapt17/lighting/shaders/specular.{vs,fs}`: the **per-fragment** version, which interpolates N, L
  and V to the fragment shader and computes H and the lighting there. Aim for this shape.
- These shaders use the legacy built-ins `gl_ModelViewProjectionMatrix` and `gl_Normal`. Port the
  *math* into the grapher's own core-profile shader, with explicit `uniform` and `in` attributes.

## Open questions

1. Should the normals be analytic, from `∂f/∂x` and `∂f/∂y` of the authored function, or averaged
   from the adjacent triangle faces? Recommendation: analytic, since the inputs are known functions.
   That could mean an optional derivative field on `Surface`, or sympy differentiation, which gacalc
   already depends on.
2. Should there be one light? mvp's v4 `3lights` shader uses three. Recommendation: start with one
   directional light, which gives the clearest highlight.
3. Should the light direction and shininess be menubar sliders, rather than defaults hard-coded in
   source? Recommendation: sliders, because they are view settings, not function definitions.
