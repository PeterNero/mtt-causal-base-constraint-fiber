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

The third theorem compares compression with the actual transfer mechanisms
already present in the MTT research mesh. It proves the common propagated-
excursion identity

```text
E_R(S,T) = P S R T P,
D_R - D_Q = -P S (R-Q) T P.
```

Raw compression uses `R=Q`, Feshbach reduction uses the excluded resolvent, and
Hodge transfer uses the degree-minus-one homotopy `h=d*G_Q`. Exact pinned
witnesses disprove their direct identification: one A-infinity channel has raw
excursion zero but transferred `m3(a,a,b)=ac`, while the Feshbach raw and
resolvent-weighted values are respectively `1/4` and `1/12`. The shared
architecture is exact; the propagator cannot be omitted.

The fourth theorem executes that architecture on the selected finite q79 Weyl
geometry. The commuting adjoint actions of the selected qutrit Weyl pair define
a canonical 36-dimensional twisted Koszul DGA. Exact Hodge theory gives
cohomology dimensions `1,2,1`, reduced-Green eigenvalues `1/3` and `1/6`, and a
contracting homotopy `h=d*G`. The harmonic center is already an exterior
subalgebra, so every transferred `m_n` above `m2` vanishes. This proves a useful
interaction cutset rather than manufacturing a higher product.

It also separates two previously easy-to-confuse 96-dimensional spaces. The
Weyl-center range and `ker(D_fin)` have zero intersection: the selected shift
response leaks outside the center, while the compressed response is exactly
invertible. The finite Weyl contraction is therefore not the finite Dirac
zero-mode projector.

The fifth theorem supplies the first exact global q79 bridge for that finite
Hodge object. The six affine `S3` holonomies lift to unitary cochain maps and
preserve `Delta`, `P`, `G` and `h`. A local Fourier cochain map has order four
and induces the exact quarter-turn `j=[[0,-1],[1,0]]` on harmonic one-forms.
After tensoring harmonic `H1` by the determinant line and rank-three sheet
bundle, the two monodromy signs cancel and give exactly the established q79
`D/E` strain local system, including `J_DE`, the rank-two Reynolds subbundle
and rank-four TT subbundle.

The same calculation identifies the precise limit. The harmonic exterior
product globalizes, but affine reflections have 360 nonmultiplicative basis
pairs each and the Fourier lift has 108. Full-chain `C4` also fails to commute
with translated `S3` holonomies. Thus `C4` globalizes on the harmonic/strain
shadow, not as a parallel automorphism of the full forward-difference DGA.

The sixth theorem constructs the minimal signed-direction completion that
removes those product defects. The 144-dimensional calculus on
`+x,-x,+z,-z` is an exact DGA under affine `S3` and Fourier `C4`; together they
generate `(Z3 x Z3) semidirect C4` of order 36. The unique equal half-edge
metric preserves the selected `0,3,6` Hodge eigenvalues.

The old 36-dimensional complex survives exactly as an isometric reducing
cochain summand. Its harmonic image is the orientation-odd `(1,2,1)` exterior
algebra already tied to q79 strain. The full symmetric complex also has twelve
additional harmonic classes. Off harmonics the selected image is not product
closed: 864 basis pairs leak, compressed multiplication differs on 504 pairs,
and it has 4,464 nonzero associators. Finite covariance is therefore solved,
but physical mode selection and full-chain product transfer are not.

The seventh theorem resolves the harmonic mode-selection question at the
universal first-jet tier. In the odd/even signed-edge basis, reflection and the
Fourier square act by `diag(-1,-1,+1,+1)`, so the odd projector is canonically

```text
P_O = (1-Fourier^2)/2.
```

For every connection-generated signed transport family, exact `sinh/cosh`
expansion shows that the odd plane carries the principal first derivative,
while the even plane begins with `h*nabla^2/2`. The twelve extra harmonic
classes are exactly the ideal generated by the even plane, and quotienting by
that ideal gives the selected `(1,2,1)` exterior algebra strictly and
associatively. This is a derived first-jet selector, not yet a physical q79
HYM promotion: the selected endpoint, continuum intertwiner and error bounds
remain open.

The eighth theorem closes the previously open finite response transfer through
arity three without deleting those twelve classes. It constructs the exact
48-dimensional target

```text
T = old q79 response complex direct-sum higher-jet harmonic ideal
```

and an explicit strong deformation retract from the 144-dimensional symmetric
DGA onto `T`. Homological transfer gives 881 nonzero binary products and 17,204
nonzero ternary products. The transferred `m3` satisfies the arity-three
Stasheff identity on all 110,592 homogeneous basis triples and therefore
supplies the precise homotopy correction to 7,124 nonzero binary associators.
It vanishes on all-harmonic triples and whenever two or more inputs lie in the
higher-jet ideal. This is an exact finite low-arity result; `m4` and higher,
the `D_fin` bridge, the continuum HYM realization and a physical action were
not closed at that tier. The next theorem closes `m4` only.

The ninth theorem proves that the transfer does not truncate after `m3`.
Using the same source-locked contraction and sign convention, it computes a
nonzero degree-minus-two `m4` on 693,208 basis quadruples. The arity-four
Stasheff identity has zero residual on all 3,869,500 degree-admissible
quadruples, and an independent implementation reproduces the complete support,
sector tables and operation digest. The operation vanishes with the unit, on
all-harmonic inputs and with three or four higher-jet inputs, but it is nonzero
with one or two such inputs. This closes finite transfer through arity four;
`m5` and higher remain open.

## Run the proof

```powershell
python verify.py
```

