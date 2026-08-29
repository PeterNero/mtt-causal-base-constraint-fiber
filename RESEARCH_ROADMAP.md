# Research Roadmap

The order matters. Later steps may consume earlier results; they may not rename
missing source data as solved.

## Step 1: Compression algebra

**State:** closed in this repository at `EXACT_GENERAL` and
`EXACT_BENCHMARK` tiers.

Deliverables:

- multiplicativity-defect identity;
- exact leakage formula for compressed commutators;
- norm and approximate-compatibility bounds;
- exact rank-two rational witness;
- locality guardrail for coherent-preserving local algebras.

## Step 2: Fiberwise and unbounded globalization

**State:** open.

Prove the same result for decomposable Hilbert bundles and controlled unbounded
operators with a common invariant core. State measurable-field, domain and
closure hypotheses. Connect the local-net result to the existing MTT locality
descent theorem without duplicating its theorem body.

**Exit:** a fiberwise packet whose compression, commutators and leakage maps are
defined almost everywhere, closable, and compatible with net isotony.

## Step 3: Repair-to-projector theorem

**State:** abstract equivariant theorem closed; selected q79 instantiation open.

Given a nonlinear repair map `F` and a stable fixed point `u_*`, derive `P` as a
Riesz/spectral projector of `D F(u_*)` or of the selected Hessian. Prove its
gap, smooth/decomposable dependence and source provenance. Determine whether
the leakage maps are exactly the off-diagonal second-variation or connection
terms.

**Exit:** one source hash produces `F`, `u_*`, the linearization, gap, `P`, `Q`
and both leakage maps. This is the first step that can materially advance
`B.ACTION.01`.

The repository theorem now closes the general implication

```text
equivariant F + stabilized u_* + isolated tangent cluster
  -> symmetry-preserved Riesz projector.
```

The pinned cohesive finite witness has now been evaluated explicitly. Its
Hessian is `I2`, so the canonical fixed tangent projector is zero. It cannot by
itself furnish the nontrivial physical `P/Q` split required by this exit.

## Step 4: Excluded-sector propagator and higher transfer

**State:** abstract comparison, selected finite Weyl execution, q79 harmonic
globalization, minimal full-covariance DGA, universal harmonic first-jet
quotient, finite transfer through `m4`, an all-arity higher-`J` support theorem
and all-arity nontruncation closed; the full `m5` table, SI(5), complete later
arity tables and continuum q79 execution remain open.

The raw compression defect, Feshbach correction and Hodge-transferred higher
products have now been placed in one exact language:

```text
E_R(S,T)=P S R T P.
```

Raw compression uses `R=Q`; Feshbach uses the excluded resolvent; A-infinity
transfer uses `h=d*G_Q` and signed tree sums. Exact witnesses prove that these
are not directly equal in general. The common architecture is closed, while
the propagator is indispensable.

The selected finite Weyl pair now emits a canonical twisted Koszul differential
and normalized Hilbert-Schmidt pairing. Its exact Hodge package is

```text
P=(P_W, P_W direct-sum P_W, P_W),
G=(G_W, G_W direct-sum G_W, G_W),
h=d*G.
```

The harmonic algebra is strict exterior algebra, so all transferred products
above `m2` vanish. This is a result, not a failed search: the finite center
complex cannot be the source of nonzero physical interactions. Moreover, its
degree-zero rank-96 range is transverse to the separate rank-96 kernel of
`D_fin`; coupling them requires a real Feshbach/transfer step.

The q79 monodromy bridge is now also exact. Full affine `S3` acts by unitary
cochain maps preserving the Hodge contraction. Harmonic `H1` carries two sign
representations, and its Fourier quarter-turn is the shared-root matrix `j`.
Tensoring by `det(E_D)` and `E_D` gives exactly the rank-six q79 strain local
system and `J_DE`. The harmonic exterior product is equivariant.

