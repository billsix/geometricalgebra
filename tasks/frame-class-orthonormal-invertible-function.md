# `Frame` dataclass — an orthonormal representation of a frame, and its `InvertibleFunction`

**Status:** proposed — open questions below block implementation
**Priority:** 3
**Difficulty:** 5
**Created:** 2026-11-04 (William Emerison Six <billsix@gmail.com>)
**Part of / resolves:** the open "representation decision" in `tasks/define-frame.md` (a dedicated
`Frame` class, chosen by the maintainer 2026-11-04).

## BLUF

Add a `Frame` dataclass to `src/gacalc/frame.py`. Its constructor takes a frame (linearly independent
vectors `v_1 … v_k`) and stores two things in its place: an orthonormal ordered set `u_1 … u_k` and, for
each original vector, the coefficients that rebuild it (`v_i = Σ_j c_ij u_j`). `iter(frame)` gives back
the original vectors. `Frame.to_invertible_function()` returns an `InvertibleFunction` whose forward map
sends `e_i ↦ v_i` and whose inverse is computed by dotting with the orthonormal set. Done = all of this
passes symbolic (sympy) tests in 𝒢₂ and 𝒢₃, plus an SVD investigation written up (Phase 4).

## Context (read first)

- `tasks/define-frame.md`: Phase 1 is done. `src/gacalc/frame.py` already has `are_linearly_independent`,
  `is_frame`, `prefix_blades`, `make_orthogonal_frame` (rejection-based Gram–Schmidt),
  `make_orthogonal_frame_hestenes`, and `make_orthogonal_frame_hestenes_inverse`. The symbolic test
  pattern (`sympy.symbols` coefficients) is in `tests/test_frame.py`.
- `tasks/reference/transform-and-composable-function-layer.md`: maps `ComposableFunction` /
  `InvertibleFunction` (`src/gacalc/functions.py`). Constructor fields are `func`, `latex_repr`,
  `inverse`, `latex_repr_inv`; there is a `linearity` tag, and `to_matrix` uses it. Transform factories
  late-bind the basis via `type(v).basis_vector(i)`.
- `tasks/reference/symbolic-equality.md`: how to compare sympy-valued multivectors.
- `tasks/lean-frame-coverage.md`: Lean coverage of `frame.py` (parked 2026-10-04).

## The maintainer's request (2026-11-04, paraphrased)

1. A dataclass whose constructor accepts vectors that make a frame.
2. Its internal representation is an **orthogonalized, normalized ordered set** (an instance variable),
   built in `__post_init__`.
3. A second instance variable holds, for each orthonormal vector, an iterable of **coefficients**. These
   are multiplied pairwise with the orthonormal vectors and summed to rebuild the original vector list.
4. `__iter__` returns the **original** vectors, rebuilt from 2 + 3.
5. `to_invertible_function()` → `InvertibleFunction`. **Forward:** project the input onto
   `e_1, e_2, …` (as many as there are frame vectors), then multiply each component by the matching vector
   from `iter()` and sum: `f(x) = Σ_i (x · e_i) v_i`. **Inverse:** dot the input with the orthonormal
   set, then use orthonormality to recover `x`.
6. Symbolic unit tests in 2D and 3D, using sympy first (Lean only if sympy struggles).
7. If the sympy version works, create a follow-up task for Lean equivalents.
8. Try to rederive the SVD this way (the maintainer expects it may not work, but wants it tried).

## Analysis: what this is mathematically (prior art)

**It is the QR decomposition, written in GA terms.** Put the frame vectors in the columns of `V`, so
`V = Q R`:

- the orthonormal set `u_1 … u_k` = the columns of `Q`;
- the coefficients `c_ij = u_j · v_i` = the entries of `R`. Gram–Schmidt makes `R` **upper triangular**:
  `v_i` only uses `u_1 … u_i`, so `c_ij = 0` for `j > i`. The diagonal is `c_ii = |w_i|`, the length of
  the `i`-th rejection, which equals `|A_i| / |A_{i-1}|` in Hestenes' prefix-blade notation (H&S eq 3.1;
  see `define-frame.md` Part 1c);
