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
the complete `m5` table remained open at that tier.

The tenth theorem replaces an invalid fixed-parity extrapolation with the exact
mode-dependent invariant space `R_g=image(H|V_g)`. In every nonzero Fourier
mode this space has graded dimensions `(2,3,1)`, is preserved by left and right
"multiply by `J`, then apply `H`" operators, and every terminal multiplication
by `J` is killed by the target projection. The resulting tree theorem proves
for every `n>=3` that `m_n` vanishes with `n-1` or more `J` inputs. The same
packet evaluates Merkulov's exact `lambda5` on 86,796 selected admissible
quintuples and gives the independently replayed witness

```text
m5(C:0,0,1, C:0,0,1, C:0,0,1, C:1,0,1, C:1,0,0)
  = (1/24 + omega/48) C:2,0,1.
```

The witness extends to an exact two-parity recurrence. For
`x=C:0,0,1`, `y=C:1,0,1` and `z=C:1,0,0`, the odd and even subsequences are

```text
m_(2r+3)(x^(2r+1),y,z) = (2+omega)/(4*12^r) C:2,0,1,
m_(2r+4)(x^(2r+2),y,z) = -omega/(8*12^r) C:2,0,1.
```

Therefore `m_n` is nonzero for every `n>=3`: this finite transfer never
truncates. Complete operation and Stasheff tables from `m5` onward remain open.

The eleventh theorem closes a different all-arity question: source promotion
does not require a separate continuum comparison for every nonzero `m_n`. A
degree-zero DGA morphism preserving the inclusion, projection and transfer
homotopy transports every planar-tree operation automatically. The exact q79
translation and Fourier generators preserve the complete 144-to-48 contraction
and induce a faithful order-36 action on the response target. Hence the whole
nontruncating hierarchy is equivariant at once. This is an exact general and
finite theorem, not a continuum promotion: all seven physical endpoint rows
remain open.

The twelfth theorem attacks those seven rows as one system. It proves that
they factor through three same-source packets: geometry plus action (`GAS`),
spectral synthesis (`SYN`) and four-dimensional BV compactification (`BV4`).
The physical `C4` row and rank-102 Galerkin/Feshbach row are deterministic
consequences of `GAS+SYN`, not additional physical source choices. Exact
countermodels show that upper complementary action data, synthesis selection
and physical compactification cannot be inferred from one another. This is a dependency
reduction, not a three-parameter claim: physical acceptance remains `0/3`
typed components and `0/7` rows. The components may be stored together; the
count describes distinct information, not files.

The thirteenth theorem opens the `BV4` packet at the associated-matter lane.
For a graded equivariant internal operator `D_X`, an external causal Dirac
operator `D_Y` and normalized internal modes, it proves

```text
D_tot=D_Y tensor I + Gamma_Y tensor D_X,
D_tot^2=D_Y^2 tensor I + I tensor D_X^2.
```

The internal kernel therefore externalizes exactly as massless
four-dimensional fields, while nonzero internal eigenvalues label the massive
mode operators. Gauge characters and chirality are inherited from the
equivariant graded kernel; the free quadratic action and cotangent BV pairing
reduce exactly; and an internal gap controls the classical complement. The
exact witness has `ker(D_+)=3 tensor H16`, dimension 48, and replays the A46/A50
anomaly, shared-circle and `Z6` rows. This is a universal compiler, not the
selected q79 operator: the full physical `BV4` packet and all interaction
values remain open.

## Run the proof

```powershell
python verify.py
```

The verifier uses only the Python standard library. It rebuilds the packets,
independently checks the `m4` packet in routine mode, reconstructs the eight
higher-jet invariant spaces, the exact `m5` witness and the all-arity recurrence,
checks the all-arity source-promotion contract, executes the seven-row
factorization/Feshbach witnesses, executes the associated-matter product-Dirac
and `3 x 16` BV4 witness, and runs the unit tests.

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
- `HigherJetFiltrationAndTransferredAritySupportTheorem_v1.md`: exact
  all-arity `n-1 J` support theorem, eight-mode invariant-space certificate and
  closed all-arity nontruncation family.
- `AllArityContractionMorphismSourcePromotionTheorem_v1.md`: general
  contraction-morphism theorem, exact all-arity q79 covariance and the strict
  seven-row continuum endpoint contract.
- `SevenRowEndpointFactorizationAndMinimalSourceTheorem_v1.md`: exact
  factorization of the seven endpoint rows through `GAS`, `SYN` and `BV4`,
  exact minimality countermodels and the derived Feshbach/C4 rows.
- `AssociatedMatterProductDiracBVExternalizationCompilerTheorem_v1.md`: exact
  associated-matter zero-mode, representation, free-action, causal-mode and
  complement-gap compiler with a `3 x 16 = 48` witness.
- `ProviderNeutralProjectionSourceQuotientAndQ79NecessityTheorem_v1.md`:
  provider-neutral source quotient, exact non-q79 80-to-48 witness, strict q79
  necessity classification and no-source/no-values countermodels.
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
- `q79_higher_transfer_jet_filtration_source_lock.json`: pinned `m4`, contraction
  and Merkulov `lambda5` boundary for the all-arity support theorem.
- `q79_all_arity_source_promotion_source_lock.json`: pinned finite contraction,
  HYM-naturality, polar-compiler and action/BV boundary sources.
