# Provider-Neutral Projection Source Quotient and q79 Necessity Theorem

## Status

Claim ID: `CBF.T14`

Tier:

```text
EXACT_GENERAL
+ EXACT_BENCHMARK
+ CONDITIONAL_MTT_CLASSIFICATION
```

Machine decision:

```text
Q79_NOT_LOGICALLY_REQUIRED_PHYSICAL_SOURCE_STILL_REQUIRED
```

This theorem changes no physical acceptance count. `GAS`, `SYN` and `BV4`
remain `0/3`, and the seven physical endpoint rows remain `0/7`.

## 1. Verdict

The q79 endpoint is not a mathematical input of the fixed-point projection
itself. It is one proposed upstream realization of the data that projection
consumes. Consequently:

1. q79 is **not logically necessary** for the projection/compiler theorems;
2. q79 is **not yet sufficient** for selected physics, because its physical
   HYM, action, continuum-operator and BV rows remain open;
3. q79 is **not proved unique** among possible source realizations;
4. q79 is **compatible with the constraint-fiber interpretation only if** its
   vertical geometry satisfies the no-extra-clock, no-independent-initial-data
   and base-microcausality tests in the research charter;
5. the six-dimensional geometric endpoint can be bypassed, but a selected
   same-source action/operator/normalization object cannot.

The shortest accurate slogan is therefore

```text
bypass q79 geometry: possible in principle;
bypass selected source data: impossible in general.
```

This distinction prevents two opposite mistakes. We should not treat one old
compactification route as part of the definition of MTT projection. We should
also not imagine that projection can create masses, couplings or thresholds
after the source of those numbers has been discarded.

## 2. What the projection actually uses

The abstract fixed-point route in `RESEARCH_CHARTER.md` is

```text
closure repair F
  -> selected fixed point u_*
  -> linearization D F(u_*) or Hessian K
  -> selected spectral/tangent projector P
  -> compressed operators and transferred products
  -> four-dimensional physical records.
```

The associated-matter compiler `CBF.T13` uses

```text
D_tot = D_Y tensor I + Gamma_Y tensor D_X,
P_tot = I tensor P_0,
P_0 = projector onto ker(D_X).
```

Neither formula contains `79`, an eta9 coordinate, a Fu-Yau atlas or a
six-dimensional manifold. The formulas consume an internal graded operator,
its normalized kernel, a density/pairing, an external causal Dirac packet and
same-source action data. Their q79 origin is provenance, not an algebraic
argument of the compiler.

The seven-row theorem `CBF.T12` similarly consumes the typed packets

```text
GAS = geometry/action/fixed-point source,
SYN = spectral synthesis, projector, complement and Green data,
BV4 = four-dimensional BV externalization.
```

`CBF.T13` refines the associated-matter part of `BV4` through

```text
AMK = associated-matter kernel packet,
EXT4 = external four-dimensional causal packet,
DEN = density, cyclic pairing and normalization packet.
```

These are the genuine interface types. The name of the upstream provider is
not one of them.

## 3. Provider-neutral physical source object

Define a provider-neutral physical source object `S` to contain:

```text
S = (
  root source and selection certificate,
  four-dimensional causal base EXT4,
  GAS,
  SYN,
  AMK,
  DEN,
  BV4,
  same-source identity and intertwining certificates,
  constraint-fiber certificates,
  held-out physical comparison packet
).
```

The root provider may be

```text
q79 Hull-Strominger geometry,
direct closure-repair dynamics,
a selected finite spectral/action object,
an endpoint universality class,
or another certified source.
```

Every component must trace to one root source hash. A provider-neutral schema
does not mean a provenance-neutral schema. Importing a metric from one branch,
an action from another and observed couplings from a third fails the contract.

The machine-readable form is
`provider_neutral_physical_source_contract.schema.json`.

## 4. Source-preserving equivalence

Let `S` and `S'` be two provider-neutral source objects over isometric causal
bases. Write `S ~ S'` if there is a graded unitary or isometric intertwiner `W`
such that, on their declared domains,

```text
W u_*              = u_*',
W D_X              = D_X' W,
W K                = K' W,
W P                = P' W,
W G                = G' W,
W rho(g)           = rho'(g) W,
W i                = i' W_phys,
p' W               = W_phys p,
W H                = H' W,
```