- the forward map `f(x) = Σ (x·e_i) v_i` is multiplication by `V`;
- the inverse is `x = R⁻¹ Qᵀ y`. Dotting `y` with each `u_j` gives `u_j·y = Σ_i c_ij x_i` (that is
  `Qᵀ y`). Because `R` is triangular, the result is solved by **back-substitution**, last coordinate
  first: `x_k = (u_k·y)/c_kk`, then `x_{k-1} = (u_{k-1}·y − c_{k-1,k} x_k)/c_{k-1,k-1}`, and so on.

This is the standard numerical-linear-algebra way to solve `Vx = y` and least-squares problems (Stanford
EE263 QR lecture, linked below). It is uncommon in intro textbooks, which teach inverses through RREF /
Gauss–Jordan, so it may look new. What the GA version adds: orthogonalization by **rejection** instead of
coordinates (`make_orthogonal_frame` already does this), and the triangular coefficients have a geometric
meaning (`c_ii = |A_i|/|A_{i-1}|`, a ratio of successive span volumes). A web search (2026-11-04) found no
source presenting this exact construction as a GA linear transformation.

**Dotting with the orthonormal set alone does not give `x`.** It gives `y`'s coordinates in the `u`
basis. A triangular undo is still needed. The undo is cheap and exact, but it has to be in the inverse.

