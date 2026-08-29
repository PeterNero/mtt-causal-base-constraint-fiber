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

The fifteenth theorem supplies an exact direct source for that free witness.
For one family-blind coisometric residual

```text
J : C^4 tensor H16 -> H16,
```

rank-nullity gives `ker J=C^3 tensor H16`, and three retained family copies
occur exactly at source multiplicity four within this one-residual-copy class.
Every normalized such `J` is `U(4)`-equivalent to `[I16 0 0 0]`. Its H4-T9
multiplier Hessian is precisely the existing `80 x 80` CBF.T13 operator, its
normal square gives the positive repair Hessian, and the exact repair
semigroup converges to the 48-state projector. This is a conditional reverse-
source result, not an independent prediction that nature starts with four
copies. Its residual `U(3)` symmetry also proves a no-go: the free source alone
cannot split family masses or select mixing and CP data.

The sixteenth theorem determines exactly what can and cannot activate family
curvature in that source. For a regular graph residual

```text
Phi(n,k)=n+psi(k),
```

surjectivity forces the multiplier to vanish at every critical point of the
pure multiplier action. Consequently, nonlinear residual jets are invisible
in both the zero-pressure multiplier Hessian and the quadratic repair cost.
A nonzero normal load changes this: at pressure `p n0`, the tangent Hessian is

```text
<u,H_p v>=p<n0,D2 psi(0)[u,v]>.
```

An exact A46/A47/A50-compatible witness uses the FSB.04e/04f family responses.
It raises the `80 x 80` bordered-Hessian rank from `32` to `56`, preserves the
gauge and shared-circle actions, and reduces the common family stabilizer from
`U(3)` to `U(1)`. This is a real activation result, but not a mass result: the
operator has only two nonzero singular levels, the physical pressure and
same-root source are unselected, and Lorentz/Higgs/Yukawa typing plus all nine
charged magnitude values remain open.

The seventeenth theorem supplies the missing finite zero-section action and
proves why it is minimal. The canonical cotangent term `<lambda,Phi>` vanishes
when its dual field is zero and cannot activate curvature at a regular point.
Adding the field-only affine normal term

```text
U_ell(n,k)=-ell(n)
```

is necessary and sufficient in the minimal affine class. On the nonlinear
closure graph it becomes

```text
U_ell(-psi(k),k)=ell(psi(k)),
```

so a linear upper action produces the full lower quadratic family response.
The exact finite action has real bordered dimension 160, rank 112 and kernel
dimension 48. Moreover, `L_p(n,k,p mu)=p L_1(n,k,mu)` proves that all nonzero
pressure magnitudes are one unoriented classical projective class. Pressure
therefore adds no continuous dimensionless family-shape knob; one overall
physical action scale, density and the complete physical typing remain open.

The eighteenth theorem removes an artificial part of that source obligation.
A46/A47/A50 select the unique invariant neutral line `N^c subset H16`, but a
unit frame in that line is conventional. The exact change

```text
(B,epsilon,n,lambda)->(aB,epsilon/a,an,lambda/a)
```

leaves both the contracted Hessian `H=epsilon o B` and the full affine action
unchanged. Every nonzero one-dimensional factorization has one `GL(1,C)`
orbit. A74 also fixes the finite family measure to `Tr/3`. The physical exit is
therefore reduced to `H_eff=c_action H_resp` plus the same-root BV density,
with the prospective coefficient formula
`c_action=<H_resp,H_eff>_F/192`. The endpoint and coefficient remain open.

## Run the proof

```powershell
python verify.py
```

The verifier uses only the Python standard library. It rebuilds the packets,
independently checks the `m4` packet in routine mode, reconstructs the eight
higher-jet invariant spaces, the exact `m5` witness and the all-arity recurrence,
checks the all-arity source-promotion contract, executes the seven-row
factorization/Feshbach witnesses, executes the associated-matter product-Dirac
and `3 x 16` BV4 witness, independently reconstructs the closure-pressure
family Hessian, reconstructs the affine zero-section action and its realified
rank/projective-pressure boundaries, reconstructs the normal-frame quotient,
finite trace and action-scale residual, and runs the unit tests.
It also reconstructs the routed 48-dimensional relative Gram family, checks
the canonical odd supercharge and an independent graded product-square
witness, and verifies the one-universal-scale orbit.

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
- `MinimalOneConstraintMultiplierSourceAndThreeFamilyIndexTheorem_v1.md`:
  exact minimal one-constraint family index, unitary source classification,
  multiplier/repair identity, projection flow and free-family no-go.
- `ClosurePressureFamilyHessianActivationAndRegularMultiplierNoGoTheorem_v1.md`:
  regular-multiplier zero-pressure no-go, exact closure-pressure activation,
  finite family-response symmetry reduction and magnitude boundary.
