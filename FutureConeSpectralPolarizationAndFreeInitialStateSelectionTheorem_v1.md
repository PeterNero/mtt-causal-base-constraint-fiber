# Future-Cone Spectral Polarization and Free Initial-State Selection Theorem v1

**Claim ID:** `CBF.T45`
**Date:** 2026-08-30
**Status:** exact selected free initial state on the homogeneous flat direct
branch; generic cosmological state, determinant-line phase, interacting BV
transport, cutoff removal, `G1` and full `G2` remain open

## 1. Result

CBF.T44 constructed a state-free global causal object,

```text
C_H[V_plus,V_minus]
  = S_H[V_minus]^(-1) star S_H[V_plus],
C_H[V,V]=1,
```

and proved that a scalar functional requires a state,

```text
Z_omega[V_plus,V_minus]=omega(C_H[V_plus,V_minus]).
```

That theorem deliberately worked on a generic time-oriented globally
hyperbolic background. Such a background has a nonempty Hadamard state space,
but it need not have a preferred vacuum.

The direct route also contains a narrower object. CBF.T43 uses the homogeneous
flat branch, the future time orientation, the selected finite coordinate

```text
t_*=(1-sqrt(13))/6,
```

and a constant positive radial amplitude `H`. On this branch the product
Dirac operator has a time-translation generator `K_H`. Its three physical
mass moduli are strictly nonzero. The future spectral projector therefore
exists without a zero-mode convention:

```text
P_fut
  = 1_(0,infinity)(K_H)
  = (I+K_H |K_H|^(-1))/2.                    (1.1)
```

Equation (1.1) determines one pure quasifree free CAR state `omega_fut`.
Within the class of time-translation-invariant, gauge-compatible pure
quasifree states satisfying the selected future ground-state spectrum
condition, it is unique. No density matrix, temperature or continuous state
coordinate is fitted.

The same projector has an independent repair-boundary characterization. For
the oriented first-order half-line equation

```text
(partial_s+K_H)u=0,       s>=0,               (1.2)
```

the boundary values of square-integrable or decaying solutions are exactly
`Ran(P_fut)`. Thus its Calderon projector is

```text
C_+=P_fut.                                      (1.3)
```

This is the precise sense in which closure repair can select a quantum
polarization on this branch. The orientation and the first-order charge are
essential. The positive Hessian semigroup

```text
exp(-s|K_H|)
```

damps both spectral signs and selects no polarization.

The T44 scalar is now defined on this branch by

```text
Z_fut[V_plus,V_minus]
  =omega_fut(C_H[V_plus,V_minus]),
Z_fut[V,V]=1.                                  (1.4)
```

This closes the free initial-state subclause of `G2` on the homogeneous flat
direct branch. It does not construct an interacting fixed-coupling state,
remove a regulator, trivialize the relative determinant line, select a
cosmological state or promote the top-level physical `G2` gate.

## 2. Typed inherited data

The construction uses four already separated types.

### 2.1 Physical Weyl carrier

CBF.T43 distinguishes

```text
48 physical left-Weyl internal labels,
2 spin components per left-Weyl field,
96 continuum off-shell Weyl components,
96 dimensions in the separate KO6 real completion.
```

The final two occurrences of `96` are not multiplied. The exact executable
witness below uses the first `96`: 48 physical Weyl labels times two energy
signs at zero spatial momentum. It does not reinterpret the KO6 completion
as another set of particles.

### 2.2 Direct causal operator

CBF.T25 supplies the Green-hyperbolic direct family

```text
D_dir(t;A,H)=D_A+Y_t(H).
```

On the covariantly constant neutral flat branch,

```text
D_dir(t,H)
  =D_Y tensor I96+Gamma_Y tensor H D_phys(t),

D_dir(t,H)^2
  =D_Y^2 tensor I96+H^2 I tensor D_phys(t)^2.  (2.1)
```

Passing to a Cauchy surface gives a self-adjoint one-particle Hamiltonian
whose momentum symbol may be written schematically as

```text
K_H(p)=alpha.p tensor I96+beta tensor H D_phys(t_*),

K_H(p)^2
  =|p|^2 I+H^2 D_phys(t_*)^2.                 (2.2)
```

Equation (2.2), not an identification of internal directions with space,
controls the energy gap.

### 2.3 Free CAR state space

The selected free Dirac CAR theorem gives a representation-independent even
observable net and a nonempty convex space of positive normalized quasifree
Hadamard states. It explicitly does not choose one state on a generic curved
background.

### 2.4 T44 causal element

The T44 relative element is defined in the algebra before a representation or
state is selected. Its equal-source identity, causal factorization and common
central phase cancellation are inherited unchanged.

## 3. Exact gap theorem

