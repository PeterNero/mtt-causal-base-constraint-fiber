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
quotient and finite transfer through `m3` closed; higher-arity and continuum
q79 execution open.

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
exact low-arity `A_infinity` structure. Higher operations have not yet been
computed or proved to vanish.

**Remaining exit:** instantiate the proved first-jet selector on the selected
continuum q79 HYM complex and construct its full response transfer. The source
must emit the nonzero-Chern endpoint, connection, reduced Green, physical `C4`
naturality and a finite-to-continuum intertwiner with domains, pairing and
certified errors. It must also carry the nonharmonic lanes that reproduce
`D_fin`, either through an associative continuum product or a certified
`A_infinity` transfer. At the finite tier, compute `m4` and higher or prove a
truncation theorem. The even higher-jet sector must be retained, quotiented or
interpreted by that same source rather than by declaration.

## Step 5: Constraint curvature and gauge stabilizer

**State:** abstract stabilizer/faithful-quotient descent closed; physical
intertwiner and curvature identification open.

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