and `W` preserves the density, cyclic pairing, action and every selected
transferred multilinear tensor. Base-local algebras and Green operators must
also intertwine.

This is deliberately stronger than equality of spectra or dimensions.
Equal `48`-dimensional kernels alone do not establish source equivalence.

## 5. Projection quotient theorem

### Theorem 5.1

The fixed-point, spectral-transfer and associated-matter BV compilers factor
through source-preserving equivalence:

```text
          quotient
Source  ------------>  Source / ~
  |                         |
  | Pi                      | Pi_bar
  v                         v
Physical records  =  Physical records.
```

Equivalently,

```text
Pi = Pi_bar o quotient.
```

### Proof

The selected projector is transported by `P'=W P W^{-1}`. Hence every
compressed operator obeys

```text
P' A' P' = W (P A P) W^{-1}.
```

The leakage identity, Feshbach operator and Riesz functional calculus are
natural under the same intertwiner. The contraction identities for `(i,p,H)`
then imply, by `CBF.T10`, that every transferred `m_n` intertwines. The product
Dirac identity gives

```text
(I tensor W) D_tot (I tensor W^{-1}) = D_tot'.
```

The kernel, representation, free quadratic action, cotangent pairing and
modewise causal operators are therefore carried to unitarily equivalent
objects. Because the density, cyclic pairing and interaction tensors are also
part of the equivalence relation, their overlap coefficients agree. Thus all
records emitted by the declared compiler agree up to the accepted physical
equivalence. This proves the factorization.

## 6. q79 necessity classification

Let `Q79` denote the category of completed q79 endpoint realizations and
`Src` the provider-neutral source category. A completed q79 construction would
define a realization map

```text
R_q79 : Q79 -> Src.
```

The physical compiler is then `Pi o R_q79`. Nothing in `Pi` requires that its
input lie in the image of `R_q79`. Any alternative realization

```text
R_alt : Alt -> Src
```

with the same certificates is equally admissible to the compiler.

### Corollary 6.1: q79 is not necessary at compiler tier

The exact non-q79 benchmark in Section 7 is an object of the formal source
interface and compiles through the same 80-to-48 projection. Therefore q79 is
not a logical prerequisite of the compiler.

### Boundary of the corollary

The benchmark is not a selected physical source. It disproves logical
necessity, not physical uniqueness. To prove that q79 is physically necessary
one would need a theorem that every accepted physical source object lies in
the image of `R_q79`. No such theorem is present in the current corpus or
curated authority graph.

To prove q79 sufficient, the active route must still construct an object of
`Src`: selected visible/hidden HYM data, action/Hessian, synthesis and Green
operator, normalized kernel/density and the BV pushforward. The exact discrete
authority `A11`, `q=79 mod 448` on its stated branch, does not by itself emit
those objects.

## 7. Exact 80-to-48 coordinate-equivalence witness

Take

```text
H_plus  = Q^64,
H_minus = Q^16,
D_+     = [I16  0  0  0] : H_plus -> H_minus,
D_X     = [[0,D_+^T],[D_+,0]].
```

Then

```text
rank(D_+)       = 16,
dim ker(D_+)    = 48,
coker(D_+)      = 0,
index(D_+)      = 48 = 3 x 16.
```

Let `P_0` select the three unused 16-dimensional blocks. Let `W` cyclically
permute those blocks and act identically on the 32-dimensional complement.
Then exactly

```text
W^3       = I,
W D_X W*  = D_X,
W P_0 W*  = P_0.
```

Because the A46/A50 action is family blind,

```text
rho_48 = I3 tensor rho_16,
```

`W` also commutes with the gauge and shared-circle generators. One source can
name the family frame `(0,1,2)` and another `(1,2,0)`; their provider
coordinates differ, but the projected physical object is the same equivalence
class.

The machine packet executes all 80-dimensional matrix identities exactly over
the integers. It labels both sources as benchmarks. It does not identify either
with the selected universe.

This witness makes the central point concrete: provider coordinates are not
physical merely because they occur before projection.

## 8. No-source, no-values theorem

The ability to forget q79 coordinates does not allow us to forget source
dynamics.

### Theorem 8.1

No rule depending only on the retained kernel, its dimension, gauge
representation and free projected operator can recover all complement
thresholds or interaction magnitudes.