CBF.T27 gives

```text
spec(D_phys(t))
 ={ +(1-2t)^16, -(1-2t)^16,
    +(1-t)^16,  -(1-t)^16,
    +(1+t)^16,  -(1+t)^16 }.                  (3.1)
```

At `t=t_*`, define the positive moduli

```text
mu_4  =1-2t_*=(2+sqrt(13))/3,
mu_2m =1-t_* =(5+sqrt(13))/6,
mu_2p =1+t_* =(7-sqrt(13))/6.                (3.2)
```

They obey the exact order

```text
mu_4 > mu_2m > mu_2p > 0.                    (3.3)
```

Indeed,

```text
mu_4-mu_2m=(sqrt(13)-1)/6>0,
mu_2m-mu_2p=(sqrt(13)-1)/3>0,
mu_2p=(7-sqrt(13))/6>0,
```

where the last inequality follows from `49>13`. Hence `t_*` avoids all three
singular walls `-1`, `1/2` and `1`.

### Theorem 3.1: direct-branch mass gap

For `H>0`, the Hamiltonian (2.2) has no zero-energy mode and

```text
|K_H(p)| >= H(7-sqrt(13))/6.                 (3.4)
```

### Proof

On each of the three rank-16 physical Weyl branches, equation (2.2) gives

```text
E_j(p)^2=|p|^2+H^2 mu_j^2.
```

Equation (3.3) gives `E_j(p)>=H mu_2p>0`. QED.

The absolute value `H` remains an inherited unresolved radial scale. The
statement is exact for every `H>0`; T45 neither fits `H` nor promotes it to an
SI mass.

## 4. Future spectral polarization

Because `0` is outside the spectrum, Borel functional calculus defines

```text
P_fut =1_(0,infinity)(K_H),
P_past=1_(-infinity,0)(K_H)=I-P_fut.         (4.1)
```

The sign formula in (1.1) follows immediately. Therefore

```text
P_fut^2=P_fut=P_fut^*,
P_past^2=P_past=P_past^*,
P_fut P_past=0,
P_fut+P_past=I.                              (4.2)
```

Let `Gamma` denote the self-dual CAR conjugation. The real structure of the
neutral direct family pairs positive and negative energy:

```text
Gamma K_H Gamma=-K_H.                        (4.3)
```

Functional calculus then gives

```text
Gamma P_fut Gamma=P_past,
P_fut+Gamma P_fut Gamma=I.                   (4.4)
```

Thus `P_fut` is a basis projection for the self-dual CAR algebra.

### Theorem 4.1: unique future ground-state covariance

Fix the homogeneous flat branch, its future time orientation, `t=t_*` and
`H>0`. Among gauge-compatible pure quasifree states invariant under the
time-translation group and satisfying the future ground-state spectrum
condition, the covariance is uniquely `P_fut`.

### Proof

A pure gauge-compatible quasifree state is determined by a basis projection
`P`. Time-translation invariance makes `P` reduce the spectral measure of
`K_H`. The future ground-state spectrum condition occupies the positive
spectral subspace and excludes the negative one. Since there is no zero
spectral subspace, `P=1_(0,infinity)(K_H)=P_fut`. Degeneracies inside one
mass branch do not create another covariance because the spectral projector
is the identity on the complete positive-energy eigenspace. QED.

Thermal and other stationary mixed states are not counterexamples: they do
not satisfy the pure ground-state clause. A nonstationary preparation is
also a different typed object.

## 5. Half-line and repair selection

Consider the oriented first-order boundary problem (1.2). By the spectral
theorem, a boundary component with `K_H` eigenvalue `lambda` evolves as

```text
u_lambda(s)=exp(-s lambda)u_lambda(0).        (5.1)
```

For `lambda>0` it decays and is square integrable on the positive half-line.
For `lambda<0` it grows. There is no `lambda=0` case by Theorem 3.1.

### Theorem 5.1: Calderon/repair equivalence

The space of boundary values of decaying solutions of (1.2) is exactly
`Ran(P_fut)`. Consequently the positive-half-line Calderon projector is
`C_+=P_fut`.

### Proof

Apply (5.1) to the positive and negative spectral measures of `K_H`.
Square-integrability retains every positive component and removes every
negative component. This is precisely the range of (4.1). QED.

This supplies a concrete upstream reading:

```text
oriented first-order closure charge
  -> one-sided admissible repair boundary data
  -> spectral polarization
  -> quasifree state
  -> scalar causal functional.              (5.2)
```

It also identifies a sharp limitation. If the repair generator is replaced
by the positive Hessian `|K_H|` or `K_H^2`, then all nonzero modes decay:

```text
exp(-s|K_H|)u(0) -> 0
```

