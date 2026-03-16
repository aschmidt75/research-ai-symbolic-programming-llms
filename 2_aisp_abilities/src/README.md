


## Format of prompts

- every file in request-*.txt
- this is the user prompt
- Tight binding + output constraint (recommended)
⊢𝔸1.0.classify_b2c_order@2026-03-15
Δ⊗λ ≡ 3
∀output: output ∈ 𝔻oc ∧ ⊢wf(output)

<user input here>
⊢ — invokes/asserts the spec
Δ⊗λ ≡ 3 — forces zero-cost binding (the tightest level, where Post(A) ⊆ Pre(B)), as defined in ⟦Γ:Binding⟧. This means "no adaptation, no null state, no crash — exact match only."
∀output: output ∈ 𝔻oc ∧ ⊢wf(output) — output MUST be a well-formed AISP document, nothing else