**The GA-native comparison is the reciprocal frame.** `x_i = vⁱ · y` in one step, with
`vⁱ · v_j = δⁱ_j`. galgebra builds `vⁱ` from the pseudoscalar (`define-frame.md`, "How galgebra does
it"). There is a direct link to this task: **the reciprocal of the last vector is `vᵏ = w_k / |w_k|²`**,
because `w_k` is orthogonal to `v_1 … v_{k-1}`. Back-substitution is therefore the reciprocal frame built
one vector at a time, from the end backwards. The tests should check that both inverses agree.

**Float precision.** Classical Gram–Schmidt loses orthogonality on nearly-dependent frames (Householder
or modified Gram–Schmidt are the stable choices). That does not matter for symbolic tests. Add one
numeric test with a mildly oblique frame, and note the limitation in the docstring.

## Design (proposed; finalize after the questions)

```python
@dataclasses.dataclass(frozen=True)
class Frame(Generic[V]):
    vectors: dataclasses.InitVar[Sequence[V]]               # constructor input only
    orthonormal_vectors: tuple[V, ...] = field(init=False)  # u_1 … u_k
    coefficients: tuple[tuple[Real, ...], ...] = field(init=False)  # coefficients[i][j] = u_j · v_i

    def __post_init__(self, vectors): ...    # is_frame check → ValueError; make_orthogonal_frame → normalize;
                                             # c_ij = u_j · v_i; object.__setattr__ (frozen)
    def __iter__(self) -> Iterator[V]: ...   # yields Σ_j c_ij u_j for each i
    def __len__(self) -> int: ...
    def to_invertible_function(self) -> InvertibleFunction[V]: ...  # linearity=LINEAR
```

- Reuse `make_orthogonal_frame` + `base.normalize`; don't add a third Gram–Schmidt.
- Store `coefficients` as full `k`-length rows, with the zeros below the diagonal kept explicitly. This
  matches "pairwise multiply and sum" literally, and a test can check the triangular structure.
- `__iter__` rebuilds the vectors instead of storing the originals, as requested. The rebuild is exact
  symbolically and accurate to round-off in floats.
- Forward map: `e_i` comes from `type(x).basis_vector(i)`, following the transform-factory convention.

**The three-forms rule (`CLAUDE.md`).** The maintainer overrode it for this request: sympy goes first,
and Lean becomes a follow-up task. The prose + LaTeX book page is also deferred, until the Lean task
exists or the maintainer asks for it. Tests follow `CLAUDE.md`'s conventions: vectors written as
`2 * e_1 + 1 * e_2` from basis constants, Hestenes-grade local names, the LGPL header, and every
binding typed.

## Plan

- **Phase 1 — `Frame` dataclass.** Constructor, `__post_init__`, `__iter__`, `__len__`. Tests in 𝒢₂ and
  𝒢₃: the input is symbolic (`v_i` with sympy-symbol components, assuming independence), or concrete
  oblique for the round-trip. Check that `orthonormal_vectors` are unit length and mutually orthogonal,
  that `coefficients` is upper triangular, that `list(frame) == input` (via `symbolic-equality.md`), and
  that a non-frame raises `ValueError`.
- **Phase 2 — `to_invertible_function`.** Back-substitution inverse. Tests in 2D and 3D:
  `f(e_i) == v_i`; `f⁻¹(f(x)) == x` and `f(f⁻¹(y)) == y` for a symbolic `x`/`y`; `to_matrix(f)` has the
  `v_i` as its columns; the inverse matches the reciprocal-frame formula `x_i = vⁱ·y`.
- **Phase 3 — docs.** Docstrings that say "this is QR" and cite the prior art; a `tasks/reference/`
  domain note (frame → QR → reciprocal frame) if Phase 4 adds enough material; a `CHANGELOG.md`
  `[Unreleased]` "Added" entry.
- **Phase 4 — SVD investigation (exploratory; the result is a write-up, not necessarily code).** My
  read: a single `Frame` cannot produce the SVD. QR is one orthogonalization, while the SVD needs the
  eigenvectors of `fᵀf`. Three routes worth trying, cheapest first:
  1. **`f = Q ∘ R` as GA transforms.** `Q` is orthogonal, so it is a versor (a rotor, or a rotor times a
     reflection when `det Q < 0`), and `R` is a triangular shear-scale. This decomposition follows
     directly from Phase 1 and is achievable now.
  2. **The QR algorithm.** Repeatedly build `Frame`s (`A ← R Q`) on `fᵀf`. It converges to the
     eigen-decomposition, so it yields the SVD as a limit. Numeric only; this is real "SVD via frames".
  3. **Closed-form 2D SVD as `rotor ∘ scale_non_uniform ∘ rotor`**, built from the existing factories,
     with a symbolic check. 3D in closed form needs cubic roots, so expect it to be messy symbolically.
  Prior art: Doran's lecture notes mention the SVD as one representation of a linear function. Rotor
  recovery between frames is studied by Lasenby et al. A web search found no source that derives the
  SVD as a rotor sandwich.

## Open questions (block implementation)

1. **Fewer vectors than the dimension (`k < n`).** The forward map keeps only `x·e_1 … x·e_k` and drops
   the rest, so it is not invertible on the whole space. `f⁻¹(f(x)) = x` holds only for
   `x ∈ span(e_1…e_k)`. On `y` outside `span(v)`, the back-substitution inverse returns the
   least-squares answer. Options: (a) `Frame` accepts any `k`, and `to_invertible_function` raises unless
   `k = n`. (b) Allow `k < n` and document the partial inverse. **Recommend (a).**
2. **Storing originals vs rebuilding them.** You asked for `__iter__` to rebuild from coefficients, and
   the plan does that. Should the originals *also* be kept (to avoid float drift), or not at all?
   **Recommend not at all**, as you described.
3. **SVD placement.** Should Phase 4 stay in this task, or become its own task once Phases 1–3 are done?
   **Recommend its own task**, so this one can be archived as soon as the code is green.

## Follow-ups to create at completion (not now)

- **Lean equivalents** (only if the sympy version works, per the maintainer): a task mirroring the
  `Frame` invariants (orthonormality, triangular coefficients, rebuild, `f⁻¹ ∘ f = id`), cross-linked
  with `tasks/lean-frame-coverage.md`.
- When this is archived, update `tasks/define-frame.md` (the representation decision and its codebase
  sweep).

## Sources (web search 2026-11-04)

- [Stanford EE263 — QR factorization lecture](https://web.stanford.edu/class/archive/ee/ee263/ee263.1082/lectures/qr.pdf): Gram–Schmidt as QR, triangular `R`
- [QR decomposition (Wikipedia mirror)](https://kaweah.freedombox.rocks/kiwix/wikipedia_en_all_maxi_2023-10/QRD): solving with QR and least squares; Gram–Schmidt stability vs Householder/Givens
- [Singular value decomposition (Wikipedia)](https://en.wikipedia.org/wiki/Singular_value_decomposition): rotation · axis scaling · rotation
- [Doran, GA2015 Lecture 4](https://geometry.mrao.cam.ac.uk/wp-content/uploads/2015/10/GA2015_Lecture4.pdf): linear functions in GA (outermorphism), mentions the SVD
- [Composing Linear Layers from Irreducibles (arXiv 2507.11688)](https://arxiv.org/pdf/2507.11688): linear maps as sums of rotor sandwiches, citing H&S
- [Boston, GA for camera networks](https://facerec.ece.wisc.edu/cameranet/Geometric_Algebra__boston.pdf): SVD used to recover a rotor (Lasenby et al. 1996)