The full forward-difference DGA does not descend through these canonical
maps: reflection and Fourier product defects are nonzero, and full-chain `C4`
does not commute with all translated holonomies. This is the new sharp
boundary, rather than an unspecified monodromy-naturalness gap.

The minimal signed-direction completion now removes those DGA defects exactly.
It has four directions, dimension 144 and finite covariance group
`(Z3 x Z3) semidirect C4` of order 36. With squared edge norm `1/2`, its Hodge
eigenvalues remain `0,3,6`. The old complex is an isometric reducing cochain
summand and its harmonic image is exactly the orientation-odd `(1,2,1)`
sector.

This completion also exposes the next obstruction. It contains twelve extra
harmonic classes, so it is not quasi-isomorphic to the selected complex. The
selected image is not product closed off harmonics, and orthogonal product
compression is nonassociative. Full covariance is therefore available only
before the unresolved physical mode/product selection.

The harmonic mode selection is now derived at the universal first-jet tier.
The signed-edge space splits canonically into orientation-odd and
orientation-even planes using the spectral projectors of `C4^2`. For every
connection-generated signed transport family, the exact central/even
difference identity places the principal first derivative in the odd plane
and the even plane at axial second-jet order. The twelve extra harmonic classes
are precisely the ideal generated by the even plane, and the selected
`(1,2,1)` harmonic algebra is its strict associative quotient.

This theorem removes an arbitrary harmonic selector only after a source is
known to be first order. It does not manufacture the selected q79 endpoint or
turn the finite qutrit translations into a convergent lattice family.

The finite off-harmonic response problem is now solved through arity three.
The 144-dimensional symmetric DGA strongly deformation retracts onto the
48-dimensional complex formed by the old response lanes plus the complete
twelve-class higher-jet harmonic ideal. The transferred `m2` is nonassociative,
but a computed nonzero `m3` satisfies the arity-three Stasheff identity on all
110,592 basis triples. This replaces the former associativity cutset with an
exact low-arity `A_infinity` structure.

The next arity has now been executed as well. The transferred `m4` is nonzero
on 693,208 basis quadruples and has degree `-2`. The arity-four Stasheff
identity holds on all 3,869,500 degree-admissible quadruples, with the complete
support and digest independently replayed. It vanishes on harmonic quadruples
and with three or more higher-jet inputs, but two higher-jet inputs can
contribute. Therefore the finite hierarchy provably does not truncate at
`m3`.

The maximal higher-jet sector is now controlled at every arity. In each nonzero
mode, mixed one-old/one-`J` transfer excursions span the six-dimensional space
`R_g=image H`, with graded dimensions `(2,3,1)`. This space is invariant under
all left/right `J` homotopy multipliers and terminal `J` multiplication projects
to zero. The resulting planar-tree theorem proves that `m_n` vanishes with
`n-1` or more `J` inputs for every `n>=3`.

An exact selected execution also proves that `m5` is nonzero:

```text
m5(C:0,0,1, C:0,0,1, C:0,0,1, C:1,0,1, C:1,0,0)
  = (1/24 + omega/48) C:2,0,1.
```

This witness lies in an exactly recurrent family. The two parity subsequences
satisfy

```text
m_(2r+3)(x^(2r+1),y,z) = (2+omega)/(4*12^r) C:2,0,1,
m_(2r+4)(x^(2r+2),y,z) = -omega/(8*12^r) C:2,0,1,
```

so a nonzero transferred operation exists at every arity `n>=3`. The finite
structure is proved not to truncate at any finite arity; what remains is full
table/coherence execution, not the nonvanishing truth value.

The full arity-five domain still has 144,443,776 candidates after all proved
cheap cutsets, so the complete operation and SI(5) should proceed by distinct
`H lambda4` state compression and exact covariance-orbit decomposition, not a
raw `48^5` loop.

All-arity covariance is now closed independently of that census. The exact
contraction-morphism theorem proves that one DGA source map preserving `i`, `p`
and `H` transports every `m_n`. Translation and Fourier satisfy those identities
on the complete q79 144-to-48 contraction and generate a faithful order-36
target action. Complete later-arity tables are therefore coherence data, not a
prerequisite for exact source promotion.

