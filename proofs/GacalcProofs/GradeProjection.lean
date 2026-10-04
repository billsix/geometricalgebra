import GacalcProofs.G2
import GacalcProofs.G3

/-! # Grade projection: `r_vector_part`, `even_part`, `odd_part`

    The grade-r selector `⟨a⟩_r` keeps the grade-r coefficients and zeros the rest (gacalc
    `r_vector_part`, base.py); `even_part`/`odd_part` sum the even/odd grade parts
    (base.py). The projection laws — idempotence, completeness (the parts reassemble the
    whole), and even+odd = whole — are coordinate leaves. "Obvious by construction," but named here so
    the contraction/inner-product proofs can lean on them. -/
namespace GacalcProofs

namespace G2

/-- Grade-r projection `⟨a⟩_r` on 𝒢₂ (grades 0,1,2; higher r gives 0), as the linear
    combination of the grade-r basis blades (the `e_*` constants) rather than a positional
    struct literal — the Lean mirror of gacalc's "build from the basis constants". -/
noncomputable def rVectorPart (r : ℕ) (a : G2) : G2 :=
  match r with
  | 0 => smul a.s one
  | 1 => add (smul a.c1 e_1) (smul a.c2 e_2)
  | 2 => smul a.c12 e_12
  | _ => ⟨0, 0, 0, 0⟩

/-- Even part `⟨a⟩₀ + ⟨a⟩₂`. -/
noncomputable def evenPart (a : G2) : G2 := add (rVectorPart 0 a) (rVectorPart 2 a)

/-- Odd part `⟨a⟩₁`. -/
noncomputable def oddPart (a : G2) : G2 := rVectorPart 1 a

/-- **Idempotence:** `⟨⟨a⟩_r⟩_r = ⟨a⟩_r`. -/
theorem rVectorPart_idem (r : ℕ) (a : G2) :
    rVectorPart r (rVectorPart r a) = rVectorPart r a := by
  rcases r with _ | _ | _ | n <;>
    simp only [rVectorPart, add, smul, one, e_1, e_2, e_12] <;> ext <;> ring

/-- **Completeness:** `⟨a⟩₀ + ⟨a⟩₁ + ⟨a⟩₂ = a`. -/
theorem rVectorPart_complete (a : G2) :
    add (add (rVectorPart 0 a) (rVectorPart 1 a)) (rVectorPart 2 a) = a := by
  simp only [rVectorPart, add, smul, one, e_1, e_2, e_12]; ext <;> ring

/-- **Even + odd = whole:** `even_part a + odd_part a = a`. -/
theorem even_add_odd (a : G2) : add (evenPart a) (oddPart a) = a := by
  simp only [evenPart, oddPart, rVectorPart, add, smul, one, e_1, e_2, e_12]; ext <;> ring

end G2

namespace G3

/-- Grade-r projection `⟨a⟩_r` on 𝒢₃ (grades 0,1,2,3; higher r gives 0). -/
noncomputable def rVectorPart (r : ℕ) (a : G3) : G3 :=
  match r with
  | 0 => ⟨a.s, 0, 0, 0, 0, 0, 0, 0⟩
  | 1 => ⟨0, a.c1, a.c2, a.c3, 0, 0, 0, 0⟩
  | 2 => ⟨0, 0, 0, 0, a.c12, a.c13, a.c23, 0⟩
  | 3 => ⟨0, 0, 0, 0, 0, 0, 0, a.c123⟩
  | _ => ⟨0, 0, 0, 0, 0, 0, 0, 0⟩

/-- Even part `⟨a⟩₀ + ⟨a⟩₂`. -/
noncomputable def evenPart (a : G3) : G3 := add (rVectorPart 0 a) (rVectorPart 2 a)

/-- Odd part `⟨a⟩₁ + ⟨a⟩₃`. -/
noncomputable def oddPart (a : G3) : G3 := add (rVectorPart 1 a) (rVectorPart 3 a)

/-- **Idempotence:** `⟨⟨a⟩_r⟩_r = ⟨a⟩_r`. -/
theorem rVectorPart_idem (r : ℕ) (a : G3) :
    rVectorPart r (rVectorPart r a) = rVectorPart r a := by
  rcases r with _ | _ | _ | _ | n <;> rfl

/-- **Completeness:** `⟨a⟩₀ + ⟨a⟩₁ + ⟨a⟩₂ + ⟨a⟩₃ = a`. -/
theorem rVectorPart_complete (a : G3) :
    add (add (add (rVectorPart 0 a) (rVectorPart 1 a)) (rVectorPart 2 a)) (rVectorPart 3 a) = a := by
  simp only [rVectorPart, add]; ext <;> ring

/-- **Even + odd = whole:** `even_part a + odd_part a = a`. -/
theorem even_add_odd (a : G3) : add (evenPart a) (oddPart a) = a := by
  simp only [evenPart, oddPart, rVectorPart, add]; ext <;> ring

end G3

end GacalcProofs