### Threshold proof

Use the same 80-dimensional carrier and projector, but replace `D_+` by

```text
D_+^(1)=[I16,0,0,0],
D_+^(2)=[2 I16,0,0,0].
```

Both have the same 48-dimensional kernel, projector, family representation and
zero-mode projection:

```text
P D_X^(1) P = P D_X^(2) P = 0.
```

Their nonzero squared eigenvalues are respectively `1` and `4`; their
complement gaps are `1` and `2`. Thus the retained free zero-mode structure
does not determine the threshold scale.

### Interaction proof

Let the source contain a normalized one-dimensional invariant interaction
line spanned by `I`. Define

```text
T_1 = I,
T_2 = 2 I.
```

The free operator, projector and representation are identical. But the
unitarily invariant squared tensor norms are

```text
||T_1||^2 = 1,
||T_2||^2 = 4.
```

No source-preserving unitary relates them. A forgetful map that discards `T`
therefore identifies two sources with different physical interaction values.
No function of the remaining data can recover which value was selected.

This is an exact non-identifiability theorem. It applies directly to the hope
that a projector, family count or gauge representation alone could emit
Yukawa magnitudes, masses or nonlinear threshold rows.

## 9. Does q79 fit the constraint-fiber picture?

Conditionally, yes. Automatically, no.

It fits if its six-dimensional data are a mathematical realization of the
upper constraint source and satisfy all of the following:

1. no independent causal cone or clock is assigned to the vertical
   coordinates;
2. no freely specifiable vertical initial data survive independently of base
   evolution;
3. vertical relabelings preserving the source are gauge or representation;
4. observable effects descend through fixed points, holonomy, index, spectra
   and transfer;
5. the reduced net remains microcausal on the four-dimensional base.

In that interpretation, q79 is not a second physical arena. It is a highly
structured model of the admissibility constraints whose fixed point and
linearization generate the lower theory.

If, instead, q79 vertical modes carry independent propagating data, energy or
observable Kaluza-Klein towers, then they are physical internal degrees of
freedom. They cannot be rebranded as pure constraints. The current q79 program
has not yet supplied the certificate that decides this distinction.

Thus q79 fits the new viewpoint well as a **provider candidate**, but it does
not yet fit perfectly as a proved pure constraint fiber.

## 10. What purpose q79 still serves

The q79 program remains valuable for four reasons.

1. **Concrete existence route.** It attempts to construct rather than merely
   postulate the metric, connection, action, operator and normalized modes.
2. **Topological discreteness.** The q79 branch can turn continuous source
   ambiguity into arithmetic and cohomological selection questions.
3. **UV completion candidate.** A Hull-Strominger realization may provide
   anomaly/Bianchi and high-energy consistency not visible in a finite model.
4. **Cross-check.** If a direct repair source and q79 independently descend to
   the same provider-neutral equivalence class, that agreement would be much
   stronger than either route alone.

What q79 must not do is become an unquestioned premise merely because much
work has accumulated around it. `A11` establishes a discrete branch theorem,
not that nature must realize the full q79 endpoint.

## 11. Alternative routes to physicality

### 11.1 Direct closure-repair route

Select a nonlinear repair/action object directly over the four-dimensional
causal base:

```text
F or S
  -> selected u_*
  -> K=D F(u_*) or Hess(S)(u_*)
  -> P,G and transferred products
  -> AMK+DEN+BV4.
```

This is the most faithful route to the current MTT philosophy because the
operator is the tangent shadow of repair. It bypasses a six-dimensional
compactification but not the selected fixed point or action.

### 11.2 Finite spectral/action route

Treat a selected finite projected algebra, graded Hilbert space, Dirac
operator, real structure, density and spectral/cyclic action as the exact
source. The Chamseddine-Connes spectral action is an external precedent for
operator-first internal geometry, not evidence that the MTT source is already
selected.

This route is attractive for the already-exact 48-state and finite-response
packets. Its hard question is why this finite object, action and scale are
selected before empirical replay.

### 11.3 Universality-class route

Prove that a class of upper endpoints, possibly including q79, maps to one
provider-neutral equivalence class with controlled errors. Then the detailed
endpoint is not physical; only its universal fixed-point data are.

