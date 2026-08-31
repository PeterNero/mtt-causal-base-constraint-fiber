# Common Action-Quantum Torsor and One-Primitive BV Normalization Theorem v1

**Claim:** CBF.T49

**Date:** 2026-08-31

**Status:** exact recovery of the suppressed radial action coefficient, exact
one-dimensional common bosonic action-amplitude torsor, and exact direct
local-formal tree-plus-one-loop normalization relative to one shared action
quantum; the value of that primitive, the physical q79 cyclic real slice and
pairing, the full upper action, determinant holonomy, fixed-coupling continuum
and top-level physical endpoint remain open

## 1. Result

CBF.T48 retained a positive scalar coefficient named `A_H`. Read in isolation,
that notation makes the scalar normalization look independent of the gauge
normalization and of the perturbative BV action quantum. It is not independent
at the T32 product-spectral-action tier.

T32 starts from

```text
S_scalar
 =f0/(8 pi^2) integral Tr[
    (partial Phi)^2+Phi^4-4(f2 Lambda^2/f0)Phi^2
  ],
```

and computes a common trace multiplicity `32`. Therefore the coefficient
suppressed in the normalized T34/T48 radial formulas is exactly

```text
A_H=32 f0/(8 pi^2)=4 f0/pi^2.                       (1.1)
```

The A52/A88 gauge convention is

```text
g_i^(-2)=c_g K_i,
c_g=6f0.                                             (1.2)
```

Consequently

```text
A_H/g_i^(-2)=2/(3 pi^2 K_i),                         (1.3)
```

and every scalar-to-gauge relative normalization is independent of `f0` once
the positive overlap shape `K` is fixed. The logarithmic amplitude Jacobian
with respect to `log f0` is

```text
d(log A_H,log g_1^-2,log g_2^-2,log g_3^-2)/d log f0
 =(1,1,1,1)^T,                                      (1.4)
```

which has rank one. There is one common positive amplitude, not one scalar
amplitude plus one gauge amplitude.

Let

```text
alpha=f0/hbar.                                       (1.5)
```

At the direct radial tree-plus-one-loop tier, the dimensionless effective
action `Gamma/hbar` is fixed relative to `alpha`. Its tree coefficient is
`4alpha/pi^2`; T43's selected Weyl loop coefficient is `1/(2pi^2)`. Their
overall coefficient ratio is exactly

```text
one-loop/tree=1/(8alpha).                            (1.6)
```

T39's pointed subtraction adds no free coefficient. It is unique at every
formal order after its value, tadpole and Hessian conditions are imposed.
Thus the direct radial local-formal action has one shared action-quantum
primitive and no additional radial, loop or local-formal BV-scheme
normalization knob. The unidentified physical q79 cyclic multiplier is a
separate gluing obligation retained in Section 7.

This is not a zero-primitive theorem. A88 and A89 prove that normalized
filters, Born probabilities, circle holonomy, instanton charge and theta
periodicity do not select the positive coefficient. At fixed `hbar`, changing
`f0` changes canonically normalized interaction vertices and the loop/tree
ratio. The remaining primitive is physically meaningful.

## 2. Exact coefficient recovery

On the fixed-source branch put

```text
Phi(x)=h(x)D_phys(t_*).
```

T32 gives

```text
Tr D_phys(t_*)^2=32q2_*,
Tr D_phys(t_*)^4=32q4_*.
```

After freezing `t=t_*`, its scalar action is therefore

```text
S_rad
 =4f0/pi^2 integral [
    q2_* (partial h)^2
    +q4_* h^4
    -4c_H q2_* h^2
  ],                                                 (2.1)
```

where

```text
c_H=(f2/f0)Lambda^2.                                 (2.2)
```

Comparing (2.1) with T48's notation proves (1.1). No new convention or
observed value is involved.

Two different quantities were previously both denoted informally by `c` in
different research lines. T49 separates them permanently:

```text
c_H=(f2/f0)Lambda^2       radial mass-squared scale,
c_g=6f0                   common gauge action amplitude. (2.3)
```

They have different types and dimensions. T49 never equates them.

## 3. Common scalar-gauge normalization

For fixed positive gauge-overlap shape `K=diag(K_1,K_2,K_3)`, A52/A88 give

```text
g_i^-2=6f0 K_i.                                      (3.1)
```

Equations (1.1) and (3.1) imply

```text
g_i^-2/g_j^-2=K_i/K_j,
A_H/(6f0 K_i)=2/(3pi^2K_i).                          (3.2)
```

Under the positive action

```text
f0 -> a f0,
A_H -> a A_H,
g_i^-2 -> a g_i^-2,
g_i -> a^(-1/2)g_i,          a>0,                   (3.3)
```

