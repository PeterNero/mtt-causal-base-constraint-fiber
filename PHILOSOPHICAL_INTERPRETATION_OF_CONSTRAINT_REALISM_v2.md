# A Philosophical Interpretation of Causal-Base Constraint Realism v2

## Local events, global admissibility, and the projection of physical structure

## Abstract

This paper develops a philosophical interpretation of Modal Triplet Theory
(MTT) in which ordinary physical events and causal interactions occur on a
four-dimensional base, while a structured fiber over that base records the
ways a local configuration can be continued, compared, repaired, and admitted
as part of one coherent physical history. The fiber is not assumed to be a
second spacetime. Its coordinates may instead represent phase, orientation,
internal physical modes, gauge comparison, or constraint data. Which of these
roles is physical must be decided by propagation, energy, locality, and
observable-action tests rather than by the mere presence of extra coordinates.

The central dynamical proposal is that closure should be read first as a repair
process. A nonlinear repair residual has fixed points; its linearization at a
fixed point gives a tangent operator; an isolated spectral sector gives a
projector; and compression to that sector produces the lower operators seen by
physical observers. In this picture, particles can be persistent patterns of
repair, wave and particle descriptions can be complementary readouts of one
retained state, gauge structure can descend from source symmetry through a
faithful quotient, and some lower incompatibility can arise from excursions
through an excluded constraint sector. Local causal propagation and global
state nonseparability are thereby kept mathematically distinct.

This is an interpretation of a mixed-status research program, not a declaration
that its physical construction is complete. Exact general theorems already
connect compression, leakage, fixed-point linearization, spectral projection,
and gauge descent. Established MTT authorities also provide a structural
Standard Model gauge quotient and a closed operational Born source on a
declared recorder domain. The selected continuum repair action, physical q79
HYM endpoint, complete local quantum field theory, universal apparatus family,
and no-knob precision values remain open. The preferred ontology is therefore
moderate structural realism joined to a process account, held conditionally
until one source construction selects the complete physical chain.

## 1. Scope and claim discipline

This paper asks what the current MTT mathematics could mean if its central
structures are physically realized. It does not own the mathematical theorems
it cites, and it does not promote an abstract or finite theorem into a selected
physical result.

Four labels are used throughout:

| Label | Meaning in this paper |
|---|---|
| **Exact** | A mathematical statement proved under its stated hypotheses. |
| **Established** | A result accepted by the current MTT research ledger at its declared physical or structural tier. |
| **Conditional** | A construction that works if an explicitly missing source, endpoint, or analytic hypothesis is supplied. |
| **Interpretive** | An ontological or explanatory reading that is compatible with the mathematics but is not entailed by it. |

The distinction matters. An exact theorem about all orthogonal projectors does
not select the projector used by nature. A finite benchmark can prove that a
mechanism is possible without proving that the universe instantiates it. A
structural gauge derivation can identify the correct global group without
already supplying all of its dynamics. A closed operational probability law on
one recorder domain does not settle the ontology of every measurement.

The status statements in this version are locked to the research model
generated on 2026-08-31 with state hash
`5fdba232d862a95c164603f3156f0cfb8f8abed50af0756edc1618457b5d1f45`.
They are included to prevent philosophical language from outrunning the proof
ledger. Later technical results should update the status table, not silently
rewrite the meaning of the earlier words.

## 2. The central picture

A compact statement of causal-base constraint realism is:

> Reality is locally eventful and globally admissible. Events and causal
> interactions occur on a four-dimensional spacetime base. The structure over
> each event describes the ways a configuration can be continued, compared,
> repaired, and made compatible with the whole. Persistent objects are stable
> invariant patterns of that continuing process.

The phrase **causal base** says where physical localization and causal order
live. The phrase **constraint fiber** says that not every coordinate appearing
in the upper description should automatically be interpreted as another place.
The phrase **constraint realism** adds a cautious ontological commitment: the
invariant admissibility relations may be physically real even when a particular
choice of fiber coordinates is not.

This is a one-world view unless further physics says otherwise. The upper
structure is not presumed to be a hidden universe running alongside the visible
one. It is closer to the organized space of ways in which this world can remain
coherent. Some upper degrees of freedom may nevertheless turn out to be genuine
internal physical fields. The interpretation must allow that mixed verdict.

## 3. One world, several mathematical levels

The proposal becomes clearer when its levels are separated.

### 3.1 The causal base

Let `M` denote a four-dimensional Lorentzian spacetime, or a suitable causal
generalization. Points and regions of `M` label where events occur. The causal
cone on `M` determines which interventions can influence which later events.
Local quantum field algebras, detector couplings, and records are assigned to
regions of this base.

The claim that `M` is the causal base is stronger than saying that four
coordinates are convenient. It assigns four-dimensional spacetime the jobs of
localization, causal propagation, inertial comparison, and the initial-value
problem.

### 3.2 The upper carrier

Let

```math
\pi:E\longrightarrow M
```

be a bundle or bundle-like carrier. A fiber `E_x` can contain phase,
orientation, internal representation, deformation, closure, or comparison
data associated with the event `x`. A section `u` assigns compatible upper data
over a region of the causal base.

The word "upper" denotes descriptive level, not vertical location. Nothing in
the bundle notation alone shows that an inhabitant could travel from one fiber
coordinate to another as it travels through space.

### 3.3 Admissible sections

Not every formal section need represent a possible physical state. The theory
must specify an admissible class, perhaps by equations, constraints, boundary
conditions, topology, or a variational principle. Schematically,

```math
\mathscr C_{\rm adm}
=\{u\in\Gamma(E):\mathcal F(u)=0
\text{ and the required global conditions hold}\}.
```

This is the first sense in which the whole can constrain the parts. A local
fiber value may be algebraically allowed but fail to extend to an admissible
global section.

### 3.4 Physical reduction

Physical observers do not necessarily access every upper component. A selected
projector, quotient, decoder, or instrument maps upper data to accepted physical
states and observables. That reduction is not a cosmetic final step. It can
change products, expose gauge equivalences, and generate effective
incompatibility. The source of the reduction must therefore be derived rather
than chosen because it reproduces desired lower physics.

## 4. What exists on this interpretation?

The proposed ontology has four candidate commitments.

1. **Events:** localized physical occurrences on the causal base.
2. **Processes:** causal evolution, interaction, and repair connecting possible
   local continuations.
3. **Invariant structures:** fixed sectors, holonomies, gauge-invariant
   relations, and stable response patterns.
4. **Records:** durable, physically accessible correlations produced by local
   interactions.

