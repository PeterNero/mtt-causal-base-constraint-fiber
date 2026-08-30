# Quantum Radial-Anchor Ward Identity and Tadpole-Selection Boundary Theorem v1

**Claim:** CBF.T37

**Date:** 2026-08-30

**Status:** exact differentiated-pushforward Ward identity; exact sufficient
QJ1 mechanisms; exact proof that the q79 formal QME permits but does not select
radial tadpole cancellation; exact T35 tadpole obstruction and zero-source
state-anchor reduction; no selected interacting q79 state, radial Ward
primitive or physical QJ1 certificate.

## 1. Result

CBF.T36 reduced closure-jet matching to three typed quantum certificates. The
first is

```text
QJ1: d Gamma(H)=0,
```

where `H` is the CBF.T34 radial point. The question is whether this equality
follows from the existing upper action and projection naturality.

CBF.T37 gives a precise answer.

For every differentiable finite or regulated pushforward, the radial derivative
of the effective action is the expectation value of one covariant insertion:

```text
Gamma'(H)=<D_H S-hbar A_H>_H.                         (1.1)
```

Here `D_H S` includes the horizontal derivative of the action along the chosen
cycle transport, while `A_H` is the logarithmic derivative of the transported
measure and determinant density. Equation (1.1) proves that action naturality
alone is insufficient. QJ1 follows if the insertion vanishes pointwise, is
quantum-BV exact with an anomaly-free Stokes functional, is odd under a
centered measure-preserving involution, or is anchored by a selected
zero-source state.

The current q79 quantum results close an important part of this list. The
selected three-family carrier has zero local gauge-anomaly class and admits an
all-orders formal local QME normalization scheme. Since the Higgs radius is a
gauge-invariant ghost-zero coordinate, however, the local counterterms

```text
c+a h^2+b h^4
```

are also QME compatible. Their derivative at `H` is `2aH+4bH^3`, which can be
arbitrary. Thus the q79 QME proves that a tadpole-preserving scheme exists; it
does not select that scheme or force QJ1.

The strongest positive reduction is state-first. If one selected interacting
q79 state supplies a zero-source radial expectation `H_state`, then the
Legendre effective action obeys

```text
Gamma'(H_state)=0                                     (1.2)
```

identically. Physical QJ1 is therefore reduced to the same-source equality

```text
H_state=H_T34.                                        (1.3)
```

The q79 corpus already constructs nonempty formal physical state spaces and
their transport, but explicitly does not select one preferred interacting
state. Equation (1.3), or an explicit BV-exact radial Ward primitive, is the
remaining source theorem.

Finally, the actual T35 determinant is tested rather than discussed
abstractly. In MSbar at `mu=Lambda`, its unrenormalized one-loop tadpole at the
T34 point is nonzero:

```text
V_F'(H)/(kappa_F Lambda^3)
=-100.1144836274302795882555068876969....              (1.4)
```

Both determinant-normalization branches therefore shift the tree stationary
point. No accidental QJ1 cancellation has been found.

## 2. Differentiated pushforward identity

Let `h` be a retained radial coordinate. After transporting every integration
cycle `L_h` to one reference cycle `L`, write the regulated Euclidean
partition function as

```text
Z(h)=int_L exp[-S_h(y)/hbar] r_h(y) dmu(y),            (2.1)
Gamma(h)=-hbar log Z(h).                              (2.2)
```

The Radon-Nikodym factor `r_h` contains the transported measure, determinant
half-density and the Jacobian of cycle transport. Define

```text
A_h(y)=partial_h log r_h(y).                           (2.3)
```

If differentiation under the integral is valid and no uncancelled boundary
term is produced, then

```text
partial_h Z
=int_L[-partial_h S_h/hbar+A_h]
       exp[-S_h/hbar] r_h dmu.                        (2.4)
```

Dividing by `Z` gives the exact identity

```text
Gamma'(h)=<partial_h S_h-hbar A_h>_h.                 (2.5)
```

For a nontrivial horizontal transport, `partial_h S_h` in (2.5) is replaced
by its covariant derivative `D_h S`; the Lie derivative of the measure and
cycle is absorbed into `A_h`. An actual boundary contribution must be added
separately and proved zero. Thus the fully typed form is

```text
Gamma'(H)
=<D_H S-hbar A_H>_H+B_H/Z(H).                        (2.6)
```

Equation (2.6) is the radial Schwinger-Dyson/Ward obstruction. A commuting
action square controls `D_H S`, but it says nothing about `A_H`, `B_H` or the
expectation functional unless those objects are included in the projection
contract.

## 3. Exact sufficient mechanisms for QJ1

Equation (2.6) gives four distinct sufficient mechanisms.

### 3.1 Pointwise horizontal stationarity

If

```text
D_H S(y)=0 for every integrated y,
A_H(y)=0,
B_H=0,                                                (3.1)
```