- `AffineZeroSectionActionAndProjectiveClosurePressureUniquenessTheorem_v1.md`:
  zero-section necessity, graph-pullback action, nonzero-pressure projective
  uniqueness and exact finite realified action witness.
- `NormalFrameQuotientAndActionIntertwinerMinimalDataTheorem_v1.md`: unique
  invariant normal line, exact `GL(1,C)` factorization quotient, finite trace
  uniqueness and minimal physical Hessian-intertwiner exit.
- `EquivariantFeshbachOneDimensionalResponseTheorem_v1.md`: exact response
  module reduction and scalar relative-intertwiner criterion.
- `WeylGramClosureRepairRelativeResponseSourceTheorem_v1.md`: primitive
  Weyl-Gram derivation of the normalized finite response line.
- `CausalWeylGramAuxiliaryFeshbachLiftTheorem_v1.md`: order-zero causal lift
  and exact nontrivial 96-to-48 auxiliary Schur synthesis.
- `RelativeProductSuperchargeSingleOperatorSourceTheorem_v1.md`: canonical
  odd closure-repair supercharge, graded causal product, neutral-relative
  square and one-universal-metrology-scale theorem.
- `PhysicalYukawaIncidenceKO6HessianCompressionTheorem_v1.md`: exact A48/A51
  four-channel incidence, KO6-real physical completion and CBF.T22
  target/source Hessian compression.
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
- `direct_one_constraint_multiplier_source_lock.json`: pinned CBF.T13/T14,
  H4-T9/T10/T15 and A46/A47/A50 source boundary for the direct source theorem.
- `direct_one_constraint_multiplier_source_contract.schema.json`: strict
  conditional contract for one normalized four-to-one typed residual.
- `closure_pressure_family_hessian_activation_source_lock.json`: pinned
  CBF.T15 and FSB.04e/04f/04g theorem and packet provenance.
- `closure_pressure_family_hessian_activation_contract.schema.json`:
  machine-readable pressure, curvature, source-provenance and physical-typing
  acceptance contract.
- `affine_zero_section_action_source_lock.json`: pinned CBF.T16, H4 action/
  cotangent boundaries and FSB.04e/04f/04g response sources.
- `affine_zero_section_action_contract.schema.json`: machine-readable closure
  graph, zero-section action, projective pressure and physical-typing contract.
- `normal_frame_action_intertwiner_source_lock.json`: pinned CBF.T17,
  A46/A47/A50, A74/A86, FSB.04e/04f and BV-density boundary sources.
- `normal_frame_action_intertwiner_contract.schema.json`: machine-readable
  normal-line quotient, finite trace and physical Hessian-intertwiner contract.
- `relative_product_supercharge_source_lock.json`: pinned finite, causal,
  continuum-SM, product-Dirac and metrology inputs for CBF.T22.
- `relative_product_supercharge_contract.schema.json`: strict single-operator
  provenance, scale and physical-boundary contract.
- `physical_yukawa_hessian_source_lock.json`: pinned CBF.T20/T22, A46-A51,
  A86, q79 continuum-SM and Lorentzian-hyperbolic sources for CBF.T23.
- `physical_yukawa_hessian_contract.schema.json`: strict finite physical
  Yukawa-Laplacian typing and selected-endpoint boundary contract.
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
- `direct_one_constraint_multiplier_source.packet.json`: generated exact
  family-index, action/repair, flow, descent and parameter-boundary certificate.
- `closure_pressure_family_hessian_activation.packet.json`: generated exact
  multiplier no-go, pressure activation, rank, symmetry and value-boundary
  certificate.
- `affine_zero_section_action.packet.json`: generated exact affine-action,
  graph-pullback, pressure-projective, real-rank and boundary certificate.
- `normal_frame_action_intertwiner_reduction.packet.json`: generated exact
  normal-frame quotient, trace, response-norm and scale-recovery certificate.
- `build_constraint_compression_leakage.py`: deterministic packet builder.
- `verify_constraint_compression_leakage.py`: independent packet verifier.
- `build_closure_pressure_family_hessian_activation.py`: deterministic CBF.T16
  packet builder.
- `verify_closure_pressure_family_hessian_activation.py`: independent CBF.T16
  reconstruction and boundary verifier.
- `build_affine_zero_section_action.py`: deterministic CBF.T17 packet builder.
- `verify_affine_zero_section_action.py`: independent CBF.T17 action,
  realification and projective-pressure verifier.
- `build_normal_frame_action_intertwiner_reduction.py`: deterministic CBF.T18
  quotient, trace and endpoint-coefficient packet builder.
- `verify_normal_frame_action_intertwiner_reduction.py`: independent CBF.T18
  reconstruction and physical-boundary verifier.
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