This is not pure substance ontology. A particle need not be a tiny bearer of
properties that remains numerically identical beneath every change. Nor is it
pure relationism in which no events or systems exist. The middle position is
that systems are real, while their identity and properties depend partly on
invariant relational and dynamical structure.

The ontology is also selective. A coordinate representative, gauge label, or
discarded mode need not be independently real merely because it appears in an
equation. The natural ontological candidates are structures preserved by the
relevant transformations and expressed in physical observables.

## 5. Closure as repair rather than a static shape

The decisive conceptual move from v1 is to treat closure first as a verb.
Geometry can describe a closed configuration, but closure itself concerns
whether a configuration can continue coherently when it is disturbed.

Let a nonlinear residual

```math
\mathcal F:U\subset\mathcal H\longrightarrow\mathcal H
```

measure failure of admissibility. A repair evolution can be written
schematically as

```math
\frac{d u}{d s}=-\mathcal F(u).
```

Here `s` is initially an auxiliary repair parameter. It is not Lorentzian time,
not the shared phase circle, and not automatically a physical dissipation time.

A closed configuration `u_*` obeys

```math
\mathcal F(u_*)=0.
```

Linearizing near it gives

```math
u=u_*+\delta u,
\qquad
\frac{d\delta u}{d s}=-J_*\delta u+O(\|\delta u\|^2),
\qquad
J_*=D\mathcal F(u_*).
```

At this point the operator is no longer postulated as the beginning of the
story. It is the tangent map of repair at an admissible background. When the
linearized problem is well posed, its first response is controlled by a
semigroup such as

```math
e^{-sJ_*}.
```

This explains why heat-kernel and resolvent mathematics can appear naturally.
They describe how deviations from closure are propagated, damped, or retained
in the tangent approximation.

The interpretation is attractive, but its physical form remains conditional.
The current program has exact abstract and finite repair constructions. It has
not yet selected one continuum repair law that simultaneously supplies the q79
background, Lorentzian action, normalization, physical projector, and all
observables.

## 6. From repair to the retained physical sector

Suppose an isolated spectral cluster of `J_*` is enclosed by a contour
`Gamma`. The corresponding Riesz projector is

```math
P=\frac{1}{2\pi i}\int_\Gamma(zI-J_*)^{-1}\,dz,
\qquad Q=I-P.
```

This gives a principled order of explanation:

```text
one source or action
  -> nonlinear repair residual
  -> selected fixed background
  -> tangent operator
  -> spectral gap
  -> retained projector P and excluded sector Q
  -> reduced states, observables, and instruments.
```

The order is philosophically important. If `P` is inserted by hand, the upper
description can be engineered to reproduce almost any lower theory. If `P` is
the spectral projector of a selected repair source, the lower theory becomes a
consequence of the same object that defines admissibility.

The excluded space `Q\mathcal H` is not simply "unreal." It can represent
unstable directions, heavy modes, incompatible continuations, gauge artifacts,
or degrees of freedom integrated out of the accepted description. Which reading
is correct depends on the source and observables. What matters mathematically is
that discarded excursions can leave a memory in the effective lower algebra.

## 7. The exact mathematics of constrained reduction

For an orthogonal projector `P`, let `Q=I-P` and define the compressed operator

```math
\Phi_P(T)=PTP\big|_{P\mathcal H}.
```

Compression is generally not multiplication preserving. The exact defect is

```math
\Phi_P(S)\Phi_P(T)-\Phi_P(ST)
=-PSQTP\big|_{P\mathcal H}.
```

The right-hand side has a direct interpretation. The first operation leaves
the retained sector, the intermediate state travels through `Q`, and the second
operation returns it. A calculation that deletes `Q` before composing the
operations loses this route.

For self-adjoint upper operators define leakage maps

```math
L_A=Q\widetilde A P,
\qquad
L_B=Q\widetilde B P.
```

If the upper operators commute, their lower compressions satisfy the exact
identity

```math
[\Phi_P(\widetilde A),\Phi_P(\widetilde B)]
=L_B^*L_A-L_A^*L_B.
```

Thus commuting upper questions can have incompatible lower shadows. The lower
commutator records the oriented mismatch between two ways of trying to leave
the admissible sector.

This is established compression mathematics, related to Toeplitz and Hankel
operators. MTT's contribution is not the invention of the identity. Its
possible contribution would be to derive a physical `P`, physical upper
operators, and the action scale from one source, then show that the resulting
lower algebra is the one observed in quantum physics.

## 8. A finite example of emergent incompatibility

The mechanism can be seen without interpretation. Let

```math
P=I-\frac13\mathbf 1\mathbf 1^{\mathsf T},
\qquad
Q=\frac13\mathbf 1\mathbf 1^{\mathsf T}
```

on `C^3`. The retained space is the two-dimensional plane whose coordinates
sum to zero. Choose

```math
\widetilde X=\operatorname{diag}(1,0,0),
\qquad
\widetilde Y=\operatorname{diag}(0,1,0).
```

The upper matrices commute. Their compressions do not:

```math
[P\widetilde X P,P\widetilde Y P]
=\frac19
\begin{pmatrix}
0&-1&1\\
1&0&-1\\
-1&1&0
\end{pmatrix}.
```

The commutator is exactly the leakage form
`L_Y^*L_X-L_X^*L_Y`. The example proves that constrained reduction can create
lower incompatibility. It does not prove that these matrices are position and
momentum, that the projector is physical, or that the coefficient is `hbar`.
In finite dimension, the trace of a commutator vanishes, so an exact nonzero
canonical relation `[A,B]=icI` cannot hold. A physical uncertainty theory still
requires selected infinite-dimensional observables or a controlled limit,
domains, and normalization.

## 9. Fixed points and the identity of objects

In a substance-first picture, an object persists because the same underlying
thing remains present. In a repair-first picture, a physical object persists
because its organizing pattern is invariant under the admissible dynamics.

```text
disturbance
  -> response through retained and excluded modes
  -> restoration or transport of an invariant pattern
  -> persistent identity.
```

The relevant fixed point need not be static. A traveling wave, periodic orbit,
soliton, transported section, or gauge-equivalence class can be fixed in a
co-moving, quotient, or stroboscopic description. **Identity by invariance
under repair** means that the pattern survives in the appropriate physical
category, not that every coordinate remains numerically constant.

This offers a natural account of particle type. Two excitations are instances
of the same type when they lie in the same selected invariant class and carry
the same physical transformation data. Their individuality can still depend on
localized records and histories.

The Fixed Points series supplies rigorous conditional versions of stability,
spectral projection, perturbation, and convergence. It does not yet prove that
every Standard Model particle is a selected fixed point of one MTT repair law.