then QJ1 follows immediately. Classical stationarity only at `(H,y_*)` is
weaker than (3.1). The odd Gaussian witness of CBF.T36 is an exact
counterexample to replacing pointwise stationarity by stationarity at one
fiber point.

### 3.2 Quantum-BV exact radial insertion

Let `s_q` be the quantum BV differential in a selected QME scheme. If

```text
D_H S-hbar A_H=s_q Psi_H                              (3.2)
```

and the integration functional obeys quantum BV Stokes,

```text
<s_q X>_H=0,                                          (3.3)
```

with no cycle boundary, then QJ1 follows. This is the genuine radial Ward
route. A vanishing gauge-anomaly class makes (3.3) available at the formal
local tier, but it does not provide the primitive `Psi_H` in (3.2).

### 3.3 Centered involution

Suppose an involution preserves the transported action, measure and cycle,
fixes `h=H`, and sends the insertion in (2.6) to its negative. Its expectation
then vanishes. Ordinary gauge-even symmetry `h -> -h` exchanges the two
nonzero broken branches and is not centered at either `+H` or `-H`; it does
not protect their locations.

### 3.4 Zero-source state anchor

Let

```text
W(J)=hbar log Z(J),
phi(J)=dW/dJ,
Gamma(phi)=J phi-W(J).                                (3.4)
```

Where the Legendre transform exists,

```text
dGamma/dphi=J.                                        (3.5)
```

Therefore the zero-source expectation

```text
H_state=phi(0)                                        (3.6)
```

obeys (1.2). This does not impose a tadpole counterterm after the fact. It
defines the quantum background by the selected state. To preserve the T34
number, one must additionally prove (1.3).

## 4. Why gauge QME does not select the radial anchor

The q79 local-QME theorem proves that the five nontrivial local gauge-anomaly
coefficients vanish and that a formal all-orders QME normalization scheme
exists. The state-space theorems construct nonempty formal positive physical
state spaces and transport them under admissible changes of Hadamard seed,
renormalization prescription and gauge fixing.

Those results are necessary but not sufficient for QJ1. The radial coordinate
is gauge invariant. Consequently

```text
C_(c,a,b)(h)=c+a h^2+b h^4                            (4.1)
```

is a gauge-invariant local counterterm in the declared four-dimensional
power-counting class. Its radial tadpole shift is

```text
C_(c,a,b)'(H)=2aH+4bH^3.                              (4.2)
```

For `H>0`, the map `(a,b)->2aH+4bH^3` is surjective. In particular, any
desired shift `r` is obtained with `a=r/(2H), b=0`. Hence two QME-compatible
normalizations can have different radial tadpoles.

This proves both sides of the formal result:

```text
QME-compatible QJ1 scheme exists: yes,
QME uniquely selects QJ1:             no.             (4.3)
```

The Nielsen identity controls gauge-parameter transport of the effective
potential and its extrema. It likewise does not choose which radial
normalization or interacting state realizes (1.3).

## 5. The QJ1 counterterm orbit

Write the T35 loop as

```text
V_F(h)=-kappa_F h^4 L(h),
L(h)=q4_* log(h^2/mu^2)+L4_*-c_scheme q4_*.           (5.1)
```

At `h=H`, let `L_H=L(H)`. Then

```text
V_F'(H)=-2 kappa_F H^3(2L_H+q4_*).                    (5.2)
```

For a counterterm

```text
delta V=delta Omega+delta m2 h^2+delta lambda h^4,    (5.3)
```

QJ1 is the single affine equation

```text
delta m2+2H^2 delta lambda
=kappa_F H^2(2L_H+q4_*).                              (5.4)
```

Thus QJ1 alone leaves one nonconstant counterterm degree of freedom and the
independent additive constant. QJ2 intersects (5.4) at the unique T35 pair

```text
delta m2=-2 kappa_F q4_* H^2,
delta lambda=kappa_F[L_H+(3/2)q4_*].                  (5.5)
```

QJ0 then fixes `delta Omega`. This recovers T36's certificate hierarchy by a
direct first-jet calculation.

Because the gauge-anomaly class vanishes, (5.4) can be imposed recursively in
a local formal QME scheme. That establishes compatibility and existence, not
an upper-MTT selection theorem.

## 6. Exact T35 obstruction at the T34 point

Use the same-source T34/T35 data

```text
H/Lambda =1.3211016293754684937241140791004495...,
q4_*      =16.523658588392582678814093766176385...,
L4_*      =18.176066017544062361087042190541135....   (6.1)
```

At `mu=Lambda` and `c_scheme=3/2`,

```text
L_H=2.5931309140518811873072225305529068...,
2L_H+q4_*=21.709920416496345053428538827282199....    (6.2)
```

Substitution into (5.2) gives (1.4). The two determinant exponents give