The verifier uses only the Python standard library. It rebuilds the first eight
packets, independently checks the `m4` packet in routine mode and runs the unit
tests.

The complete independent `m4` table and SI(4) replay is intentionally separate
from the routine suite because it evaluates 3,869,500 admissible quadruples:

```powershell
python verify_q79_symmetric_response_transferred_m4.py --recompute
```

## Repository map

- `RESEARCH_CHARTER.md`: typed hypothesis and promotion rules.
- `CURRENT_STATUS.md`: kernel-locked MTT status at project creation.
- `KERNEL_AUTHORITY_LOCK.json`: machine-readable authority snapshot.
- `CausalBaseConstraintFiberCompressionLeakageTheorem_v1.md`: theorem, proof,
  witness, locality corollary and nonclaims.
- `RepairFixedPointGaugeDescentTheorem_v1.md`: exact bridge from equivariant
  repair through fixed-point linearization to Riesz projection and faithful
  observable symmetry.
- `CohesiveRepairCompressionTransferComparisonTheorem_v1.md`: exact verdict on
  raw compression versus Green/homotopy and Feshbach transfer.
- `SelectedFiniteWeylKoszulHodgeAndInteractionCutsetTheorem_v1.md`: exact
  selected finite differential, Hodge contraction, transferred-product
  verdict and rank-96 cutset.
- `Q79WeylKoszulMonodromyC4CohomologyIntertwinerAndProductCutsetTheorem_v1.md`:
  exact `S3` cochain descent, local Fourier `C4`, determinant-twisted harmonic
  `H1` strain intertwiner and full-product cutset.
- `SelectedSymmetricWeylCalculusIsometricRetractionAndCovarianceCutsetTheorem_v1.md`:
  minimal four-direction DGA, order-36 covariance, half-edge Hodge theory,
  selected-complex retract and product/extra-mode cutset.
- `SignedEdgeFirstJetSelectionAndHarmonicIdealQuotientTheorem_v1.md`: exact
  odd/even parity split, universal first-jet selection, twelve-class harmonic
  ideal and strict selected quotient.
- `SymmetricWeylResponseRetractionAndTransferredM3Theorem_v1.md`: exact
  48-dimensional strong deformation retract and complete transferred `m2/m3`
  execution through the arity-three Stasheff identity.
- `SymmetricWeylTransferredM4AndArityFourStasheffTheorem_v1.md`: complete
  transferred `m4`, higher-jet support and exhaustive arity-four certificate.
- `closure_dynamics_transfer_source_lock.json`: commit, Git-blob and SHA-256
  provenance for the read-only source artifacts.
- `q79_weyl_koszul_source_lock.json`: pinned q79 Weyl, completed-response,
  shared-line and cyclic-cotangent inputs.
- `q79_weyl_koszul_monodromy_c4_source_lock.json`: pinned finite Hodge,
  q79-monodromy, shared-root `C4` and continuum-boundary inputs.
- `q79_symmetric_weyl_calculus_source_lock.json`: pinned selected-complex and
  monodromy/C4 cutset inputs for the signed-direction completion.
- `q79_signed_edge_first_jet_source_lock.json`: pinned symmetric-calculus,
  harmonic-C4 and adjacent q79 first/second-jet evidence for the first-jet
  quotient theorem.
- `q79_symmetric_response_transfer_source_lock.json`: pinned symmetric DGA,
  selected retract and higher-jet-ideal sources for the response transfer.
- `q79_symmetric_response_higher_transfer_source_lock.json`: pinned low-arity
  transfer and Merkulov-recursion boundary for the `m4` extension.
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
- `cohesive_repair_compression_transfer_comparison.packet.json`: generated
  compression/transfer comparison certificate.
- `selected_finite_weyl_koszul_hodge_and_interaction_cutset.packet.json`:
  generated exact finite q79 Hodge/cutset certificate.
- `q79_weyl_koszul_monodromy_c4_cohomology_intertwiner.packet.json`: generated
  global cohomology-shadow bridge and product-cutset certificate.
- `q79_symmetric_weyl_calculus_isometric_retraction.packet.json`: generated
  symmetric-covariance, Hodge-retract and extra-mode certificate.
- `q79_signed_edge_first_jet_harmonic_ideal_quotient.packet.json`: generated
  signed-edge parity, formal jet and harmonic-ideal quotient certificate.
- `q79_symmetric_response_retraction_transferred_m3.packet.json`: generated
  strong-deformation-retract and transferred low-arity operation certificate.
- `q79_symmetric_response_transferred_m4.packet.json`: generated complete `m4`
  support, digest, cutsets and SI(4) certificate.
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

The immediate finite frontier is no longer an unexplained harmonic projector
or a missing ternary/quaternary correction. The orientation-odd first-jet quotient is
forced for every connection source, and the exact 48-dimensional target now
retains the complementary higher-jet classes while carrying the transferred
product through `m4`. The nonzero quaternary operation rules out truncation
after `m3`; what remains finitely begins at `m5`. Physical promotion still requires the selected
nonzero-Chern q79 HYM endpoint, analytic domains and pairing, its Green
operator, physical C4 naturality, a `D_fin` intertwiner and certified
finite/continuum error bounds from one selected source.

The nine exact packets currently pass `338/338` checks and thirty-nine unit
tests. The finite `P/G/h` package, q79 harmonic strain globalization, full
signed-direction DGA covariance, universal harmonic first-jet quotient and
response transfer through `m4` are closed. Transfer from `m5` onward, the selected HYM
endpoint, finite-to-continuum intertwiner and physical-action promotion are
not.