## 10. Repair symmetry and gauge descent

Suppose a group `G` acts unitarily on the upper carrier and the repair law is
equivariant:

```math
\mathcal F(U_g u)=U_g\mathcal F(u).
```

Let `G_*` be the stabilizer of a fixed background `u_*`. Exact differentiation
then gives

```math
J_*U_g=U_gJ_*
\qquad(g\in G_*).
```

The isolated Riesz projector commutes with the same stabilizer. Compression and
leakage therefore transform covariantly. If `\mathcal A_{\rm phys}` is the
accepted reduced observable algebra, define

```math
K_{\rm phys}
=\{g\in G_*:\operatorname{Ad}(U_{g,P})(A)=A
\text{ for every }A\in\mathcal A_{\rm phys}\}.
```

The faithful reduced action is

```math
G_{\rm faithful}=G_*/K_{\rm phys}.
```

This chain distinguishes three notions often compressed into the single word
"gauge":

1. a symmetry of the upper repair source;
2. a redundancy acting trivially on accepted observables;
3. a faithful physical symmetry remaining after quotienting the redundancy.

The distinction blocks a common philosophical mistake. Not every source
symmetry is mere description, and not every upper coordinate is a physical
charge. The action kernel has to be calculated.

## 11. The Standard Model gauge result and its proper interpretation

Current MTT authority `A47` establishes, at its structural tier, the faithful
low-energy group

```math
\frac{SU(3)\times SU(2)\times U(1)}{\mathbb Z_6}
```

from selected native bundle tensors. Authority `A50` separately establishes
the anomaly-free shared hypercharge circle and its exact charge rows. These are
substantial structural results. They are not re-proved here.

The repair-to-gauge theorem supplies an upstream interpretation only
conditionally: if the selected physical repair source has the native tensor
automorphisms, if its background and projector are preserved, and if the kernel
on the physical observable algebra is the same diagonal `Z6`, then the
established group is the faithful shadow of closure geometry.

The missing antecedent matters. The selected continuum action, HYM endpoint,
connection, and full intertwining data remain open. It would therefore be too
strong to say that MTT has already derived all gauge dynamics from repair. The
accurate claim is that the structural group is established and the abstract
descent mechanism is exact, while their same-source physical identification is
unfinished.

## 12. Gauge as relational comparison

The philosophical content of gauge structure is not exhausted by the word
"redundancy." Local representatives are needed to compare internal states from
place to place. A connection records how those representatives are related;
holonomy records what remains after transport around a loop; gauge-invariant
quantities express the relational content that survives a change of local
handle.

On this interpretation:

> Gauge freedom is freedom in choosing local relational handles without
> changing the closed physical pattern. Gauge fields encode the comparison law
> for those handles across the causal base.

This view explains why apparently surplus variables can be indispensable to a
local formulation. It also explains why gauge constraints can make the state of
a whole region fail to factor neatly into independent states of its subregions.
The failure is not automatically a nonlocal force; it can arise because the
shared boundary and comparison data cannot be assigned independently.

## 13. A hierarchy of locality claims

"Locality" names several different conditions. Causal-base constraint realism
is credible only if they are kept apart.

| Locality notion | Question |
|---|---|
| Causal locality | Can an intervention at one base event influence a spacelike event? |
| Algebraic microcausality | Do observables assigned to spacelike regions commute? |
| Fiberwise locality | Are upper transformations defined pointwise or locally over the base? |
| Projector compatibility | Does reduction preserve the local subalgebra? |
| State separability | Is the joint state determined by independent states of the parts? |
| Bell local causality | Do joint probabilities factor given a complete past specification and the other Bell assumptions? |

These conditions do not imply one another. In particular,

```text
spacelike observable algebras commute
does not imply
the joint state factorizes.
```

The exact locality theorem in this repo applies to the coherent-preserving
upper local algebra

```math
\mathcal A_U^P(O)
=\{A\in\mathcal A_U(O):[A,P]=0\}.
```

If the upper net is spacelike local, compression of this compatible algebra is
also spacelike local. The result transports locality. It does not make an
arbitrary global projector local. Operators with nonzero `QAP` leakage require
an additional localization theorem before they can be admitted as physical
local observables.

This guardrail gives precise content to the user's central intuition:

```text
local causal interactions on the four-dimensional base
+ locally compatible upper bundle structure
+ global admissibility of the joint section
does not equal
a hidden superluminal communication channel.
```

## 14. Entanglement as nonseparability of one admissible whole

Entanglement is most cleanly described here as **nonseparability without
superluminal interaction**. Two spacelike laboratories can possess commuting
local observable algebras while the joint state is not a product or classical
mixture of independently specified local states.

In the present vocabulary:

```text
local algebras          -> where interventions occur
joint admissibility     -> which global states are allowed
nonfactorizing state    -> entanglement
local instruments       -> actual experimental couplings
joint records           -> observed correlations.
```

The state of the pair belongs to the preparation as a whole. A measurement on
one side does not need to send a controllable message through the fiber to
create the distant correlation. The local interactions reveal correlations of
the already nonseparable state.

The fiber should therefore not be pictured as a hidden telephone cable. It is a
candidate representation of the common constraint structure under which the
joint state exists. This is close to relational and structural accounts in
which the properties of the whole are not reducible to intrinsic properties of
separately specified parts.

## 15. Bell's theorem is a boundary, not an inconvenience

Moving a hidden variable into an upper fiber does not evade Bell's theorem. If
the upper model retains Bell factorization, measurement independence, and the
relevant common-cause assumptions, it is still constrained by Bell inequalities.
Calling it "upper-local" changes no mathematics.

The viable reading is different:

1. dynamics and detector couplings remain microcausal on the base;
2. the prepared joint quantum state is nonfactorizing;
3. lower Bell factorization therefore does not hold;
4. the theory must derive the state, setting-dependent instruments, and joint
   probabilities rather than insert them after the fact;
5. operational no-signalling must remain exact.

This is not a local hidden-variable explanation. It is a proposal to explain
why the nonfactorizing quantum state is an admissible global structure while
all controllable interactions remain local.

To become more than reinterpretation, MTT must select a Bell experiment from
one source and reproduce its correlations, setting independence, instrument
algebras, and no-signalling constraints. The philosophical picture cannot be
used as a substitute for that calculation.

## 16. Wave and particle as two faithful readouts

Wave-particle duality need not describe a substance alternating between two
incompatible materials. One retained state or operator can have two
complementary representations:

```text
spectral, phase-coherent, or modal readout -> interference and extension
localized instrument and record readout    -> discrete event registration.
```