`CBF.T15` now fills the free direct-source subclause. It proves that the
CBF.T13 `80 -> 48` operator is the normalized H4-T9 multiplier Hessian for the
minimal one-residual-copy, family-blind source compatible with the A46 target.
Its repair flow converges exactly to the retained carrier, with no continuous
dimensionless matrix parameter after source-frame quotient. This does not
promote a physical source: the four-copy premise is reverse-derived from A46,
one overall physical scale is unselected, and the exact `U(3)` stabilizer
forbids family splitting until selected nonlinear same-source tensors enter.

`CBF.T16` closes the first nonlinear mechanism question and rejects the naive
one. Higher residual terms alone cannot change the regular zero-pressure free
Hessian. The exact missing activation datum is a residual second fundamental
form paired with nonzero normal closure pressure. Composing CBF.T15 with the
source-pinned FSB.04e/04f matrices gives an exact finite witness: the bordered
rank changes `32 -> 56`, the free family stabilizer changes `U(3) -> U(1)`,
and the CP-sensitive finite orientation survives while A47 gauge and A50
shared-circle covariance are preserved. Its two nonzero singular levels prove
that this first response still cannot provide three family magnitudes.

This composition is deliberately conditional. No theorem yet says that one
physical root emits the direct residual, the finite q79 response pair and the
normal pressure. The pressure scale, Lorentz/Higgs left-right typing and nine
charged values remain open, so physical acceptance stays `0/3` packets and
`0/7` rows.

`CBF.T17` closes the finite action-form and parameter-class questions. The
minimal field-only completion is the affine normal tadpole, and restricting it
to the curved closure graph yields exactly `1/2 Re<k,H_resp k>`. Together with
the canonical multiplier term, this gives one finite polynomial that emits
`J`, the response curvature, normalized nonzero pressure and the activated
family Hessian. Its real bordered Hessian has exact inertia `(48,64,48)`.

All nonzero pressure magnitudes are related by a multiplier-coordinate change
and overall action rescaling. Hence this tier has zero new continuous
dimensionless pressure-shape parameters. This does not select the physical
overall action normalization or density, and the finite polynomial is still
assembled from locked sources rather than emitted by one selected physical
endpoint. Physical acceptance remains unchanged.

`CBF.T18` proves that the separately displayed normal covector and curvature
factor are not independent source values. A46/A47/A50 select one invariant
complex normal line; all nonzero frames and factorizations of the same
contracted response lie in one exact `GL(1,C)` orbit and give literally the
same affine action. The A74 Weyl commutant theorem fixes the normalized family
functional to `Tr/3`. The routed response has exact rank 24, Frobenius norm
squared 192 and normalized full trace square 4.

The action-side physical exit is now one same-root equality
`H_eff=c_action H_resp` and the BV density/compactification map. If an endpoint
exists, `c_action` is uniquely computed by Frobenius contraction. Its value
cannot be recovered from normalized finite data alone, and no endpoint or
physical row is promoted here.

`CBF.T19` proves the next exact operator-theory step and corrects an overly
optimistic shortcut. Equivariant synthesis and an invertible equivariant
excluded block make the Feshbach effective Hessian equivariant. But the actual
selected lane-parity/Fourier symmetry leaves nine Hermitian directions. The
complete exact finite module ladder is

```text
36 gauge-sector directions
 -> 18 Fourier-paired directions
 -> 9 universal routed directions
 -> 1 selected relative-response line.
```

The last arrow is equivalent to requiring
`H_resp,act^-1 H_eff,act` to commute with the selected full family-lane
comparison algebra, whose commutant is exactly scalar. A rational
nonreducing witness recovers scale `7/3` with zero residual, while an
equivariant identity-matrix negative control proves that ordinary symmetry is
insufficient. The theorem therefore reduces the endpoint to a same-root
source-intertwining statement plus one BV-normalized scalar; it does not
accept a physical packet.

`CBF.T20` constructs that last line at the normalized finite-source tier
without relying on eta9/HYM endpoint output. The exact source is one shared
neutral deformation of the pinned Weyl frame:

```text
Y_s(t)=-P+t(I+X),
Y_p(t)=-P+t(I+Z).
```

The first variations of `Y_alpha(t)Y_alpha(t)^*` are exactly the shift and
phase response blocks, and universal routing gives the prior rank-24
`H_resp`. The source-coordinate reduction is `4 -> 2 -> 1`, while the active
relative comparison is `T_rel=I6`. The primitive hash excludes the target
response, and independent verification reconstructs the operators from
hard-coded exact field entries.

This does not promote a physical endpoint. The finite identity synthesis is
only an algebraic benchmark; causal-base selection, continuum SYN data, BV4
density and the absolute action scale remain open. Physical acceptance stays
`0/3` packets and `0/7` rows.

`CBF.T21` supplies the first nontrivial causal auxiliary lift of that source.
On a normally hyperbolic response bundle,