**Remaining exit:** instantiate the proved first-jet selector on the selected
continuum q79 HYM complex and construct its full response transfer. The source
must emit the nonzero-Chern endpoint, connection, reduced Green, physical `C4`
naturality and a finite-to-continuum intertwiner with domains, pairing and
certified errors. It must also carry the nonharmonic lanes that reproduce
`D_fin`, either through an associative continuum product or a certified
`A_infinity` transfer. The all-arity theorem reduces exact operation transport
to the endpoint differential/product and contraction squares; approximate
transport must instead use the existing `FSB.03b` defect majorants. At the
finite tier, the optional next coherence calculation is the complete `m5`
table and SI(5). The even higher-jet sector must be
retained, quotiented or interpreted by that same source rather than by
declaration.

The seven endpoint rows are no longer treated as independent work items.
`CBF.T12` proves the exact factorization

```text
GAS -> EP.01, EP.06
SYN -> EP.02, EP.03
GAS+SYN -> EP.04, EP.05
BV4 -> EP.07.
```

The immediate physical order is therefore:

1. bind the selected eta9/HYM endpoint and upper action into `GAS`;
2. construct `SYN` from that exact Hessian and endpoint representation data;
3. execute the now-deterministic physical `C4` and rank-102/Feshbach rows; and
4. construct `BV4` from the same source root.

The three packets are structured source objects, not three scalar knobs. The
physical count remains `0/7` until their actual q79 payloads pass.

The upstream eta9 selection campaign is governed by
`Q79_ETA9_ENDPOINT_UNLOCK_DECISION_PROGRAM_v1.md`. It replaces arbitrary-member
evaluation and premature full-frame reconstruction by an ordered sequence of
primitive quotient detection, one-vector transport, goal-oriented adjoint
readout, certified 122-variable root selection and same-source endpoint
compilation. Its success output is the `GAS` source required by this step; a
certified obstruction is an equally valid branch decision.

The associated-matter part of `BV4` now has an exact source-independent
compiler. `CBF.T13` consumes

```text
AMK  = graded equivariant internal matter operator and normalized kernel,
EXT4 = external causal Dirac packet,
DEN  = product density and pairing normalization,
```

and emits the charged/chiral zero-mode carrier, free action, cotangent pairing,
modewise causal family and complement-gap certificate. Its exact
`3 x 16 = 48` witness proves the compiler is nonempty and compatible with the
A46/A47/A50 representation data.

This changes the best parallel work order. While the q79 worker selects the
physical eta9/HYM root, this repository can:

1. build the bosonic gauge/coframe/Higgs companion externalization compiler;
2. prove the same-source action-density overlap reduction for retained
   interactions and expose every normalization;
3. bind those free operators to the accepted Lorentzian/BV domains; and
4. prepare the massive-mode pushforward contract without asserting a QME
   before the physical action and gap exist.

The physical `AMK`, `EXT4`, density and action instances are still open. No
q79 row is accepted merely because the universal compiler passes.

`CBF.T14` now separates the source interface from one provider. Projection
factors through source-preserving equivalence classes of

```text
root selection + EXT4 + GAS + SYN + AMK + DEN + BV4.
```

The q79 Hull-Strominger branch is one candidate realization of this interface,
not an argument of the projection functor. An exact non-q79 80-to-48 benchmark
disproves logical necessity at compiler tier. Exact threshold and interaction
countermodels prove that a geometric bypass cannot omit the selected action,
complement spectrum, density or normalized interaction tensors.

The new parallel physical route is therefore:

1. `PN.01`: construct a selected direct repair/action and stationary fixed point;
2. `PN.02`: derive its Hessian, domains, projector, reduced Green and causal binding;
3. `PN.03`: derive the normalized 48-state `AMK+DEN` packet from that same root;
4. `PN.04`: emit one held-out invariant interaction or threshold value; and
5. `PN.05`: construct the BV pushforward and compare held-out observables.