The wave description displays how modes propagate and interfere. The particle
description displays where an interaction leaves a stable, countable record.
Neither readout alone exhausts the common source.

If the repair tangent operator `J_*` is selected, a candidate retained
propagator has the schematic form

```math
B_{\rm adm}(s)
=P\chi(J_*)e^{-sJ_*}\chi(J_*)P.
```

Its spectral decomposition is wave-like, while its integral kernel or coupling
to a localized instrument can be particle-like. The kernel can be interpreted
as a repair propagator: it tells how a deviation in one part of the retained
sector contributes to response elsewhere.

This formula is explanatory, not yet the selected physical Hamiltonian. A heat
semigroup in an auxiliary repair parameter is not automatically unitary time
evolution. The physical state, causal propagator, detector effects, and
instrument must all arise from the same accepted source.

## 17. Uncertainty as constrained incompatibility

The compression identity suggests a structural reading of uncertainty. Two
upper questions can be jointly compatible, yet each can attempt to leave the
retained sector in a different direction. Once both are forced back through
the same physical constraint, their lower order matters.

For a normalized retained state, the ordinary Robertson inequality can be
rewritten as

```math
\Delta A\,\Delta B
\geq\frac12
\left|
\langle L_B^*L_A-L_A^*L_B\rangle
\right|
```

when the upper pair commutes. This makes the incompatibility geometrically
legible in terms of leakage.

It does not show that all quantum uncertainty is merely an artifact of lost
information. The lower state can be genuinely nonclassical, and the physical
observables may have no simultaneous values. Nor does the equation derive a
universal `hbar`. The action scale, operator domains, canonical pair, and
physical projector remain necessary.

The defensible philosophical statement is therefore limited:

> Some quantum incompatibility may be the exact shadow of jointly imposing an
> upper admissibility constraint, rather than ignorance about two hidden lower
> values.

## 18. Measurement is an ordinary physical process

Measurement should not be assigned a special metaphysical power. It is a local
physical interaction that correlates a system with an apparatus and produces a
stable, readable record.

```text
preparation
  -> system-apparatus coupling
  -> amplification or stable-sector formation
  -> accessible record
  -> conditional description relative to that record.
```

No consciousness is required. The word "measurement" does not itself explain
why a particular record occurs, and the universe does not wait for an observer
to become complete.

On the constraint-realist reading, an apparatus changes the local interaction
and admissibility conditions. The joint state evolves under those conditions,
and one of its stable record sectors becomes the observed output. The
mathematical problem is to derive the instrument and output law from the same
source as the system, not to elevate measurement into a primitive act.

## 19. Probability, records, and the remaining outcome question

The current ledger closes the canonical q79 Born source theorem on its declared
binary one-anchor recorder domain. There the stopped output measure and second
moment descent are emitted from the selected normal state without an added
stochastic primitive, fitted probability, or observed probability input. That
is a real operational achievement.

It does not establish a universal theory of every apparatus. The same ledger
keeps open the construction of a same-source apparatus family covering the
physical context class with explicit approximation bounds. It also keeps open
any stronger objective process selecting one ontic history.

This distinction leaves several ontologies compatible with the operational
result. One may read the output law instrumentally, as objective propensity, as
branch-relative weight, or as the statistics of a deeper actualization process.
The current mathematics does not select one merely from Hilbert space, unitary
evolution, and record structure. Causal-base constraint realism should not
claim otherwise.

## 20. Particles and fields

A field is a rule assigning local values, admissible variations, and relational
comparisons over the causal base. It need not be imagined as a material fluid,
although some fields can carry energy and momentum in precisely the ordinary
physical sense.

A particle can be interpreted as a stable, transportable, localized mode of
that field-and-repair structure. Its properties would be invariants of the
selected construction:

| Property | Candidate structural origin |
|---|---|
| Identity | Membership in one stable fixed or transported sector. |
| Charge | Faithful transformation under the reduced gauge group. |
| Spin | Representation under spacetime and internal symmetry. |
| Mass | A selected response, pole, Hessian, or spectral scale after normalization. |
| Lifetime | Stability or decay rate of the retained mode under physical evolution. |
| Localization | Coupling to local algebras and record-forming instruments. |

This is compatible with ordinary QFT's view of particles as excitations rather
than tiny classical objects. MTT's stronger ambition is to derive the relevant
sectors and values from one upper source. The structural representation and
several finite response maps are advanced; full same-source continuum particle
dynamics and no-knob values remain open.

## 21. Dimensions should be classified by role

The word "dimension" hides several physically different ideas.

1. **Causal spacetime dimension:** a direction of localization, causal
   propagation, inertial structure, and initial-value data.
2. **Physical internal dimension:** a degree of freedom that can propagate,
   carry energy, or produce observable towers without being a macroscopic
   spacetime direction.
3. **Constraint dimension:** a coordinate needed to express admissibility,
   phase, orientation, closure, or comparison without its own causal cone.
4. **Configuration-space dimension:** a coordinate on the space of whole
   states rather than on spacetime.
5. **Algebraic dimension:** matrix size, representation rank, component count,
   or mode multiplicity.

One should not infer ontology from a count alone. A `27 x 27` matrix has 27
components in a representation space; it does not imply 27 spacetime
directions. A fiber coordinate can be physical without being spatial. A compact
internal manifold can encode both genuinely propagating modes and constrained
or gauge directions.

The tests are operational and dynamical:

- Does the coordinate have an independent causal cone?
- Does it require independent initial data?
- Can excitations propagate in it?
- Does it carry energy or momentum?
- Does it create an observable tower?
- Is it removed by a gauge quotient?
- Does it only label equivalent or admissible continuations?

Until these questions are answered, "extra dimension" is a mathematical label,
not a settled physical interpretation.

## 22. The `1 + 3 x 3 = 4 + 6` reconciliation

MTT's world-in-world carrier can be read consistently without multiplying
manifold dimensions. A linear comparison between two three-dimensional tangent
structures has nine components:

```math
\operatorname{Hom}(\mathbb R^3,\mathbb R^3)
\cong\operatorname{End}(\mathbb R^3).
```

After a metric and orientation are chosen,

```math
\operatorname{End}(\mathbb R^3)
=\mathfrak{so}(3)\oplus\operatorname{Sym}(3),
```

with dimensions `3+6`. The symmetric part splits further into

```text
one scalar trace direction
+ two traceless diagonal shape directions
+ three symmetric off-diagonal shear directions.
```

Adding one causal order/time direction gives the bookkeeping identity

```text
1 + 3 x 3
= (1 time/order + 3 orientation)
  + (1 scalar + 2 shape + 3 shear)
= 4 + 6
= 10.
```