```text
L_mu=L0+mu^2 H_derived
```

has the same metric principal symbol because the response is order zero. The
already closed q79 Green-hyperbolic/equicausal free-BV chart theorem provides
one conditional causal carrier. The primitive involution gives

```text
C=P tensor I16,
K_mu=[[L_mu+C^*C,C^*],[C,I48]],
```

whose auxiliary Schur complement and graph pullback are exactly `L_mu`. The
normalized finite witness is `96 -> 48`, with upper rank 72 and kernel 24.
The auxiliary action is transported by `g_aux=CgC^*`, so the coupling and
synthesis are exact intertwiners.

This closes causal-form and nontrivial algebraic-SYN subclauses, not a
physical endpoint packet. The finite and causal roots are still distinct;
`mu^2`, physical background selection, Lorentz/Higgs/Yukawa typing,
same-root BV4 insertion and continuum HYM error control remain open.

`CBF.T22` removes that finite/causal separation at the mathematical operator
tier. With

```text
Y(t)=-[P tensor I16]
     +t[(I+Z) tensor R_phase+(I+X) tensor R_shift],
D_F(t)=[[0,Y(t)^*],[Y(t),0]],
```

the target block of `D_F(t)^2` has first variation `H_derived`. The graded
causal product

```text
D_Lambda(t)=D_Y tensor I96+Gamma_Y tensor Lambda D_F(t)
```

has no mixed square term, and its neutral-relative target derivative is
exactly `Lambda^2 H_derived`. Thus `mu^2=Lambda^2`; there is no separate
response-scale knob. The absolute scale still has the proved one-dimensional
metrology orbit. At the adopted one-primitive tier it is shared as
`Lambda=E0=1/L0`, with no numerical value selected and no sector-specific
scale.

The composite root is deterministic and excludes the target response, but an
upper-MTT theorem has not selected it as the physical root. Physical
Lorentz/Higgs/Yukawa identification, continuum HYM transport and BV
pushforward remain open, so physical acceptance stays `0/3` and `0/7`.

`CBF.T23` now closes the finite physical field-typing part of that statement.
In the A46 ordering

```text
H16=Q(6)+u^c(3)+d^c(3)+L(2)+e^c+N^c,
```

the A48/A51 one-Higgs incidence gives orthogonal partial isometries

```text
V_phase:{u^c,e^c}->{Q_up,L_down},
V_shift:{d^c,N^c}->{Q_down,L_up}.
```

Inserting the CBF.T20 families into these channels produces a self-adjoint,
odd and `J_F`-real `96D` physical finite Dirac family. The derivative of its
square has left-target and right-source compressions exactly equal to the
CBF.T22 pair `H_-` and `H_+`. At neutral radial Higgs amplitude `h`, the target
coefficient is `h^2`; at the adopted one-primitive tier
`h=Lambda=E0=1/L0`, so `mu^2=Lambda^2=h^2` without a sector scale.

This is a finite gauge-covariant Yukawa-Laplacian identification. It is not a
scalar Higgs-potential Hessian, a numerical vacuum selection or a measured
mass prediction. Upper-root selection, continuum HYM transport and physical
BV/QME remain open; endpoint acceptance therefore stays `0/3` and `0/7`.

The source-promotion packet passes `39/39` checks and its independent verifier
passes `20/20`. The endpoint-factorization packet passes `50/50` checks and
its independent verifier passes `37/37`. The associated-matter BV4 packet
passes `71/71` checks and its independent verifier passes `47/47`. The
provider-neutral packet passes `40/40` checks and its independent verifier
passes `50/50`. The direct multiplier-source packet passes `57/57` checks and
its independent verifier passes `68/68`. The closure-pressure packet passes
`54/54` checks and its independent verifier passes `59/59`. The canonical
affine-action packet passes `60/60` checks and its independent verifier passes
`90/90`. The normal-frame packet passes `65/65` checks and its independent
verifier passes `108/108`. The equivariant Feshbach packet passes `48/48`
checks and its independent verifier passes `58/58`. The Weyl-Gram direct-source
packet passes `61/61` checks and its independent verifier passes `79/79`. The
causal auxiliary-lift packet passes `56/56` checks and its independent verifier
passes `89/89`. The relative product-supercharge packet passes `68/68` checks
and its independent verifier passes `77/77`. The physical Yukawa-Hessian
packet passes `90/90` checks and its independent verifier passes `91/91`. The
canonical suite passes 114
unit tests. The
finite `P/G/h` package, q79 harmonic strain globalization, full
signed-direction DGA covariance, universal harmonic first-jet quotient and
all-arity response nontruncation and covariance are closed at their declared tiers. Complete
operation and Stasheff tables from `m5` onward, the selected HYM
endpoint, finite-to-continuum intertwiner and physical-action promotion are
not.