all ratios in (3.2) remain fixed. The orbit direction is one-dimensional.
The A88 rank-one gauge result therefore extends to the scalar coefficient
without adding a second direction.

The A52 numerical value of `f0` is an accepted profile coordinate inferred
from measured gauge normalization. It is useful as a diagnostic but is not a
strict MTT source. At that profile point,

```text
f0=0.39740822592486424,
A_H=0.16106348735963533,
c_g=2.3844493555491857,                              (3.4)
```

and `A_H/c_g=2/(3pi^2)` to floating precision. No number in (3.4) is used to
prove (1.1)-(3.3).

## 4. Dimensionless action quantum

The path-integral weight depends on `S/hbar`, not on `S` and `hbar`
separately. Define `alpha` by (1.5). The radial tree action becomes

```text
I_tree:=S_rad/hbar
 =4alpha/pi^2 integral [
    q2_* (partial h)^2
    +q4_* h^4
    -4c_H q2_* h^2
  ].                                                 (4.1)
```

T43 writes the one-loop term in `hbar=1` units. Restoring loop order gives

```text
Gamma=S_rad+hbar Gamma_1+O(hbar^2),
Gamma_1,rad
 =integral q4_*H_*^4/(2pi^2) rho(h/H_*),             (4.2)
```

where

```text
rho(x)=x^4(3/2-log x^2)-2x^2+1/2.                   (4.3)
```

Dividing (4.2) by `hbar` and comparing with (4.1) proves (1.6). The selected
dimensionless direct radial action through one loop is therefore

```text
Gamma_rad/hbar
 =4alpha/pi^2 integral P_*(h)
  +integral q4_*H_*^4/(2pi^2)rho(h/H_*)
  +higher formal orders.                             (4.4)
```

Here `P_*` includes the kinetic term in the first integral as displayed in
(4.1). Equation (4.4) is a local-formal expression, not a fixed-coupling
convergent functional integral.

## 5. Why the remaining primitive is physical

Put `h=H_*+eta` and use T48's canonical field

```text
phi=sqrt(2A_H q2_*) eta.                             (5.1)
```

The tree mass is the generalized Hessian eigenvalue

```text
m_h^2=8c_H,                                          (5.2)
```

so the common `A_H` cancels. This explains why T48 could select a free radial
state without selecting `f0`.

The interactions do not have that cancellation. For the convention in which
`g3` and `g4` are the third and fourth derivatives of the canonical tree
potential at `phi=0`, exact differentiation gives

```text
g3_tree
 =6sqrt(2) q4_* H_*/(sqrt(A_H) q2_*^(3/2))
 =3sqrt(2)pi q4_* H_*/(sqrt(f0) q2_*^(3/2)),

g4_tree
 =6q4_*/(A_H q2_*^2)
 =3pi^2 q4_*/(2f0 q2_*^2).                          (5.3)
```

Thus

```text
g3_tree scales as f0^(-1/2),
g4_tree scales as f0^(-1).                           (5.4)
```

At fixed `hbar`, the positive orbit (3.3) changes interaction strengths and
the ratio (1.6). It is not merely a field-coordinate convention.

## 6. Pointed renormalization adds no primitive

T43 derives the raw Weyl determinant and then applies the unique T39
two-jet retraction at `H_*`. The resulting loop term satisfies

```text
rho(1)=rho'(1)=rho''(1)=0,                           (6.1)
```

while

```text
(rho'''(1),rho''''(1),rho'''''(1))=(-16,-64,-48).   (6.2)
```

For every fixed `alpha>0`, T39's three anchor equations determine all three
allowed even local counterterm coefficients. Its exact ledger is

```text
finite anchor conditions:            3,
free coefficients after anchoring:   0.              (6.3)
```

Therefore (4.4) contains no second radial normalization parameter. The
higher vertices in (6.2) remain genuine quantum interactions.

The statement “T39 adds no primitive” is different from “upper MTT selects
T39.” The latter still needs one physical upper action/projection theorem.

## 7. BV and QME scale separation

There are two distinct scale operations.

First, a simultaneous change of action units

```text
S -> aS,
hbar -> a hbar                                      (7.1)
```

leaves `S/hbar` and `alpha` fixed. With a fixed BV bracket, both terms in

```text
1/2(S,S)-i hbar Delta S=0                            (7.2)
```

scale by `a^2`. Equation (7.1) is a unit convention.

Second, changing `f0` at fixed `hbar` changes `alpha`. That is the physical
one-dimensional orbit detected in Sections 3-5. QME, ordinary Ward identities
and normalized state conditions are homogeneous along this orbit and do not
select one point. T40 gives an explicit nonselection theorem of this type.