This is a decomposition of a comparison field. It is not ordinary dimension
multiplication, and equality of counts does not prove physical identity. The
remaining theorem obligation is to show that the three orientation directions
are precisely quotiented or absorbed in the selected physical construction and
that the six strain directions intertwine with the actual q79 vertical
geometry.

The selected `1<2<3` rank flag is recursive activation of one, two, and three
directions. It is not literal nesting of three manifolds. In a chosen Iwasawa
frame the three upper-unitriangular directions form the nil/shear sector, but
the old literal `S1 x Lens x Nil` physical topology remains retired.

## 23. The shared circle

The shared circle is best interpreted as common `U(1)` phase or holonomy data.
It is reused across the relevant lanes and counted once. Its physical meaning
can include charge comparison, phase transport, determinant-line data, or a
shared connection.

It should not be identified directly with Lorentzian time. A compact phase
coordinate and a noncompact causal ordering variable have different topology,
roles, and dynamics. A lift `R -> S1` can encode accumulated phase along time,
but that does not make time itself a circle.

The philosophical importance of one shared circle is relational. If the same
line bundle with the same connection pulls back into fixed-point, proto-spinor,
gauge, and q79 constructions, then apparently different lower encodings may be
shadows of one upper comparison standard. Proving isomorphic circles in several
papers is weaker. The decisive statement must preserve the connection,
holonomy, Hessian, and source provenance under the relevant pullbacks and
intertwiners.

## 24. Genuine internal geometry and the q79 branch

The q79 Fu-Yau/Hull-Strominger route is not merely a metaphorical constraint
space. It is a serious candidate internal geometry in established heterotic
compactification mathematics. Its modes may be physically internal, constrained,
gauge, or some mixture.

This prevents an overcorrection. Causal-base constraint realism does not say
that every extra dimension in string-inspired mathematics is unreal. It says
that the physical role of each direction must be proved. If vertical modes
propagate, carry energy, affect spectra, or survive the physical quotient, they
are genuine internal degrees of freedom even though they are not macroscopic
spacetime directions.

The current q79 branch supplies strong discrete, bundle, and finite structural
data. It does not yet supply the selected visible-hidden HYM endpoint, common
chamber, complete connection and Green operator, anomaly/Bianchi realization,
or same-source continuum-to-finite naturality. The endpoint is therefore a
candidate physical realization of the philosophy, not a premise from which the
philosophy may simply assume completion.

Alternative physical endpoints are logically possible. Any alternative must
still provide the same typed exits: one source, physical locality, stable
projector, faithful gauge action, quantum state and instruments, normalization,
and empirical comparison. Bypassing q79 does not bypass those obligations.

## 25. Gravity as response of the causal base

In this interpretation, gravity belongs primarily to the geometry of the
causal base. It should not be treated as one more internal gauge label. The MTT
proposal is that imperfect internal closure, or the effective stress of
quantized constrained matter, may source changes in the base geometry.

Philosophically:

> Gravity would be the geometry of how local causal continuation responds to
> the energetic cost and stress of maintaining a coherent physical pattern.

This is suggestive because it keeps quantized matter and constraint structure
upstairs while allowing the causal geometry to respond downstairs. It is not
yet a quantum-gravity theory. A consistent construction needs at least:

- a signed Lorentzian action rather than a merely positive repair cost;
- a conserved stress tensor or relative-Cauchy-evolution equivalent;
- gauge and diffeomorphism control;
- Newton and Planck normalization;
- a controlled low-energy limit reproducing the Einstein equations or a
  testably different alternative;
- quantum consistency if the base geometry is itself quantized;
- evidence that semiclassical backreaction is stable if it is not.

Perfect closure might correspond to vanishing effective closure stress and a
flat or stationary base in a special limit. That is a useful conjecture, not an
established equation. Positive residual energy alone does not derive general
relativity.

## 26. Three notions of time

Three parameters must remain distinct.

1. **Lorentzian time or causal order** on the base.
2. **Repair parameter** `s`, used to describe convergence toward or motion
   around an admissible sector.
3. **Shared circle phase**, a compact holonomy variable.

Only the first is physical time by present declaration. A theorem may later
relate physical evolution to a repair flow, but the relation cannot be assumed.
A dissipative semigroup and a unitary Lorentzian evolution have different
mathematical properties.

An arrow of time could arise from asymmetric boundary data, stability of
records, retarded response, or branch selection. Two mathematical orientations
do not imply two equally physical universes, nor does selection of one branch
prove that the other is well behaved. The branch question is an initial-state
and dynamics problem, not a consequence of drawing both arrows.

## 27. Laws as dynamics and constraints

Traditional formulations often contrast dynamical laws, which tell a state how
to change, with constraints, which tell a state which configurations are
allowed. Causal-base constraint realism combines them.

The repair law is dynamical at the upper level. Its zeros define admissible
structures. Its tangent operator governs local response. Its selected fixed
sector constrains lower dynamics. The same object can therefore function as

```text
a process law upstairs
+ an admissibility condition at a fixed point
+ an effective operator law after projection.
```

This is not logically circular if the levels are ordered. The nonlinear source
is specified first, the fixed point is solved, and the lower rules are derived.
It becomes circular only if the desired lower rules are used to choose the
source or projector without independent selection.

## 28. Four philosophical readings

The mathematics does not force a unique ontology. At least four readings remain
available.

### 28.1 Instrumental fiber

Only four-dimensional events, ordinary fields, and their observable relations
are real. The upper bundle is efficient bookkeeping. This reading is viable if
different upper models produce exactly the same physical structure and no
experiment or explanatory criterion distinguishes them.

### 28.2 Moderate structural realism

Events and systems are real, and invariant relational structures encoded by
connections, holonomies, fixed sectors, and gauge quotients are also real.
Coordinate representatives and pure gauge labels are not independently real.

### 28.3 Process-first constraint realism

Closure repair is fundamental. Objects, fields, and perhaps some spacetime
structure are stable modes or invariants of that process. The ontology begins
with continuation and response rather than with a list of self-contained
substances.

### 28.4 Literal higher-dimensional realism

The internal geometry describes additional physical fields or compact
directions. Constraint language is an effective lower description. This may be
correct for some q79 modes even if other fiber directions are representational.

The preferred interpretation is a combination of 28.2 and 28.3, with a mixed
verdict permitted for 28.4. The current mathematics cannot yet exclude the
instrumental reading.

## 29. Relation to nearby philosophical positions

### Structural realism

The proposal agrees that invariant structure can be more fundamental than a
particular representation. It differs from the strongest ontic structural
realism by retaining events, processes, and records rather than replacing all
objects with relations.

### Process philosophy

