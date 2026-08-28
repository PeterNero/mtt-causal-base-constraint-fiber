# MTT Causal Base and Constraint Fiber Program

This repository tests a precise reformulation of a recurring MTT idea:

> Physical locality belongs to a Lorentzian causal base, while much of the
> higher bundle geometry may encode consistency, holonomy, admissibility and
> repair constraints rather than additional places in which signals travel.

That sentence is a research hypothesis, not a completed physical theorem. The
repo is designed to turn it into small, typed, executable claims and to reject
it where those claims fail.

## Exact results

The initial theorem proves an exact operator identity. Let `P` be an orthogonal
projector, `Q = I - P`, and let upper self-adjoint operators `A_tilde` and
`B_tilde` commute. Their compressions to `Ran(P)` obey

```text
[P A_tilde P, P B_tilde P]
  = L_B^* L_A - L_A^* L_B,

L_A = Q A_tilde P,
L_B = Q B_tilde P.
```

Thus compressed noncommutativity is exactly the antisymmetric product of the
two excluded-sector leakage maps. Compatible operators, for which the leakage
vanishes, retain commutativity. This gives one algebraic language for both:

- preservation of spacelike locality on the coherent-preserving local algebra;
- possible noncommutativity of other compressed observables.

The included rational `3 x 3` witness verifies every matrix identity exactly.
It does **not** derive the canonical commutation relations, Planck's constant,
the physical q79 projector, or a Bell state.

The second theorem starts one level higher. For a group-equivariant repair law,
it proves that every symmetry stabilizing a fixed point commutes with the
linearized repair operator and its isolated Riesz projector. Compression and
leakage then transform covariantly, and the action on physical observables
factors through the source stabilizer modulo its exact kernel. A nonlinear
finite witness realizes the complete chain with a 12-element source group and a
two-element central kernel.

## Run the proof

```powershell
python verify.py
```

The verifier uses only the Python standard library. It rebuilds the packet,
checks the exact rational witness and runs the unit tests.

## Repository map

- `RESEARCH_CHARTER.md`: typed hypothesis and promotion rules.
- `CURRENT_STATUS.md`: kernel-locked MTT status at project creation.
- `KERNEL_AUTHORITY_LOCK.json`: machine-readable authority snapshot.
- `CausalBaseConstraintFiberCompressionLeakageTheorem_v1.md`: theorem, proof,
  witness, locality corollary and nonclaims.
- `RepairFixedPointGaugeDescentTheorem_v1.md`: exact bridge from equivariant
  repair through fixed-point linearization to Riesz projection and faithful
  observable symmetry.
- `MTT_FIXEDPOINT_GAUGE_GROUNDING_MAP_v1.md`: current fixed-point, A47 gauge,
  locality, duality and dimensions status map.
- `PHILOSOPHICAL_INTERPRETATION_OF_CONSTRAINT_REALISM_v1.md`: disciplined
  philosophical reading, competing ontologies, objections and Bell boundary.
- `CONSTRAINT_REDUCTION_REFERENCE_SYSTEM_v0.md`: candidate common language for
  preprojection rules, compression and transferred higher products.
- `RESEARCH_ROADMAP.md`: ordered route from this identity to a selected MTT
  physical construction.
- `constraint_compression_leakage.packet.json`: generated exact certificate.
- `repair_fixedpoint_gauge_descent.packet.json`: generated repair/symmetry
  certificate.
- `build_constraint_compression_leakage.py`: deterministic packet builder.
- `verify_constraint_compression_leakage.py`: independent packet verifier.
- `repo-manifest.json`: scope and reproducibility contract.

## Kernel workflow

This repo belongs to the shared MTT research mesh. Future work must begin with
the MTT kernel bootstrap, read current A/B objects rather than inferring status
from old corpus prose, audit the worktree, and update the durable handoff before
finishing. See `AGENTS.md` for the exact continuation procedure.

## Current scientific position

The project begins downstream of established MTT structural results and
upstream of open physical source selection:

- the canonical q79 operational Born theorem is closed on its declared domain;
- compatible coherent compression already has a locality-descent theorem;
- a cohesive closure-repair residual and tangent semigroup exist on a certified
  benchmark;
- the selected physical upper action, q79 HYM endpoint, continuum operator and
  universal apparatus family remain open.

The immediate next frontier is therefore not another interpretation. It is to
derive the physical projector `P` as the tangent/spectral projector of one
selected closure-repair dynamics and then identify the leakage maps from the
same source.

The two exact packets currently pass `49/49` rational checks and five unit
tests. The abstract repair-to-projector arrow is closed; its physical q79
instantiation is not.