for both original energy signs. Squaring erases exactly the sign needed for
polarization. Therefore a positive closure cost or heat kernel by itself
cannot choose the quantum vacuum. MTT needs its oriented first-order charge,
not merely its Hessian shadow.

The coordinate `s` in (1.2) is an auxiliary half-line parameter. T45 does
not identify it with Lorentzian time, the internal shared circle or a second
physical dimension. On the static analytic flat branch, the same boundary
problem is the familiar Euclidean half-space/Calderon construction. Extending
that interpretation to a curved q79 background requires the additional
analytic and boundary hypotheses stated in Section 10.

## 6. Quasifree state and Hadamard property

The basis projection defines a pure quasifree CAR state `omega_fut` through
its two-point covariance. Positivity follows from `0<=P_fut<=I`, normalization
from the CAR state construction, and purity from `P_fut^2=P_fut`.

The flat background, static smooth mass endomorphism and positive-frequency
spectrum place this state in the standard static Dirac ground-state class.
The static Dirac ground-state theorem therefore supplies the Hadamard
microlocal condition. Restriction gives a positive state on the even and
gauge-invariant observable algebra. Gauge transformations preserving the
fixed homogeneous background commute with the spectral construction.

This is stronger than merely exhibiting some Hadamard state. It selects one
state on one declared branch. It is deliberately weaker than claiming a
natural vacuum on every globally hyperbolic spacetime.

The construction introduces no new state parameter. It does inherit:

```text
the selected future time orientation,
t_*=(1-sqrt(13))/6,
the branch amplitude H>0.
```

The first is discrete structure, the second is an earlier selected internal
coordinate, and the third still lacks an absolute physical scale theorem.

## 7. Scalarization of T44

Use `omega_fut` as the initial Hadamard state for the T44 local-formal
relative element. Then (1.4) is a well-typed formal scalar series.

The equal-source identity is automatic:

```text
Z_fut[V,V]
  =omega_fut(1)
  =1.                                             (7.1)
```

For unequal sources, `Z_fut` is no longer an arbitrary member of the state
family: the future spectral condition has chosen the functional. The exact
two-mode witness used by T44 makes the orientation dependence visible:

```text
C=diag((3+4i)/5,(3-4i)/5),

omega_fut(C) =(3+4i)/5,
omega_past(C)=(3-4i)/5.                         (7.2)
```

Both give one on the equal-source identity. The selected time orientation
chooses the first covariance on the declared branch.

Equation (7.1) does not compute a nonperturbative determinant. The relative
S-matrix is still local-formal, and a source-dependent determinant-line phase
can change (7.2). T45 supplies the initial state, not the missing phase
trivialization or fixed-coupling completion.

## 8. Time reversal, branch choice and binary root

Reversing the time orientation sends

```text
K_H -> -K_H,
P_fut -> P_past.                               (8.1)
```

Thus there are two mathematically valid complementary oriented
polarizations. They are not two simultaneously selected states inside one
time-oriented object. The existing branch structure chooses which cone is
called future; a theorem about cosmological branch selection would be a
separate result.

The balanced binary-root unitary `Phi` intertwines the two free Dirac
presentations. Functional calculus gives

```text
Phi P_fut,+ Phi^(-1)=P_fut,-.                  (8.2)
```

Hence the corresponding quasifree states and GNS representations transport
under the already proved root equivalence. The binary root does not select a
second vacuum, an arrow of time or another observable universe.

The internal shared circle likewise supplies no replacement for (8.1). Its
holonomy may constrain internal phases, but it is not the future cone of the
four-dimensional causal base.

## 9. Relation to T38 and closure repair

CBF.T38 selects the radial marginal `delta_H`. That result and T45 act on
different state coordinates:

```text
T38: homogeneous radial amplitude marginal,
T45: fermionic positive-frequency CAR polarization.
```

Neither implies the other. A full state may have radial marginal `delta_H`
and still carry many fermionic covariances; conversely a fermionic vacuum
does not select the Higgs radial law. Their same-branch product is a candidate
free initial state for the combined local-formal theory, but the interacting
BV pushforward must still prove that the constraints and Ward identities are
preserved.

The repair lesson is correspondingly precise:

```text
positive closure cost -> stability but no energy sign,
oriented first-order closure charge -> future/past split,
one-sided decay -> selected free polarization.             (9.1)
```

This is a genuine extension of the closure-repair idea. It is not a claim
that every positive fixed-point flow secretly is quantum mechanics.

## 10. Generic-background no-promotion theorem

The construction relies on three extra structures:

1. a stationary homogeneous flat background;
2. a selected future time-translation generator;
3. a spectral gap at zero.