The repair-first account treats persistence as stabilized activity. It shares
the process-philosophical intuition that becoming and relation are basic, but it
requires explicit operators, fixed points, and observable maps rather than a
purely verbal metaphysics.

### Modal interpretations

The fiber organizes possible continuations and admissible structures, so the
view is modal in a technical sense. It is not Lewisian possible-world realism.
The alternatives in a fiber are not automatically concrete universes.

### Relational quantum mechanics

Both approaches resist assigning all properties independently of interaction
and context. Causal-base constraint realism adds a proposed upper source and
projection mechanism. It should not claim to subsume relational quantum
mechanics until it derives the same operational predictions and clarifies the
status of records between observers.

### Algebraic quantum field theory

AQFT already cleanly separates local observable algebras from global states.
That separation is central here: microcausality can coexist with entanglement.
MTT's additional task is to derive the net, state, and projector from its repair
geometry.

### Gauge and fiber-bundle interpretations

Connections, holonomies, quotients, and edge data are standard tools. The new
philosophical claim is not that bundle geometry exists, but that one selected
repair source may explain why the physical bundle, projector, gauge quotient,
and quantum algebra occur together.

### String and compactification programs

String theory makes internal geometry dynamically and spectrally meaningful.
Constraint realism offers a role-sensitive language for asking which internal
directions are physical, constrained, or representational after projection. It
does not eliminate the need for worldsheet consistency, anomaly cancellation,
moduli stabilization, or the low-energy limit.

## 30. What is genuinely new, and what is not?

Most ingredients are established mathematics:

- fiber bundles and connections;
- constrained Hamiltonian systems and gauge reduction;
- fixed points, gradient flows, and semigroups;
- Riesz projectors and spectral perturbation;
- Toeplitz compression and Hankel leakage;
- AQFT locality and nonfactorizing states;
- effective operators, Feshbach reduction, and transferred products.

Credibility increases when these precedents are acknowledged. Renaming them is
not a new theory.

The potentially original content lies in a successful **same-source
composition**:

```text
one selected closure/repair object
  -> physical background and projector
  -> faithful Standard Model structure
  -> quantum local net and Born recorder
  -> particles, values, and interactions
  -> gravitational response
  -> held-out predictions.
```

If the arrows are independently derived and commute, the result would be more
than a reinterpretation of familiar mathematics. If the arrows require
separate fitted sources or observed targets, the proposal remains a useful
organizational language rather than a fundamental closure.

## 31. Two exact toy witnesses and their limits

The repo contains two especially useful finite witnesses.

### 31.1 Compression witness

The rank-two sum-zero projector in Section 8 turns two commuting diagonal upper
operators into noncommuting lower compressions. It verifies the leakage identity
with exact rational arithmetic. It demonstrates a mechanism for lower
incompatibility.

It does not select quantum observables, canonical commutation, or a physical
action scale.

### 31.2 Repair and gauge witness

On `R^3`, take

```math
H_0=2P+5Q,
\qquad
\mathcal F(u)=H_0u+(u^{\mathsf T}u)u.
```

The unique fixed point is zero, the tangent operator is `H_0`, the spectral gap
is three, and the low projector is `P`. Signed coordinate permutations preserve
the source and projector. On the retained operator algebra, the central pair
`{+I,-I}` acts trivially, leaving a faithful quotient of order six.

This demonstrates the chain

```text
repair symmetry -> fixed point -> tangent projector -> faithful quotient
```

without fit or measured input. It is not the Standard Model gauge group and is
not a physical universe model.

Together the witnesses show that the philosophical chain is mathematically
coherent. They do not establish that nature follows it.

## 32. Current research-status ledger

The following table records the status relevant to this interpretation. It is
not a summary of every MTT result.

| Structure | Current status | Philosophical consequence |
|---|---|---|
| Compression multiplicative defect and leakage commutator | Exact general theorem plus exact finite witness | Constrained reduction can alter products and create lower incompatibility. |
| Equivariant repair, fixed-point linearization, Riesz projector, and faithful quotient | Exact general theorem plus exact finite witness | The proposed repair-to-gauge chain is mathematically coherent. |
| Fixed-point analytic spine | Rigorous under stated analytic hypotheses | Stable-sector language has a real analytic basis. |
| Faithful low-energy `(SU3 x SU2 x U1)/Z6` | Established structural authority `A47` | The correct global gauge group is available at its declared tier. |
| Shared anomaly-free hypercharge circle | Established authority `A50` | The common circle has concrete gauge content, not merely symbolism. |
| Canonical q79 operational Born source | Closed on its declared recorder domain | Probability is not wholly inserted as an external stochastic primitive there. |
| Cohesive nonlinear repair prototype | Verified on a pushed branch, not selected physical authority | Repair-first dynamics has a serious prototype but not the final source. |
| q79 discrete and finite source structures | Strong exact and conditional results | A physical internal candidate exists, but finite structure is not continuum completion. |
| Selected visible-hidden HYM endpoint | Open: `B.HS.01` | The preferred physical compactification endpoint is not yet selected. |
| Continuum geometry-to-operator naturality | Open: `B.GEO.01`, `B.OP.01` | The finite/projected structures are not yet fully tied to one physical continuum operator. |
| Selected upper action and normalization | Open: `B.ACTION.01` | Repair, quantum evolution, and gravity do not yet come from one physical action. |
| Universal apparatus and objective actualization | Open: `B.QM.03` | Operational records do not settle universal measurement or one-history ontology. |
| Interacting BV/QME continuum QFT | Open: `B.QFT.02` | Free/finite quantum structures are not full interacting QFT closure. |
| No-knob precision Standard Model values | Open: `B.SM.02` | Structural parity is not yet true held-out precision equivalence. |

Nothing in this table is worsened by calling the philosophy interpretive. The
status separation is what makes a future promotion meaningful.

## 33. What would count as scientific success?

The interpretation becomes a physical theory only if one selected source
discharges a chain of independent tests.

1. **Source selection:** state the nonlinear source or action without using the
   desired lower observables as construction inputs.
2. **Existence:** prove a physically admissible fixed background exists.
3. **Stability:** establish the gap, domains, and well-posed repair or causal
   evolution.
4. **Projection:** derive `P`, `Q`, and any decoder or quotient.
5. **Locality:** construct a local net and prove microcausality after reduction.
6. **Gauge:** derive the stabilizer, action kernel, faithful quotient,
   connection, and holonomies from the same source.
7. **Quantum structure:** derive states, observables, instruments, and the action
   scale with positivity and normalization.
8. **Matter:** obtain the particle sectors, interactions, and value rows without
   replaying measured targets.