- `q79_seven_row_endpoint_factorization_source_lock.json`: pinned all-arity,
  HYM/Feshbach, action and BV-compactification authorities for the dependency
  theorem.
- `q79_physical_endpoint_three_packet_contract.schema.json`: machine-readable
  same-source input schema for the physical endpoint integration.
- `q79_bv4_associated_matter_externalization_source_lock.json`: pinned H4-T16,
  H4-T18, H4-T21, A46/A47/A50 and shared-circle inputs for the BV4 compiler.
- `q79_bv4_associated_matter_externalization_contract.schema.json`:
  machine-readable same-root `AMK+EXT4+DEN` instance and remaining-row schema.
- `provider_neutral_projection_source_lock.json`: kernel-authority and local
  source lock for the q79/provider classification.
- `provider_neutral_physical_source_contract.schema.json`: machine-readable
  source interface shared by q79, direct-repair, finite-spectral and certified
  universality-class providers.
- `MTT_FIXEDPOINT_GAUGE_GROUNDING_MAP_v1.md`: current fixed-point, A47 gauge,
  locality, duality and dimensions status map.
- `PHILOSOPHICAL_INTERPRETATION_OF_CONSTRAINT_REALISM_v1.md`: disciplined
  philosophical reading, competing ontologies, objections and Bell boundary.
- `CONSTRAINT_REDUCTION_REFERENCE_SYSTEM_v0.md`: candidate common language for
  preprojection rules, compression and transferred higher products.
- `RESEARCH_ROADMAP.md`: ordered route from this identity to a selected MTT
  physical construction.
- `Q79_ETA9_ENDPOINT_UNLOCK_DECISION_PROGRAM_v1.md`: quotient-first,
  goal-oriented decision tree for selecting or obstructing the same-source
  eta9/Deligne/HYM endpoint before expensive full reconstruction.
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
- `q79_higher_transfer_jet_filtration_and_m5_feasibility.packet.json`: generated
  invariant-space, all-arity support/nontruncation and `m5` workload certificate.
- `q79_all_arity_source_promotion.packet.json`: generated all-arity naturality,
  target-covariance and continuum endpoint-contract certificate.
- `q79_seven_row_endpoint_factorization.packet.json`: generated dependency,
  minimality and exact Hessian/Feshbach/C4 certificate.
- `q79_bv4_associated_matter_externalization.packet.json`: generated product-
  Dirac, 48-state representation, action/pairing and complement certificate.
- `provider_neutral_projection_source_quotient.packet.json`: generated source-
  quotient, q79 classification, equivalence witness and value no-go certificate.
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

The immediate finite frontier is no longer an unexplained harmonic projector,
a missing ternary/quaternary correction, or uncertainty about truncation at
any finite arity. The orientation-odd first-jet quotient is forced for every
connection source, and the exact 48-dimensional target retains the complementary
higher-jet classes while carrying a nonzero transferred operation at every
arity `n>=3`. The all-arity support theorem controls the maximal `J` sector. A
complete `m5` table and SI(5) still require state compression or exact covariance
orbits. All-arity covariance no longer requires those tables: it follows from
the exact source/contraction squares. Physical promotion still requires the selected
nonzero-Chern q79 HYM endpoint, analytic domains and pairing, its Green
operator, physical C4 naturality, a `D_fin` intertwiner and certified
finite/continuum error bounds from one selected source.

Those obligations are now organized rather than flat. `GAS` must bind the
selected HYM endpoint to the physical action and normalization; `SYN` must bind
the continuum Hessian to the retained finite sector; and `BV4` must externalize
that same source to the accepted four-dimensional BV fields. Once `GAS+SYN`
exist, the physical symmetry and rank-102/Feshbach rows are computations, not
new source packets. This reduces source-type ambiguity but does not change the
strict physical `0/7` count.

The free associated-matter portion of `BV4` is now organized one level deeper.
Once the selected endpoint exports the graded first-order matter operator,
normalized harmonic basis, reduced Green and gap, `CBF.T13` computes the
charged/chiral four-dimensional carrier and its free causal operators. It does
not supply that endpoint instance, the nonlinear overlap values, the complete
bosonic/gravity stack or the quantum pushforward.

The projection interface is now also separated from its expected geometric
provider. `CBF.T14` proves that source-preserving equivalent realizations give
equivalent projected records and supplies an exact non-q79 benchmark. Thus q79
is not logically necessary for the compiler. It remains an active geometric
provider candidate whose physical sufficiency is open, not a discarded branch.
The same theorem proves that complement thresholds and normalized interaction
values cannot be reconstructed from the retained free kernel alone. A direct
repair/action or finite spectral source may bypass q79 geometry only by filling
the same selected action, synthesis, normalization and BV obligations.

The source-promotion packet passes `39/39` checks and its independent verifier
passes `20/20`. The endpoint-factorization packet passes `50/50` checks and
its independent verifier passes `37/37`. The associated-matter BV4 packet
passes `71/71` checks and its independent verifier passes `47/47`. The
provider-neutral packet passes `40/40` checks and its independent verifier
passes `50/50`. The canonical suite passes 63 unit tests. The
finite `P/G/h` package, q79 harmonic strain globalization, full
signed-direction DGA covariance, universal harmonic first-jet quotient and
all-arity response nontruncation and covariance are closed at their declared tiers. Complete
operation and Stasheff tables from `m5` onward, the selected HYM
endpoint, finite-to-continuum intertwiner and physical-action promotion are
not.