H4-T14 supplies a canonical algebraic cotangent pairing and cyclic action
coefficient one. It explicitly leaves the physical trace normalization and
real slice open. T49 therefore uses H4-T14 only as a compatibility statement:
if the q79 cotangent action is proved to push forward to the direct action,
its physical multiplier must represent the same `alpha`; it cannot be counted
as an additional free normalization after that gluing equation is certified.
T49 does not assert that the gluing equation already exists.

T39 supplies a formal QME-compatible anchored scheme and T46 supplies formal
state pullback and a canonical BRST lift from the complete T48 seed. These
constructions introduce no continuous normalization selector. The finite-shell
q79 theorem similarly preserves the free QME up to its determinant-line
scalar. None of these formal or normalized statements selects `alpha` or the
relative determinant holonomy.

## 8. One-shared-primitive closure standard

A89 records the adopted gauge standard

```text
two relative gauge coordinates plus one shared positive anchor. (8.1)
```

T49 proves that the scalar coefficient and direct radial loop expansion do
not require another anchor. At this adopted tier the ledger is

```text
shared positive action primitives before scalar/BV consolidation: 1,
shared positive action primitives after consolidation:            1,
new primitive introduced by T49:                                  0,
strict MTT source value for alpha:                                 open. (8.2)
```

Given `alpha`, equations (1.1)-(7.2) fix the complete direct radial
tree-plus-one-loop normalization and the T39 anchored local-formal scheme.
This is a legitimate one-primitive closure. It is not a no-knob prediction.

The rejected A89 level-120 near-hit is not revived. Chern-Weil integrality
selects instanton number, not the CP-even coefficient. The shared circle can
carry phase and holonomy data, but phase periodicity does not quantize the
positive kinetic amplitude.

## 9. Gate ledger after T49

The action frontier now separates as

```text
direct scalar coefficient A_H/f0:             closed exactly,
direct scalar/gauge relative normalization:   closed exactly,
number of common positive amplitudes:         exactly one,
direct radial one-loop coefficient:           closed by T43,
T39 finite radial coefficients given alpha:   closed, zero free,
complete free seed and formal lift:            closed by T48/T46,
adopted one-shared-primitive normalization:    closed conditionally,
strict source selection of alpha:              open,
physical q79 cyclic pairing and real slice:    open,
same-upper full interaction/BV map:            open,
determinant-line relative holonomy:            open,
fixed-coupling regulator-independent limit:   open,
top-level B.ACTION.01 and G2:                  open. (9.1)
```

The direct radial part of the normalization problem is therefore no longer
an unspecified collection of constants. The remaining physical action
normalization is one typed scalar `alpha`, plus structural existence of the
q79 action/projection bridge.

Physical endpoint acceptance does not move:

```text
physical gates:   0/3,
physical packets: 0/3,
physical rows:    0/7.                              (9.2)
```

## 10. Exact scientific boundary

T49 proves:

- `A_H=4f0/pi^2` from the hash-locked T32 action and trace;
- exact scalar-to-gauge ratios and rank-one common-amplitude Jacobian;
- exact distinction between the radial scale `c_H` and gauge amplitude `c_g`;
- the dimensionless direct radial tree-plus-one-loop action relative to
  `alpha=f0/hbar`;
- exact loop/tree prefactor ratio `1/(8alpha)`;
- invariance of the free generalized mass under the common amplitude;
- non-invariance of canonical cubic and quartic interactions;
- zero additional T39 radial counterterm freedom after anchoring;
- extension of the adopted one-shared-primitive standard to the direct
  scalar and local-formal radial BV normalization ledger; and
- an exact no-go against selecting `alpha` from topology, normalized
  probability, Ward/QME identities or shared-circle phase alone.

T49 does not prove:

- a source-derived numerical value of `f0`, `hbar`, `alpha` or a gauge coupling;
- that A52's measured profile coordinate is a no-knob MTT prediction;
- a physical q79 HYM cyclic pairing, trace density or real slice;
- equality of H4-T14's cotangent action with the accepted physical BV action;
- the full bosonic, fermionic and gravitational upper action from one source;
- determinant-line connection or relative holonomy;
- a fixed-coupling interacting C-star continuum;
- RG/pole/uncertainty transport or held-out observable prediction; or
- closure of `B.ACTION.01`, `B.QFT.02`, physical `G1` or top-level `G2`.

The next honest action target is no longer “find the scalar normalization.”
It is to construct the physical q79 cyclic real slice and pairing and prove
that its action pushforward lands on the one-primitive direct normalization
class established here.

## 11. Reproduction

```text
python build_common_action_quantum_torsor.py
python verify_common_action_quantum_torsor.py
python -m unittest tests.test_common_action_quantum_torsor -v
```

The machine-readable result is
`common_action_quantum_torsor.packet.json`.