9. **Gravity:** derive controlled base-geometry response and its low-energy
   limit.
10. **Prediction:** publish held-out consequences and uncertainty estimates that
    can fail.

Success is not the existence of a parameter choice that fits known data. It is
the independent selection of the choice and the survival of held-out tests.

## 34. What would falsify or weaken the interpretation?

Several outcomes would count against the strong form.

- No selected repair source can produce the required stable projector.
- The physical projector makes the reduced local algebra violate
  microcausality or operational no-signalling.
- The faithful gauge quotient cannot be obtained from the same source that
  produces matter and the action.
- The q79 or any replacement endpoint fails the required analytic and anomaly
  conditions.
- Physical constants require as many unconstrained inputs as the theory aims to
  explain, with no independent selection rule.
- The resulting correlations fail quantum experiments or Bell tests.
- Gravitational response lacks conservation, has unstable modes, or fails the
  measured low-energy limit.
- Several inequivalent upper constructions remain empirically identical and no
  explanatory criterion selects among them.

The last outcome would not make the mathematics useless. It would favor an
instrumental fiber interpretation over constraint realism.

## 35. Main objections and replies

### Objection 1: This only renames configuration space

**Reply:** It may do so unless one source selects the fiber, projector, and
observables and produces new constraints or predictions. The paper presents a
research interpretation, not a novelty claim based on vocabulary.

### Objection 2: A global constraint is disguised nonlocal causation

**Reply:** Global admissibility and controllable causal influence are distinct.
A boundary-value condition can restrict whole solutions without transmitting a
signal. The physical model must nevertheless prove local algebras,
no-signalling, and projector compatibility; the distinction cannot be asserted
by analogy alone.

### Objection 3: Bell's theorem forbids the proposal

**Reply:** Bell forbids the relevant locally causal hidden-variable
factorization, not microcausal quantum theories with nonfactorizing states. The
proposal cannot retain Bell factorization under a new name. It must reproduce
quantum correlations while identifying state nonseparability, rather than a
superluminal interaction, as the failed lower assumption.

### Objection 4: The projector can always be chosen to manufacture quantum
rules

**Reply:** Correct. This is why source selection is the central gate. The
projector must be the spectral or geometric consequence of an independently
specified source, with held-out validation.

### Objection 5: Repair merely moves the unexplained operator one level up

**Reply:** At the present frontier, partly. The repair-first proposal improves
the explanatory order only if a simpler nonlinear source generates several
operators and sectors at once. If each desired operator requires a tailored
repair law, no explanatory gain has been made.

### Objection 6: Fixed points imply a frozen universe

**Reply:** Fixed points can be defined after quotienting transport, gauge, or
periodic evolution. The invariant object can be a moving pattern. The physical
time evolution must still be stated separately from auxiliary repair flow.

### Objection 7: Extra dimensions are being declared unreal by fiat

**Reply:** The paper gives role tests, not a universal verdict. Propagating and
energetic internal modes are physical. Gauge, constraint, and algebraic
directions need not be spacetime dimensions.

### Objection 8: Gauge redundancy cannot be physically real

**Reply:** Gauge representatives need not be real as distinct states, while the
connection, holonomy, quotient, and invariant relational structure can be.
Constraint realism commits to the invariants, not every representative.

### Objection 9: Measurement still has no single outcome

**Reply:** The current operational theorem supplies an output law on a declared
domain, not a universal ontic actualization law. The philosophy deliberately
leaves that stronger question open rather than hiding it inside the word
"repair."

### Objection 10: The program explains everything only after the fact

**Reply:** That risk is real. Source hashes, dependency ledgers, no-fit
declarations, independent verifiers, and held-out tests are required precisely
to distinguish derivation from replay.

## 36. A philosopher's description of the main physical ideas

### Entanglement

The whole has an admissible state that cannot be decomposed into independent
states of the parts. Local interactions reveal its joint structure without a
message passing between spacelike detectors.

### Wave-particle duality

One retained process has an extended modal description and a localized record
description. Wave and particle are complementary shadows, not competing
substances.

### Gauge

Physical comparison requires local handles. Changing the handles can leave the
closed pattern unchanged, while the connection and holonomy record invariant
relational content.

### Uncertainty

Two lower questions can be incompatible because they leave and re-enter the
same constrained sector in different orders. This is not mere ignorance of two
simultaneously sharp hidden values.

### Measurement

A measurement is an ordinary local coupling that creates a durable record. It
has no privileged metaphysical status merely because a physicist reads it.

### Extra dimensions

Some extra coordinates can catalogue ways of being coherent rather than ways
of moving through space. Others can be genuine internal physical modes. Their
role must be derived.

### Particles

Particles are stable, transportable, localized invariants of fields and repair
dynamics, characterized by their physical symmetry and response data.

### Gravity

Gravity may be the causal base's response to the stress and energetic cost of
maintaining coherent constrained matter. This remains a programmatic
hypothesis.

## 37. Compact formal dictionary

| Symbol or phrase | Role |
|---|---|
| `M` | Four-dimensional causal base. |
| `E -> M` | Upper bundle or constraint carrier. |
| `u` | Upper section or configuration. |
| `F(u)` | Closure or repair residual. |
| `u_*` | Admissible fixed background with `F(u_*)=0`. |
| `J_*=DF(u_*)` | Tangent repair operator. |
| `P` | Selected retained spectral/coherent projector. |
| `Q=I-P` | Excluded, unstable, heavy, or incompatible sector. |
| `Phi_P(A)=PAP` | Lower compressed observable. |
| `L_A=QAP` | Excursion of an upper operation out of the retained sector. |
| `G_*` | Stabilizer of the selected background. |
| `K_phys` | Transformations acting trivially on accepted observables. |
| `G_*/K_phys` | Faithful physical symmetry. |
| local net | Assignment of observables to causal-base regions. |
| instrument | Physical system-apparatus coupling and record map. |
| shared circle | Common phase/holonomy line, not physical time. |
| q79 | Selected discrete branch and candidate internal-geometric program, not by itself the full physical endpoint. |

## 38. The research program in one diagram

```text
CAUSAL BASE M
  local events, causal cones, detector regions
        ^
        | physical fields and records
        |
UPPER CONSTRAINT CARRIER E -> M
  phase, orientation, internal, comparison, closure data
        |
        v
SELECTED SOURCE / ACTION
        |
        v
NONLINEAR REPAIR F
        |
        v
FIXED BACKGROUND u_*
        |
        v
TANGENT OPERATOR J_* AND GAP
        |
        +-------------------------------+
        |                               |
        v                               v
RETAINED P                         EXCLUDED Q
        |                         response, memory,
        |                         heavy/unstable modes
        v
LOCAL REDUCED ALGEBRA + FAITHFUL GAUGE QUOTIENT
        |
        v
STATE + INSTRUMENT + RECORD LAW
        |
        v
PARTICLES, INTERACTIONS, VALUES, AND BASE-GEOMETRY RESPONSE
```