A generic globally hyperbolic cosmological background need not possess the
second structure. Without a stationary generator, `1_(0,infinity)(K_H)` is
not available as a global invariant prescription. Local covariance and the
Hadamard wavefront condition select a state space, not one state.

### Theorem 10.1: branch-specificity

T45 cannot be promoted, using only the T25 generic causal data, to a natural
preferred state on every object of the framed globally hyperbolic category.

### Proof

The T25 generic data supply advanced/retarded propagation and a time
orientation, but no natural stationary Hamiltonian or asymptotic boundary.
The positive-energy functional calculus used in (4.1) is therefore absent.
Moreover the standard natural-state no-go excludes a generally covariant
preferred state for nontrivial dynamically local theories under its stated
hypotheses. T45 evades that no-go only by restricting to the extra flat
stationary branch structure; deleting that structure deletes the selector.
QED.

There are rigorous routes beyond strict stationarity, but each adds named
data: asymptotically static in/out conditions, an analytic Euclidean
reflection/Calderon problem, or an independently selected initial density
matrix. None is currently emitted by the q79 physical endpoint.

## 11. Gate and parameter ledger

The resulting gate ledger is

```text
direct local one-loop G0:                    closed by T43,
global state-free causal evolution:          closed by T44,
flat-branch free initial state:              closed by T45,
flat-branch local-formal scalarization:      defined by T45,
generic curved/cosmological state:           open,
relative determinant phase/holonomy:         open,
interacting QME-preserving BV pushforward:   open,
fixed-coupling cutoff removal and state:     open,
physical tangent metric G1:                  open.          (11.1)
```

At the subclause level,

```text
G2a free initial state on flat branch:       closed,
G2b interacting BV/state pushforward:        open,
G2c positive fixed-coupling continuum state: open.
```

The top-level T41 gate count therefore remains `0/3`; component progress is
not renamed as physical gate acceptance. Physical packet and row acceptance
also remain `0/3` and `0/7`.

The parameter ledger is

```text
new observed inputs:              0,
new fitted parameters:            0,
new continuous state selectors:   0,
new thermal parameters:           0,
inherited discrete orientation:   1,
inherited unresolved scale:       H.                         (11.2)
```

## 12. External mathematical context

Wrochna proves that the ground state for the Dirac equation on Minkowski
space with static smooth external potentials is Hadamard
([arXiv:1108.2982](https://arxiv.org/abs/1108.2982)). Gerard and Stoskopf prove
the Hadamard property of Dirac in/out states on asymptotically static
spacetimes ([arXiv:2108.11955](https://arxiv.org/abs/2108.11955)). These
results support the branch-specific state construction; they do not provide
the missing q79 cosmological boundary.

Fewster reviews the natural-state no-go in dynamically local locally
covariant QFT ([arXiv:1502.04642](https://arxiv.org/abs/1502.04642)). Gerard
and Wrochna construct analytic Hadamard states from Euclidean Calderon
projectors under additional analytic hypotheses
([arXiv:1706.08942](https://arxiv.org/abs/1706.08942)). Barvinsky and Kolganov
make explicit that a Schwinger-Keldysh scalar functional carries initial
density-matrix data ([arXiv:2309.03687](https://arxiv.org/abs/2309.03687)).

T45 uses these as primary mathematical context. Its MTT-specific contribution
is the exact same-source identification of the selected `t_*` direct mass
gap, future-cone spectral projector and oriented closure-repair boundary, with
the positive-Hessian nonselection theorem kept explicit.

## 13. Frontier after T45

The T44 state cutset is no longer uniformly open. It is now factored:

```text
generic causal operator:                  state free and closed,
homogeneous flat direct initial state:    selected and closed,
generic cosmological initial state:       open,
interacting/fixed-coupling state:         open.
```

The most direct next target is not another vacuum ansatz. It is to transport
the selected flat initial state through the existing local QME/BV map and
prove one of the two genuine exits:

1. a QME-preserving interacting state at fixed coupling with positivity and
   regulator-independent convergence; or
2. a selected asymptotic/analytic q79 boundary whose Calderon or in-state
   projector reduces to `P_fut` on the flat branch.

In parallel, `G1` can be attacked independently by deriving the physical
tangent pairing and Hessian transport.

## 14. Reproduction

Run

```text
python build_future_cone_spectral_polarization.py
python verify_future_cone_spectral_polarization.py
python -m unittest tests.test_future_cone_spectral_polarization -v
```

The builder verifies the pinned sources, exact `Q(sqrt(13))` gap and ordering,
the 48/48 zero-momentum reduced-Weyl polarization, charge-conjugation
exchange, half-line decay selection, positive-Hessian nonselection, T44
scalar witness, root neutrality and unchanged physical counters. The
machine-readable result is
`future_cone_spectral_polarization.packet.json`.