This is the cleanest mathematical realization of the user's intuition. It is
also demanding: equality of dimensions, indices or gauge groups is not enough.
The action, density, normalized interactions, Green operators and observables
must agree or converge.

### 11.4 Base-local algebra/BV route

Start from a locally covariant or factorization-algebra net on the
four-dimensional base and let upper closure data constrain its admissible
objects and states. This naturally respects the idea that locality is physical
on the base while global upper geometry constrains states. It still requires a
selected action, state and normalization.

### 11.5 Declared few-parameter route

If no zero-parameter selection exists, adopt one to three declared primitives
at source level, propagate them through the exact compiler, and reserve enough
held-out observables for a real test. This can be scientifically valuable, but
its claim is an economical effective reconstruction rather than a no-knob
derivation.

## 12. Which route should be targeted now?

The correct strategy is parallel, not exclusive:

```text
q79 worker:
  continue ETA9.QD1 -> HYM/GAS/SYN source construction;

this constraint-fiber worker:
  construct a direct repair/action provider for the same neutral contract;

comparison gate:
  test whether both descend to one source-equivalence class.
```

The immediate target here should be the first provider-neutral physical row,
not another q79-specific finite surrogate:

```text
PN.01  selected direct repair/action and stationary fixed point;
PN.02  Hessian, domains, projector, reduced Green and causal base binding;
PN.03  normalized 48-state AMK and density from that same source;
PN.04  one invariant interaction/threshold row emitted without observed input;
PN.05  BV pushforward and held-out physical comparison.
```

`PN.01-PN.03` attack the existence and normalization problem. `PN.04` is the
first decisive numerical test. If the direct route cannot emit even one
held-out scalar without importing it, it has not bypassed the q79 blocker; it
has only renamed it.

## 13. Relation to established external mathematics

The alternatives are not mathematically eccentric:

- the spectral action packages internal physics in operator data rather than
  a conventional extra-dimensional manifold;
- locally covariant QFT formulates physical content functorially over causal
  spacetimes;
- factorization algebras encode local-to-global observables without treating
  every organizing variable as physical spacetime.

These frameworks support the legitimacy of a provider-neutral interface. They
do not validate MTT's source-selection claims, q79, or any numerical result.

Primary references used only as context:

- A. Chamseddine and A. Connes, *The Spectral Action Principle*,
  https://arxiv.org/abs/hep-th/9606001
- R. Brunetti, K. Fredenhagen and R. Verch, *The generally covariant locality
  principle*, https://arxiv.org/abs/math-ph/0112041
- K. Costello and O. Gwilliam, *Factorization algebra*,
  https://arxiv.org/abs/2310.06137

## 14. Exact claims and nonclaims

### Proved here

- the projection/compiler interface is provider neutral;
- source-preserving equivalent realizations have equivalent projected records;
- a non-q79 exact 80-to-48 benchmark passes the same free-matter compiler;
- q79 is therefore not logically necessary at compiler tier;
- complement thresholds and normalized interaction magnitudes cannot be
  recovered from the retained free structure alone;
- the q79-specific endpoint contract is one refinement of a more general
  source interface;
- the precise constraint-fiber conditions under which q79 is compatible.

### Not proved here

- a selected non-q79 physical source;
- physical sufficiency or physical uniqueness of q79;
- a completed physical q79 endpoint;
- any accepted value for a mass, Yukawa coupling, threshold or precision row;
- a four-dimensional spacetime derivation;
- quantum BV/QME or continuum interacting closure.

## 15. Reproduction

```text
python build_provider_neutral_projection_source_quotient.py
python verify_provider_neutral_projection_source_quotient.py
python -m unittest tests.test_provider_neutral_projection_source_quotient -v
```

The generated certificate is
`provider_neutral_projection_source_quotient.packet.json`.

## 16. Final interpretation

The q79 program is no longer the hidden definition of the target. It is one
candidate implementation of a now-explicit provider interface.

That is a conceptual advance, not a retreat from q79. If q79 closes, it will
be valuable because it constructs the right source object, not because the
number `79` was inserted into the projection. If a direct repair or finite
spectral source closes first, the same compiler can be used without q79. If
both close and land in one equivalence class, MTT gains a genuine universality
result.

What cannot be skipped is reality's selection of one normalized action/source
class. Projection explains how such a source appears in four-dimensional
physics. It does not select the source from nothing.