Every arrow is a theorem obligation. The diagram is not a completed derivation.

## 39. Conclusion

Causal-base constraint realism offers a coherent way to think about several
features of modern physics without turning them into separate mysteries.
Locality belongs to causal interaction on the four-dimensional base;
entanglement belongs to the nonfactorizing state of an admissible whole; gauge
belongs to relational comparison and faithful quotient; wave and particle are
different readouts of one retained process; uncertainty can reflect the algebra
of constrained reduction; and extra coordinates can have physical,
configurational, or purely algebraic roles.

The unifying idea is that closure is active. Reality is not only a collection
of things satisfying static conditions. On the preferred interpretation it is
a continuing process by which local structures remain jointly admissible, with
persistent objects appearing as invariants of that process.

The strongest honest conclusion is conditional:

> If one selected MTT source derives the repair law, physical fixed background,
> local projector, faithful gauge quotient, quantum state and instruments,
> normalized values, and gravitational response, then causal-base constraint
> realism provides a unified ontology for the resulting theory. Until that
> same-source chain is complete, it remains a disciplined philosophical
> interpretation supported by exact mathematical bridges, not a finished
> fundamental theory.

That boundary is not a weakness to conceal. It is the line that makes the next
proof scientifically meaningful.

## 40. Internal sources and theorem ownership

This synthesis relies on the following owner documents in this repository and
does not duplicate their theorem ownership:

1. [Causal-Base Constraint-Fiber Compression-Leakage Theorem](CausalBaseConstraintFiberCompressionLeakageTheorem_v1.md).
2. [Repair, Fixed-Point, and Gauge-Descent Theorem](RepairFixedPointGaugeDescentTheorem_v1.md).
3. [MTT Fixed-Point, Gauge, and Projection Grounding Map](MTT_FIXEDPOINT_GAUGE_GROUNDING_MAP_v1.md).
4. [Constraint Reduction Reference System](CONSTRAINT_REDUCTION_REFERENCE_SYSTEM_v0.md).
5. [Current Kernel-Locked Status](CURRENT_STATUS.md).
6. [Research Roadmap](RESEARCH_ROADMAP.md).

The Fixed Points, Foundations, Projection-Admissibility, Bell, duality,
proto-spinor, Standard Model, q79, quantum mechanics, QFT, and quantum-gravity
papers remain the owners of their respective physical claims.

## 41. Selected external context

1. M. Esfeld, [Quantum entanglement and a metaphysics of relations](https://philsci-archive.pitt.edu/1735/1/Entanglement.pdf).
2. V. Lam, [The entanglement structure of quantum field theory](https://philsci-archive.pitt.edu/10089/).
3. H. Halvorson and R. Clifton, [Generic Bell correlation between arbitrary local algebras in quantum field theory](https://arxiv.org/abs/math-ph/9909013).
4. S. De Haro and J. Butterfield, [The Philosophy and Physics of Duality](https://philsci-archive.pitt.edu/26099/).
5. C. Rovelli, [Why Gauge?](https://philsci-archive.pitt.edu/10096/).
6. J. Nguyen, N. Teh, and L. Wells, [Why surplus structure is not superfluous](https://philsci-archive.pitt.edu/14166/).
7. N. P. Landsman, [Rieffel induction as generalized quantum Marsden-Weinstein reduction](https://arxiv.org/abs/dg-ga/9601009).
8. W. Donnelly and L. Freidel, [Local subsystems in gauge theory and gravity](https://arxiv.org/abs/1601.04744).
9. M. Schlichenmaier, [Berezin-Toeplitz quantization and Berezin transform](https://arxiv.org/abs/math/0009219).
10. A. Karabegov, [A formal model of Berezin-Toeplitz quantization](https://arxiv.org/abs/math/0607365).

These references provide context for structural realism, entanglement,
duality, gauge structure, constrained reduction, and operator compression. They
do not certify the specifically MTT source-selection claims.

## 42. Version delta: v1 to v2

This section is deliberately separate from the abstract and scientific
argument.

| Change | Reason |
|---|---|
| Added an abstract, scope statement, and four-level status vocabulary. | Prevent exact mathematics, established MTT results, conditional compilers, and interpretation from being conflated. |
| Reorganized the ontology into causal base, upper carrier, admissible sections, and physical reduction. | Make clear that the "upper world" is a descriptive level, not automatically another spacetime. |
| Expanded closure into an explicit repair-flow, fixed-point, linearization, semigroup, and Riesz-projector chain. | Explain where the central operator can come from rather than treating it as primitive. |
| Added the exact compression and leakage identities with a worked finite witness. | Ground the uncertainty and projection discussion in proved mathematics. |
| Expanded repair symmetry into stabilizer, projector covariance, observable kernel, and faithful quotient. | Distinguish source symmetry, gauge redundancy, and physical symmetry. |
| Integrated current `A47`, `A50`, and `B.QM.01` status while retaining the open same-source antecedents. | Reflect progress since v1 without overclaiming physical completion. |
| Replaced a single locality discussion with a hierarchy of causal, algebraic, fiberwise, projector, separability, and Bell notions. | Prevent global admissibility from being mistaken for superluminal causation. |
| Expanded Bell, entanglement, wave-particle, uncertainty, probability, and measurement sections. | Make measurement an ordinary record-forming process and state exactly what remains open. |
| Added role-based dimension tests and the explicit `1+3x3=4+6` decomposition. | Reconcile the world-in-world carrier without multiplying manifold dimensions or reviving literal Lens-Nil topology. |
| Clarified the shared circle and q79 Fu-Yau branch. | Separate phase/holonomy, physical time, constraint coordinates, and genuine internal geometry. |
| Expanded gravity and time boundaries. | Keep closure stress, Lorentzian action, repair time, phase, and arrow-of-time claims distinct. |
| Added comparisons with neighboring philosophies and established mathematical programs. | Identify what is interpretively distinctive without presenting standard mathematics as novel. |
| Added success, falsification, objection, glossary, diagram, and current-status sections. | Turn the document into a standalone philosophical paper and a usable research guide. |
| Preserved theorem ownership in the technical papers. | Avoid duplicating or silently strengthening theorem claims in an interpretive synthesis. |

Version 1 remains the historical concise interpretation. Version 2 is the
expanded current synthesis.
