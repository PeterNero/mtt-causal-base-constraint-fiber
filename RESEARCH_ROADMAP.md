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

**State:** abstract comparison and selected finite Weyl execution closed;
continuum q79 execution open.

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

**Remaining exit:** one selected continuum q79 differential and pairing must
map to this finite contraction through a cochain/product intertwiner, carry the
nonharmonic response lanes that reproduce `D_fin`, and provide analytic
continuum-to-finite error control.

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