The q79 worker should continue independently. If both routes close, compare
them through the provider-neutral quotient. Agreement of the complete source
packet would establish a universality result; agreement of dimensions or
indices alone would not.

`CBF.T15` closes `PN.01` only for the normalized free associated-matter
subclass. The residual `Phi(a)=J a` has a stationary critical locus, exact
multiplier action, positive repair normal and rank-48 limiting projector. It
also proves the conditional source-index statement `4 source copies - 1
residual copy = 3 retained family copies`. This does not close physical
`PN.01`: selection of the source class and its physical normalization remain
open.

`CBF.T16` now closes the mechanism question behind the first two items, with a
sharp correction. A regular nonlinear residual by itself cannot modify the
zero-pressure multiplier or repair Hessian: surjectivity forces the multiplier
to zero. The required quadratic datum is the pair

```text
(residual curvature D2psi, nonzero normal closure pressure p n0).
```

The exact FSB.04e/04f finite composition preserves gauge/shared-circle
covariance, raises the bordered rank `32 -> 56`, and breaks the free family
stabilizer `U(3) -> U(1)`. Its two nonzero singular levels also prove that this
first response cannot yield three positive family magnitudes. The result is
conditional because CBF.T15 and the q79 response pair are not yet known to
come from one physical source.

The direct-source frontier is therefore no longer "add nonlinear terms." It is:

1. construct one source-hashed constrained or cyclic action emitting `J`,
   `D2psi`, the neutral pressure/order background and its physical scale;
2. prove the same-root intertwiner to the selected response geometry;
3. derive a gauge-invariant Lorentz/Higgs left-right Yukawa second variation;
4. derive a sector-resolved spectral law or cross-sector relation reducing the
   nine FSB.04g scalar coordinates;
5. emit one held-out source-normalized mass, interaction or threshold scalar;
6. externalize the same tensors through the CBF.T13/T14 BV contract.

Until item 5 succeeds, the result remains an exact structural source compiler
rather than true Standard Model value closure.

`CBF.T17` now closes item 1 at the finite algebraic and classical-projective
tier, with one remaining physical qualifier. The minimal field-only action is
the affine normal tadpole, and its exact graph pullback produces the lower A/B
family quadratic. All nonzero pressure magnitudes form one classical
projective class, so no new continuous dimensionless pressure-shape parameter
is introduced. The physical action density and overall quantum normalization
are not selected.

`CBF.T18` removes two apparent source obligations from that qualifier.
A46/A47/A50 already select the unique invariant neutral line, while a frame
and the separate factors `epsilon` and `B` are one `GL(1,C)` quotient orbit.
A74 already fixes the finite family functional to `Tr/3`. The frame-invariant
datum is the contracted `H_resp`, whose exact squared Frobenius norm is 192.
The physical action match is therefore the single equation

```text
H_eff=c_action H_resp,
c_action=<H_resp,H_eff>_F/192.
```

Normalized finite data cannot select `c_action`; it must be emitted by the
physical action/density endpoint.

CBF.T19 further proves that Feshbach covariance alone lands in a
nine-dimensional routed Hermitian module. The exact route to the response
line is the same-root relative comparison

```text
T_rel=H_resp,act^-1 H_eff,act,
```

whose commutation with the selected family-lane comparison algebra is
necessary and sufficient for `H_eff,act=c_action H_resp,act`. The complete
finite reduction is `36 -> 18 -> 9 -> 1`; each arrow now has a named source
obligation rather than being hidden inside "equivariance."

CBF.T20 now discharges the finite normalized form of the last source
obligation. The pinned Weyl primitives `P,X,Z,F3` generate the shift and phase
blocks as first variations of positive Gram families, and one neutral shared
coordinate reduces the fixed-shape source space `4 -> 2 -> 1`. The resulting
relative comparison is exactly `T_rel=I`. This is independent of eta9/HYM
endpoint data and uses no observed or fitted coefficient.