```text
complex determinant, kappa_F=1/pi^2:
V_F'(H)/Lambda^3=-10.1437179808726809888641690208743...,

Pfaffian half, kappa_F=1/(2pi^2):
V_F'(H)/Lambda^3=-5.07185899043634049443208451043716.... (6.3)
```

The normalized QJ1 line is

```text
delta m2/(kappa_F Lambda^2)
+2(H^2/Lambda^2) delta lambda/kappa_F
=37.8905306758110426301454836733130....               (6.4)
```

There is one renormalization scale at which the bare fermion loop alone has
zero tadpole:

```text
mu_tad/H
=exp[(L4_*/q4_*-c_scheme+1/2)/2].                    (6.5)
```

In MSbar this is

```text
mu_tad/H=1.05127241877369275682425083137815...,
mu_tad/Lambda=1.38883770535941535495668312689211....  (6.6)
```

Equation (6.5) is a scheme-scale coordinate, not a physical prediction. The
current upper action does not select it, and changing `mu` without the
corresponding running of all couplings is not a substitute for RG matching.

## 7. Constraint-first interpretation

CBF.T17 proves that a linear upper normal-pressure action can pull back along
a curved closure graph to a nonlinear lower action with a classical fixed
point. CBF.T34 similarly derives a selected finite radial stationary point at
its declared action tier.

Quantum projection requires more structure. The correct object is not merely

```text
upper action -> lower action.
```

It is a pointed state-bearing projection

```text
(A_up,S_up,L_up,mu_up,omega_up,H_up)
                  |
                  v
(A_low,Gamma,omega_low,H_low),                        (7.1)
```

with commuting action, measure/cycle, state and anchor maps. Equation (2.6)
is the infinitesimal test for (7.1). Equation (1.3) is its scalar radial
anchor row.

This is the exact sense in which upper-world constraints can protect a lower
fixed point. The constraint must act on the quantum state and integration
data, not only on the classical action or its Hessian.

## 8. Exact scientific boundary

Closed here:

- the differentiated action/measure/cycle pushforward identity;
- the pointwise, BV-exact, centered-involution and state-anchor routes to QJ1;
- formal compatibility of QJ1 with the anomaly-free q79 local QME;
- exact proof that gauge QME does not uniquely select a radial tadpole;
- the complete QJ1 affine counterterm orbit;
- the exact nonzero T35 tadpole at the T34 point;
- the unique bare tadpole-zero scale as an unselected scheme coordinate; and
- reduction of physical QJ1 to one same-source state-anchor equality or one
  explicit radial Ward primitive.

Still open:

- one selected interacting q79 state or global cosmological state;
- proof that its zero-source radial expectation equals `H_T34`;
- an explicit `Psi_H` making the radial insertion quantum-BV exact;
- a selected physical integration cycle, measure and determinant line;
- QJ2 kinetic normalization and Hessian intertwining;
- QJ0 gravitational vacuum normalization;
- complete RG, loop, pole and observable transport; and
- the full exits of `B.ACTION.01` and `B.QFT.02`.

Accordingly, formal QJ1 compatibility is closed but physical QJ1 selection is
not. Physical acceptance remains

```text
packets: 0/3,
rows:    0/7.
```

## 9. Primary external context

Finite BV integration and QME-preserving pushforward provide the natural
setting for (2.6) and (3.2), but do not select an arbitrary radial
normalization:

- A. Cattaneo, P. Mnev and N. Reshetikhin,
  [Perturbative Quantum Gauge Theories on Manifolds with Boundary](https://arxiv.org/abs/1507.01221).
- K. Costello,
  [Renormalisation and the Batalin-Vilkovisky Formalism](https://arxiv.org/abs/0706.1533).

The Legendre-transform relation used in (3.4)-(3.5) is a standard effective-
action identity; a combinatorial rigorous formulation is given by:

- D. Jackson, A. Kempf and A. Morales,
  [A robust generalization of the Legendre transform for QFT](https://arxiv.org/abs/1612.00462).

Gauge-parameter dependence is controlled by Nielsen identities, which do not
select the vacuum state or finite radial normalization:

- O. Del Cima, D. Franco and O. Piguet,
  [Gauge Independence of the Effective Potential Revisited](https://arxiv.org/abs/hep-th/9902084).

Finally, local covariance does not generically provide one preferred state on
every spacetime. The current q79 program must therefore supply a special
same-branch state theorem rather than appeal to generic naturality:

- C. Fewster and R. Verch,
  [Algebraic quantum field theory in curved spacetimes](https://arxiv.org/abs/1504.00586).

These references support the general mathematical boundary only. They do not
prove the q79 state anchor or any MTT physical value.

## 10. Reproduction

```powershell
python build_quantum_radial_anchor_tadpole.py
python verify_quantum_radial_anchor_tadpole.py
python -m unittest tests.test_quantum_radial_anchor_tadpole -v
python verify.py
```

The generated packet is `quantum_radial_anchor_tadpole.packet.json`.