CBF.T21 now closes the next general and algebraic subclauses without waiting
for eta9. `H_derived` may be inserted as a smooth order-zero endomorphism of
any normally hyperbolic response operator, preserving its metric causal cone.
The primitive coupling `C=P tensor I16` and complement `I48` give a nontrivial
exact `96 -> 48` Schur reduction and graph synthesis. The existing q79
equicausal free-BV chart theorem supplies one conditional causal carrier.
However, the finite Gram root and causal chart root are still two inputs, and
the dimensionful response coefficient and physical field typing are open.

The remaining order is now:

1. prove that the finite Gram root and a causal action/background root are one
   selected upper source, or construct a new single-root provider satisfying
   both contracts;
2. derive the dimensionful coefficient `mu^2` and the physical density/action
   normalization from that source;
3. type the response into a gauge-invariant Lorentz/Higgs left-right Yukawa or
   another explicit physical field second variation;
4. complete same-root BV4 insertion and, for the q79 provider route, continuum
   HYM synthesis, projection and certified finite-error bounds;
5. use the now exact relative-intertwiner and Schur theorems to certify the
   complete physical residual and recover `c_action`;
6. externalize the accepted action and density through CBF.T13/T14;
7. derive a sector-resolved spectral law or cross-sector relation reducing the
   nine FSB.04g scalar coordinates;
8. emit one held-out source-normalized mass, interaction or threshold scalar.

The next physical theorem must discharge item 1 or 2. Another normal-frame or
finite-trace packet cannot do so: CBF.T18 proves those choices are already
quotiented or unique, and proves the absolute scale nonidentifiable before the
physical endpoint exists.

## Step 5: Constraint curvature and gauge stabilizer

**State:** abstract stabilizer/faithful-quotient descent and finite
pressure-curvature activation closed; physical same-root intertwiner and
curvature identification open.

Test whether the antisymmetrized leakage form is the curvature of a natural
connection on the retained bundle, rather than merely naming it curvature.
Then characterize vertical automorphisms preserving `F`, its connection and
`P`. Compare the stabilizer exactly with the already established `A47` native
bundle group and its diagonal `Z6` kernel.

**Exit:** a commuting diagram from upper automorphisms to the faithful gauge
group, preserving connections, Hessians and holonomies.

The exact finite witness already verifies a nontrivial central kernel and
faithful quotient. It is not the A47 group and supplies no physical connection.

## Step 6: Selected quantum pair and normalization

**State:** open.

Search the selected q79 source for an upper pair whose physical compression is
the candidate conjugate pair. The pair may commute upstairs only if Step 1's
leakage term supplies the full lower commutator. Determine the symplectic/action
normalization and whether a canonical CCR appears exactly, asymptotically or
not at all.

**Exit:** selected operators, domains, state space and normalization from one
source, with no observed quantum constant used to select the construction.

Failure is informative: the program must then treat noncommutativity as an
independent upper structure instead of a consequence of constraint reduction.

## Step 7: Entanglement and uncertainty

**State:** structurally separated, physically open.

- Use Step 2 to preserve base microcausality.
- Select a nonfactorizing state and local instruments independently.
- Derive Robertson-type uncertainty only after Step 6 supplies the physical
  commutator and domains.
- Keep operational output probability separate from objective actualization.

**Exit:** a same-source Bell/measurement packet with local instruments,
no-signalling, state provenance and an explicit ontology boundary.

## Step 8: QFT, gravity and extra-dimension verdict

**State:** open and dependent on `B.ACTION.01`, `B.GEO.01` and `B.QFT.02`.

Construct the selected Lorentzian action and renormalized transfer. Only then
test whether all vertical directions satisfy the five constraint-fiber tests in
the charter. A vertical propagating spectrum or physical KK tower falsifies the
strong "not extra spacetime" interpretation for that sector.

**Exit:** either a controlled causal-base/constraint-fiber physical theory, or
a precise mixed verdict identifying which internal directions are constraints
and which are physical degrees of freedom.
